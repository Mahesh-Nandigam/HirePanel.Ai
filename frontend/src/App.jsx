import { useState, useRef, useEffect } from 'react'
import IsoLevelWarp from '@/components/ui/isometric-wave-grid-background'

function App() {
  const [step, setStep] = useState(0);

  // Sync hash -> step on mount and hashchange
  useEffect(() => {
    const syncHashToStep = () => {
      const hash = window.location.hash;
      if (hash === '#/jd') setStep(1);
      else if (hash === '#/upload') setStep(2);
      else if (hash === '#/intake') setStep(3);
      else if (hash === '#/vetting') setStep(4);
      else setStep(0);
    };

    window.addEventListener('hashchange', syncHashToStep);
    syncHashToStep();

    return () => window.removeEventListener('hashchange', syncHashToStep);
  }, []);

  // Helper to change step and push to hash history
  const changeStep = (newStep) => {
    setStep(newStep);
    const hashes = { 0: '', 1: '#/jd', 2: '#/upload', 3: '#/intake', 4: '#/vetting' };
    window.location.hash = hashes[newStep] || '';
  };
  const [jobDescription, setJobDescription] = useState('');
  const [resumes, setResumes] = useState([]);
  const [intakeData, setIntakeData] = useState([]);
  const [isProcessingIntake, setIsProcessingIntake] = useState(false);
  const fileInputRef = useRef(null);

  // Vetting states
  const [vettingResults, setVettingResults] = useState([]);
  const [isVetting, setIsVetting] = useState(false);
  const [activeDrawerCandidate, setActiveDrawerCandidate] = useState(null);
  const leaderboardRef = useRef(null);

  const handleNextToUpload = () => {
    if (jobDescription.trim().length < 50) {
      alert("Please paste a comprehensive Job Description (at least 50 characters).");
      return;
    }
    changeStep(2);
  };

  const handleNextToIntake = async () => {
    if (resumes.length === 0) {
      alert("Please upload at least one resume PDF.");
      return;
    }
    changeStep(3);
    setIsProcessingIntake(true);
    
    const results = [];
    for (const file of resumes) {
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await fetch('http://localhost:8001/api/intake', {
          method: 'POST',
          body: formData
        });
        if (response.ok) {
          const data = await response.json();
          results.push({ ...data, file_reference: file });
        } else {
          results.push({ candidate_name: "Error", github_url: "Error", linkedin_url: "Error", resume_filename: file.name, file_reference: file });
        }
      } catch (e) {
        results.push({ candidate_name: "Network Error", github_url: "Error", linkedin_url: "Error", resume_filename: file.name, file_reference: file });
      }
    }
    
    setIntakeData(results);
    setIsProcessingIntake(false);
  };

  const handleStartVetting = async () => {
    changeStep(4);
    setIsVetting(true);
    
    // Initialize vetting results for all candidates as Evaluating immediately
    const initialVetting = intakeData.map((c) => ({
      filename: c.resume_filename,
      name: c.candidate_name,
      status: 'Evaluating',
      progress: 10,
      activeAgent: 'Intake',
      liveMessage: 'Intake Agent: Extracting candidate identifiers and details...',
      completed: false,
      payload: null
    }));
    setVettingResults(initialVetting);

    const evaluateCandidate = async (candidate, index) => {
      const formData = new FormData();
      formData.append('file', candidate.file_reference);
      formData.append('job_description', jobDescription);

      const updateProgress = (progress, agent, msg) => {
        setVettingResults(prev => prev.map((item, idx) => {
          if (idx === index) {
            return { ...item, progress, activeAgent: agent, liveMessage: msg };
          }
          return item;
        }));
      };

      // Progress bar animations simulating pipeline flow stages
      const t1 = setTimeout(() => updateProgress(30, 'GitHub', 'GitHub Agent: Scanning commit activity, repository complexity and GSoC contributions...'), 1200);
      const t2 = setTimeout(() => updateProgress(50, 'LinkedIn', 'LinkedIn Agent: Vetting job tenure, career path transitions, and stability...'), 3500);
      const t3 = setTimeout(() => updateProgress(70, 'Resume', 'Resume Agent: Parsing tech stack depth and architectural experience...'), 6000);
      const t4 = setTimeout(() => updateProgress(85, 'Debate', 'Tech Lead & HR Agent: Engaging in alignment debate panel...'), 8500);
      const t5 = setTimeout(() => updateProgress(95, 'Decider', 'Decider Agent: Synthesizing score weights and establishing final fit...'), 11000);

      try {
        const response = await fetch('http://localhost:8001/api/evaluate', {
          method: 'POST',
          body: formData
        });
        
        clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(t4); clearTimeout(t5);

        if (response.ok) {
          const payload = await response.json();
          setVettingResults(prev => prev.map((item, idx) => {
            if (idx === index) {
              return {
                ...item,
                status: payload.status,
                progress: 100,
                activeAgent: 'Finished',
                liveMessage: 'Consensus Fit Established.',
                completed: true,
                payload: payload
              };
            }
            return item;
          }));
        } else {
          setVettingResults(prev => prev.map((item, idx) => {
            if (idx === index) {
              return { ...item, status: 'ERROR', progress: 100, activeAgent: 'Failed', liveMessage: 'Evaluation failed (check API limits).' };
            }
            return item;
          }));
        }
      } catch (e) {
        clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(t4); clearTimeout(t5);
        setVettingResults(prev => prev.map((item, idx) => {
          if (idx === index) {
            return { ...item, status: 'ERROR', progress: 100, activeAgent: 'Failed', liveMessage: 'Network error connecting to backend.' };
          }
          return item;
        }));
      }
    };

    // Process all candidates in parallel concurrently
    const promises = intakeData.map((candidate, idx) => evaluateCandidate(candidate, idx));
    await Promise.all(promises);
    setIsVetting(false);
  };

  // Scroll to leaderboard once vetting is completed
  useEffect(() => {
    if (vettingResults.length > 0 && vettingResults.every(r => r.completed || r.status === 'ERROR') && !isVetting) {
      setTimeout(() => {
        leaderboardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 1500);
    }
  }, [vettingResults, isVetting]);

  const sortedCandidates = [...vettingResults]
    .filter(c => c.payload)
    .sort((a, b) => b.payload.finalScore - a.payload.finalScore);

  const handleExportCSV = () => {
    if (sortedCandidates.length === 0) return;
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Rank,Candidate Name,Status,Fit Score,Resume Depth,GitHub Code,LinkedIn Stability,JD Fit Match,Manager Justification\n";
    sortedCandidates.forEach((c, index) => {
      const p = c.payload;
      const rank = index + 1;
      const name = `"${c.name}"`;
      const status = p.status;
      const score = Math.round(p.finalScore);
      const resume = p.resume;
      const github = p.github;
      const linkedin = p.linkedin;
      const jdMatch = p.jdMatch;
      let justification = p.messages?.find(m => m.agent === 'Decider')?.text || "Fit determined by consensus.";
      justification = `"${justification.replace(/"/g, '""')}"`;
      const row = `${rank},${name},${status},${score},${resume},${github},${linkedin},${jdMatch},${justification}`;
      csvContent += row + "\n";
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "hirepanel_evaluation.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getAgentColorClass = (agent) => {
    switch (agent) {
      case 'Intake': return 'text-sky-400 border-sky-500/30';
      case 'GitHub': return 'text-blue-400 border-blue-500/30';
      case 'LinkedIn': return 'text-indigo-400 border-indigo-500/30';
      case 'Resume': return 'text-amber-400 border-amber-500/30';
      case 'Debate': return 'text-purple-400 border-purple-500/30';
      case 'Decider': return 'text-emerald-400 border-emerald-500/30';
      default: return 'text-slate-400 border-slate-500/30';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'HIRE': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'WAITLIST': return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'REJECT': return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      default: return 'text-slate-400 bg-slate-500/10 border-slate-500/30';
    }
  };

  function handleFileChange(e) {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
      setResumes(prev => [...prev, ...newFiles]);
    }
  }

  function removeFile(indexToRemove) {
    setResumes(prev => prev.filter((_, index) => index !== indexToRemove));
  }

  if (step === 0) {
    return (
      <div className="relative w-full h-screen overflow-hidden font-sans">
        {/* BACKGROUND: The New Trend */}
        <IsoLevelWarp 
          color="100, 50, 250" 
          density={50} 
          speed={1.5}
        />

        {/* CONTENT LAYER */}
        <div className="relative z-10 flex flex-col items-center justify-center h-full px-4 text-center">
          {/* Glowing Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-300 text-sm font-medium mb-8 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
            Autonomous AI Hiring Committee
          </div>
          
          {/* Hero Text */}
          <h1 className="text-6xl md:text-8xl font-black tracking-tight text-white mb-4 drop-shadow-2xl">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-200 to-purple-400">
              HirePanel AI
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-slate-300 font-medium max-w-lg mb-10 tracking-wide">
            Hire In Minutes
          </p>

          <button 
            onClick={() => changeStep(1)}
            className="group relative inline-flex items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold text-lg py-4 px-10 rounded-2xl shadow-xl transition-all duration-300 transform hover:scale-105 active:scale-95 hover:shadow-primary/20 hover:shadow-2xl cursor-pointer"
          >
            <span className="relative z-10 flex items-center gap-2">
              Build Your Dream Team
              <span className="transition-transform group-hover:translate-x-1">→</span>
            </span>
            <div className="absolute inset-0 rounded-2xl bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity animate-pulse" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-5xl relative min-h-screen">
      <header className="text-center mb-12 relative">
        <h1 className="text-5xl font-extrabold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
          HirePanel.ai
        </h1>
        <p className="text-slate-400 text-lg">Autonomous AI Hiring Committee • Live Evaluation System</p>
      </header>

      {/* STAGE 1: JD Input */}
      {step === 1 && (
        <div className="glass-panel p-8 animate-slide-up transition-all">
          <h2 className="text-2xl font-bold mb-2">Step 1: The Job Description</h2>
          <p className="text-slate-400 mb-6">Paste the full job description below. Our JD Agent will use this to strictly evaluate candidate alignment.</p>
          
          <textarea
            className="w-full h-64 bg-black/40 border border-white/10 rounded-xl p-4 text-slate-200 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors resize-none mb-6"
            placeholder="e.g., We are looking for a Senior Python Engineer with 5+ years of experience in FastAPI, React, and system architecture..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
          
          <div className="flex justify-end">
            <button 
              onClick={handleNextToUpload}
              className="bg-primary hover:bg-blue-600 text-white font-semibold py-3 px-8 rounded-xl transition-transform hover:scale-105 active:scale-95"
            >
              Next: Upload Resumes →
            </button>
          </div>
        </div>
      )}

      {/* STAGE 2: Resume Upload */}
      {step === 2 && (
        <div className="glass-panel p-8 animate-slide-up">
          <h2 className="text-2xl font-bold mb-2">Step 2: Candidate Resumes</h2>
          <p className="text-slate-400 mb-6">Upload PDF resumes for the batch you want to evaluate (specifically 3 candidates).</p>
          
          <div 
            className="border-2 border-dashed border-primary/50 hover:border-primary bg-black/30 hover:bg-primary/5 rounded-xl p-12 text-center transition-all cursor-pointer mb-6"
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              multiple 
              accept=".pdf" 
              ref={fileInputRef} 
              className="hidden" 
              onChange={handleFileChange}
            />
            <div className="text-4xl mb-4">📄</div>
            <p className="text-lg font-semibold text-slate-200">Click to Select PDFs</p>
            <p className="text-sm text-slate-500 mt-2">Only PDF format is supported</p>
          </div>

          {resumes.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Selected Candidates ({resumes.length})</h3>
              <div className="flex flex-col gap-2">
                {resumes.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between bg-white/5 border border-white/10 rounded-lg p-3">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">📄</span>
                      <span className="text-slate-200">{file.name}</span>
                    </div>
                    <button 
                      onClick={() => removeFile(idx)}
                      className="text-slate-500 hover:text-danger px-2 transition-colors"
                      title="Remove"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-between items-center mt-8">
            <button 
              onClick={() => changeStep(1)}
              className="text-slate-400 hover:text-white underline transition-colors"
            >
              ← Back to JD
            </button>
            <button 
              onClick={handleNextToIntake}
              className="bg-primary hover:bg-blue-600 text-white font-semibold py-3 px-8 rounded-xl transition-transform hover:scale-105 active:scale-95"
            >
              Next: Data Intake →
            </button>
          </div>
        </div>
      )}

      {/* STAGE 3: Intake Table */}
      {step === 3 && (
        <div className="glass-panel p-8 animate-slide-up">
          <h2 className="text-2xl font-bold mb-2">Step 3: Intake Analysis</h2>
          <p className="text-slate-400 mb-6">Our Intake Agent is parsing the PDFs to extract names and URLs.</p>
          
          <div className="overflow-x-auto bg-black/30 rounded-xl border border-white/10 mb-6">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-white/5 text-slate-400 uppercase font-semibold">
                <tr>
                  <th className="px-4 py-3">Filename</th>
                  <th className="px-4 py-3">Extracted Name</th>
                  <th className="px-4 py-3">GitHub</th>
                  <th className="px-4 py-3">LinkedIn</th>
                </tr>
              </thead>
              <tbody>
                {isProcessingIntake && intakeData.length === 0 && (
                  <tr>
                    <td colSpan="4" className="px-4 py-8 text-center text-primary animate-pulse">
                      Analyzing uploaded resumes...
                    </td>
                  </tr>
                )}
                {intakeData.map((data, idx) => (
                  <tr key={idx} className="border-t border-white/5 hover:bg-white/5 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-200">{data.resume_filename}</td>
                    <td className="px-4 py-3">{data.candidate_name}</td>
                    <td className="px-4 py-3">
                      {data.github_url !== "No" && !data.github_url.includes("Error") ? (
                        <a href={data.github_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">Link</a>
                      ) : <span className="text-slate-500">None</span>}
                    </td>
                    <td className="px-4 py-3">
                      {data.linkedin_url !== "No" && !data.linkedin_url.includes("Error") ? (
                        <a href={data.linkedin_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">Link</a>
                      ) : <span className="text-slate-500">None</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-between items-center mt-8">
            <button 
              onClick={() => { changeStep(2); setIntakeData([]); }}
              className="text-slate-400 hover:text-white underline transition-colors"
            >
              ← Back to Upload
            </button>
            <button 
              onClick={handleStartVetting}
              disabled={isProcessingIntake}
              className={`font-semibold py-3 px-8 rounded-xl transition-all ${isProcessingIntake ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 'bg-success hover:bg-emerald-600 text-white hover:scale-105 active:scale-95'}`}
            >
              {isProcessingIntake ? 'Processing...' : 'Stage 4: Start Vetting'}
            </button>
          </div>
        </div>
      )}

      {/* STAGE 4: Vetting Grid */}
      {step === 4 && (
        <div className="animate-slide-up flex flex-col gap-12">
          <div>
            <h2 className="text-3xl font-bold mb-2">Step 4: AI Committee Vetting</h2>
            <p className="text-slate-400 mb-8">
              {isVetting 
                ? "The hiring committee agents are running parallel evaluations. This takes around 15 seconds..." 
                : "Vetting complete! You can click to view the full agent debate transcript for any candidate below."}
            </p>

            {/* Vetting Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {vettingResults.map((candidate, idx) => {
                const isFlipped = candidate.completed;
                const payload = candidate.payload;
                
                return (
                  <div key={idx} className={`card-container ${isFlipped ? 'flipped' : ''}`}>
                    <div className="card-inner">
                      
                      {/* FRONT OF CARD: Evaluating State */}
                      <div className="card-front border-primary/20 bg-slate-900/50">
                        <div className="flex justify-between items-start w-full">
                          <span className={`text-xs px-2.5 py-1 rounded-full border uppercase tracking-wider font-semibold ${
                            candidate.status === 'Queued'
                              ? 'bg-slate-800/40 text-slate-500 border-slate-700/30'
                              : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                          }`}>
                            {candidate.status === 'Queued' ? 'Queued' : `${candidate.activeAgent} Running`}
                          </span>
                          <span className="text-slate-500 text-xs truncate max-w-[130px]" title={candidate.filename}>
                            {candidate.filename}
                          </span>
                        </div>

                        {/* Animated pulsing glow logo */}
                        <div className="my-auto flex flex-col items-center">
                          <div className={`w-20 h-20 rounded-full border flex items-center justify-center mb-4 ${
                            candidate.status === 'Queued'
                              ? 'border-slate-800 bg-slate-950/20'
                              : 'border-blue-500/20 bg-blue-500/5 pulse-glow'
                          }`}>
                            <span className="text-3xl">{candidate.status === 'Queued' ? '⏳' : '🤖'}</span>
                          </div>
                          <h3 className="font-bold text-lg text-slate-200">{candidate.name}</h3>
                          <p className="text-xs text-slate-500 mt-1">
                            {candidate.status === 'Queued' ? 'Waiting in queue...' : 'Evaluating candidate profile...'}
                          </p>
                        </div>

                        <div className="w-full">
                          {/* Progress bar */}
                          <div className="w-full bg-slate-800 rounded-full h-1.5 mb-2 overflow-hidden">
                            <div 
                              className={`h-1.5 rounded-full transition-all duration-1000 ${
                                candidate.status === 'Queued' ? 'bg-slate-700' : 'bg-primary'
                              }`} 
                              style={{ width: `${candidate.progress}%` }}
                            ></div>
                          </div>
                          <p className="text-slate-400 text-xs text-left line-clamp-2 h-8 leading-4">
                            {candidate.liveMessage}
                          </p>
                        </div>
                      </div>

                      {/* BACK OF CARD: Completed Evaluation */}
                      {payload && (
                        <div className="card-back border-white/10 bg-slate-955/90">
                          <div className="flex justify-between items-center w-full">
                            <span className={`text-[10px] px-2.5 py-0.5 rounded-full border font-bold uppercase ${getStatusColor(payload.status)}`}>
                              {payload.status}
                            </span>
                            <span className="text-xs text-slate-500 truncate max-w-[120px]">
                              {candidate.filename}
                            </span>
                          </div>

                          <div className="flex flex-col items-center my-3">
                            <div className="relative w-24 h-24 rounded-full border-4 border-slate-800 bg-slate-900/80 flex items-center justify-center shadow-inner">
                              <span className="text-3xl font-extrabold text-white">{Math.round(payload.finalScore)}</span>
                              <span className="text-[10px] text-slate-500 absolute bottom-3">FIT / 100</span>
                            </div>
                            <h3 className="font-bold text-lg text-slate-200 mt-2">{candidate.name}</h3>
                            <p className="text-xs text-slate-400">Vetting Score Matrix</p>
                          </div>

                          {/* Skill Matrix progress bars */}
                          <div className="flex flex-col gap-1.5 w-full text-left">
                            <div className="text-xs flex justify-between">
                              <span className="text-slate-400">Resume Depth</span>
                              <span className="text-slate-200 font-semibold">{payload.resume}/10</span>
                            </div>
                            <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden mb-1">
                              <div className="bg-amber-400 h-full" style={{ width: `${payload.resume * 10}%` }}></div>
                            </div>

                            <div className="text-xs flex justify-between">
                              <span className="text-slate-400">GitHub Code</span>
                              <span className="text-slate-200 font-semibold">{payload.github}/10</span>
                            </div>
                            <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden mb-1">
                              <div className="bg-blue-400 h-full" style={{ width: `${payload.github * 10}%` }}></div>
                            </div>

                            <div className="text-xs flex justify-between">
                              <span className="text-slate-400">LinkedIn Stability</span>
                              <span className="text-slate-200 font-semibold">{payload.linkedin}/10</span>
                            </div>
                            <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden mb-1">
                              <div className="bg-indigo-400 h-full" style={{ width: `${payload.linkedin * 10}%` }}></div>
                            </div>

                            <div className="text-xs flex justify-between">
                              <span className="text-slate-400">JD Fit Match</span>
                              <span className="text-slate-200 font-semibold">{payload.jdMatch}/10</span>
                            </div>
                            <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden mb-2">
                              <div className="bg-purple-400 h-full" style={{ width: `${payload.jdMatch * 10}%` }}></div>
                            </div>
                          </div>

                          <button 
                            onClick={() => setActiveDrawerCandidate(candidate)}
                            className="w-full bg-white/5 hover:bg-primary/20 border border-white/10 hover:border-primary/50 text-white font-medium py-2 rounded-xl text-xs transition-colors"
                          >
                            💬 View Agent Debate Logs
                          </button>
                        </div>
                      )}
                      
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* LEADERBOARD SECTION */}
          {sortedCandidates.length > 0 && (
            <div ref={leaderboardRef} className="glass-panel p-8 animate-slide-up border-white/10 mt-6 scroll-mt-6">
              <h2 className="text-3xl font-extrabold mb-2 text-slate-100 flex items-center gap-3">
                🏆 Candidate Alignment Leaderboard
              </h2>
              <p className="text-slate-400 mb-8">Candidates ranked based on overall fit matrix, technical depth, and JD alignment.</p>

              <div className="overflow-x-auto rounded-xl border border-white/10 bg-black/40">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-white/5 text-slate-400 uppercase font-semibold">
                    <tr>
                      <th className="px-6 py-4 text-center w-20">Rank</th>
                      <th className="px-6 py-4">Candidate Name</th>
                      <th className="px-6 py-4 text-center">Fit Score</th>
                      <th className="px-6 py-4 text-center">JD Match</th>
                      <th className="px-6 py-4">Manager Justification</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedCandidates.map((c, index) => {
                      const payload = c.payload;
                      const isTop = index === 0;
                      return (
                        <tr key={index} className={`border-t border-white/5 hover:bg-white/5 transition-colors ${isTop ? 'bg-amber-500/5' : ''}`}>
                          <td className="px-6 py-4 text-center">
                            <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                              index === 0 ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/25' :
                              index === 1 ? 'bg-slate-300 text-black' :
                              index === 2 ? 'bg-amber-700 text-white' : 'bg-slate-800 text-slate-400'
                            }`}>
                              {index + 1}
                            </span>
                          </td>
                          <td className="px-6 py-4 font-bold text-slate-200">
                            {c.name} {index === 0 && '👑'}
                          </td>
                          <td className="px-6 py-4 text-center font-extrabold text-primary text-base">
                            {Math.round(payload.finalScore)}
                          </td>
                          <td className="px-6 py-4 text-center font-semibold">
                            {payload.jdMatch}/10
                          </td>
                          <td className="px-6 py-4 text-slate-400 text-xs max-w-md leading-relaxed">
                            {payload.messages?.find(m => m.agent === 'Decider')?.text || "Fit determined by consensus."}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              <div className="flex justify-end gap-4 mt-8">
                <button 
                  onClick={handleExportCSV}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 px-6 rounded-xl transition-transform hover:scale-105 active:scale-95 text-sm flex items-center gap-2 shadow-lg"
                >
                  <span>📊</span> Export to CSV
                </button>
                <button 
                  onClick={() => { changeStep(1); setIntakeData([]); setVettingResults([]); }}
                  className="text-slate-400 hover:text-white underline transition-colors text-sm py-2 px-4"
                >
                  Start New Job Evaluation
                </button>
              </div>
            </div>
          )}

        </div>
      )}

      {/* SLIDING CHAT DRAWER */}
      {activeDrawerCandidate && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-fade-in">
          {/* Backdrop Click */}
          <div className="flex-grow" onClick={() => setActiveDrawerCandidate(null)}></div>
          
          {/* Drawer content */}
          <div className="w-full max-w-xl h-full bg-slate-900 border-l border-white/10 flex flex-col shadow-2xl relative animate-slide-left">
            {/* Header */}
            <div className="p-6 border-b border-white/10 flex justify-between items-center bg-slate-955">
              <div>
                <h3 className="text-xl font-bold text-slate-200">Agent Vetting Transcript</h3>
                <p className="text-xs text-slate-400">Candidate: {activeDrawerCandidate.name}</p>
              </div>
              <button 
                onClick={() => setActiveDrawerCandidate(null)}
                className="text-slate-400 hover:text-white text-xl p-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Chat Messages Log */}
            <div className="flex-grow overflow-y-auto p-6 flex flex-col gap-4 bg-slate-900/30">
              {activeDrawerCandidate.payload?.messages?.map((msg, idx) => (
                <div key={idx} className="bg-slate-955/40 border border-white/5 rounded-xl p-4 flex flex-col gap-1.5 shadow-sm">
                  <div className="flex justify-between items-center">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-lg border ${getAgentColorClass(msg.agent)}`}>
                      [{msg.agent} Agent]
                    </span>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
                    {msg.text}
                  </p>
                </div>
              ))}
            </div>
            
            {/* Footer */}
            <div className="p-4 border-t border-white/10 text-center bg-slate-950 text-xs text-slate-500">
              HirePanel.ai Committee transcripts are mathematically consistent with Groq consensus evaluations.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App
