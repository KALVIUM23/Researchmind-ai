"use client";

import React from "react";
import { Activity, Terminal, AlertCircle } from "lucide-react";

export default function LogsPage() {
  return (
    <main className="flex-1 flex overflow-hidden grid-bg-brutalist relative w-full h-full border-x border-[#232629]">
      <section className="w-full flex flex-col bg-[#111316]/95 backdrop-blur-sm z-10 relative shadow-2xl p-8">
        <header className="border-b border-[#232629] pb-6 mb-8 flex justify-between items-end">
          <div>
            <div className="font-jetbrains text-[10px] text-[#8e9192] mb-2">SYS_MOD: ACTIVITY_LOGS</div>
            <h1 className="font-libre text-3xl text-white tracking-tight uppercase flex items-center gap-3">
              <Activity className="h-6 w-6 text-[#E4F222]" />
              System Logs
            </h1>
          </div>
          <div className="flex gap-2">
            <button className="bg-[#1e2023] border border-[#232629] text-[#e2e2e6] font-jetbrains text-xs px-4 py-2 hover:border-white transition-colors">
              EXPORT LOGS
            </button>
            <button className="bg-[#E4F222] text-[#111316] font-jetbrains text-xs font-bold px-4 py-2 hover:brightness-110 transition-colors">
              CLEAR BUFFER
            </button>
          </div>
        </header>

        <div className="flex-1 bg-[#0c0e11] border border-[#232629] p-4 overflow-y-auto font-jetbrains text-[11px] leading-relaxed text-[#8e9192]">
          <div className="flex items-center gap-2 text-white mb-4 border-b border-[#232629] pb-2">
            <Terminal className="h-4 w-4" />
            <span>sys_out daemon active</span>
          </div>
          
          <div className="space-y-1">
            <p><span className="text-[#4edea3]">[2026-07-07 10:57:18]</span> [INFO] Initialized Gemini model: gemini-flash-latest, grounding: strict</p>
            <p><span className="text-[#4edea3]">[2026-07-07 10:57:18]</span> [INFO] Connected to Qdrant at :memory:, collection: researchmind</p>
            <p><span className="text-[#4edea3]">[2026-07-07 10:57:18]</span> [INFO] All services initialized</p>
            <p><span className="text-yellow-500">[2026-07-07 10:57:22]</span> [WARN] PyPDF2._reader - incorrect startxref pointer(1)</p>
            <p><span className="text-[#4edea3]">[2026-07-07 10:57:22]</span> [INFO] Document uploaded: a008770f-2a07-4eb7-bb09-efafb5f90ca2</p>
            <p><span className="text-[#4edea3]">[2026-07-07 11:50:51]</span> [INFO] Starting chunking process for sample.pdf</p>
            <p><span className="text-[#4edea3]">[2026-07-07 11:51:25]</span> [OK] Retrieved 2 filtered chunks, filters: {'{}'}</p>
          </div>
          
          <div className="mt-8 flex items-center gap-2 text-white opacity-50 animate-pulse">
            <span className="w-2 h-4 bg-white block"></span>
            Awaiting new events...
          </div>
        </div>
      </section>
    </main>
  );
}
