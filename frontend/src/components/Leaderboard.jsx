import React from 'react';

export default function Leaderboard({ 
  sortedCandidates, 
  leaderboardRef, 
  handleExportCSV, 
  changeStep, 
  setIntakeData, 
  setVettingResults, 
  vettingResults 
}) {
  if (sortedCandidates.length === 0) return null;
  
  return (
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

      {vettingResults.length > 0 && vettingResults.every(c => c.completed) && (
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
      )}
    </div>
  );
}
