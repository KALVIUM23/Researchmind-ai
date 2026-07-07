"use client";

import React from "react";
import { Database, Search, ArrowRight, Filter } from "lucide-react";

export default function ArchivesPage() {
  return (
    <main className="flex-1 flex overflow-hidden grid-bg-brutalist relative w-full h-full border-x border-[#232629]">
      <section className="w-full flex flex-col bg-[#111316]/95 backdrop-blur-sm z-10 relative shadow-2xl p-8">
        <header className="border-b border-[#232629] pb-6 mb-8 flex justify-between items-end">
          <div>
            <div className="font-jetbrains text-[10px] text-[#8e9192] mb-2">SYS_MOD: ARCHIVE_RETRIEVAL</div>
            <h1 className="font-libre text-3xl text-white tracking-tight uppercase flex items-center gap-3">
              <Database className="h-6 w-6 text-[#4edea3]" />
              Data Archives
            </h1>
          </div>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#8e9192]" />
              <input 
                type="text" 
                placeholder="Query archives..." 
                className="bg-[#1e2023] border border-[#232629] text-[#e2e2e6] font-jetbrains text-xs pl-9 pr-4 py-2 w-64 focus:outline-none focus:border-[#4edea3] transition-colors"
              />
            </div>
            <button className="border border-[#232629] text-[#e2e2e6] font-jetbrains px-3 py-2 hover:bg-[#333538]/50 transition-colors flex items-center gap-2">
              <Filter className="h-4 w-4" />
              FILTER
            </button>
          </div>
        </header>

        <div className="flex-1 flex flex-col items-center justify-center text-center opacity-60">
          <Database className="h-16 w-16 text-[#8e9192] mb-6" />
          <h2 className="font-jetbrains text-lg text-white mb-2">ARCHIVE INDEX EMPTY</h2>
          <p className="font-hanken text-sm text-[#8e9192] max-w-md">
            No historical documents or past synthesis runs found in the persistent storage volume. Upload documents in the Workspace to populate the archive.
          </p>
          <button className="mt-8 flex items-center gap-2 text-[#4edea3] font-jetbrains text-xs uppercase hover:underline">
            Initiate Data Sync <ArrowRight className="h-3 w-3" />
          </button>
        </div>
      </section>
    </main>
  );
}
