import React from 'react';

export default function CandidateDrawer({ candidate, onClose, getAgentColorClass }) {
  if (!candidate) return null;
  
  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-fade-in">
      {/* Backdrop Click */}
      <div className="flex-grow" onClick={onClose}></div>
      
      {/* Drawer content */}
      <div className="w-full max-w-xl h-full bg-slate-900 border-l border-white/10 flex flex-col shadow-2xl relative animate-slide-left">
        {/* Header */}
        <div className="p-6 border-b border-white/10 flex justify-between items-center bg-slate-955">
          <div>
            <h3 className="text-xl font-bold text-slate-200">Agent Vetting Transcript</h3>
            <p className="text-xs text-slate-400">Candidate: {candidate.name}</p>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white text-xl p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Chat Messages Log */}
        <div className="flex-grow overflow-y-auto p-6 flex flex-col gap-4 bg-slate-900/30">
          {candidate.payload?.messages?.map((msg, idx) => (
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
  );
}
