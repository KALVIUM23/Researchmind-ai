"use client";

import React from "react";
import { Settings, Save, Shield, Cpu, Network } from "lucide-react";

export default function SettingsPage() {
  return (
    <main className="flex-1 flex overflow-hidden grid-bg-brutalist relative w-full h-full border-x border-[#232629]">
      <section className="w-full flex flex-col bg-[#111316]/95 backdrop-blur-sm z-10 relative shadow-2xl p-8">
        <header className="border-b border-[#232629] pb-6 mb-8 flex justify-between items-end">
          <div>
            <div className="font-jetbrains text-[10px] text-[#8e9192] mb-2">SYS_MOD: CONFIGURATION</div>
            <h1 className="font-libre text-3xl text-white tracking-tight uppercase flex items-center gap-3">
              <Settings className="h-6 w-6 text-white" />
              Settings
            </h1>
          </div>
          <div className="flex gap-2">
            <button className="bg-white text-[#111316] font-jetbrains text-xs font-bold px-4 py-2 hover:bg-[#c7c6c7] transition-colors flex items-center gap-2">
              <Save className="h-4 w-4" />
              SAVE CONFIG
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto font-jetbrains text-sm max-w-3xl">
          
          <div className="mb-10 space-y-6">
            <div className="flex items-center gap-2 text-white border-b border-[#232629] pb-2">
              <Cpu className="h-4 w-4" />
              <h2 className="font-bold">LLM Engine</h2>
            </div>
            
            <div className="grid grid-cols-2 gap-8">
              <div className="space-y-2">
                <label className="text-[#8e9192] text-xs uppercase block">Primary Model</label>
                <select className="w-full bg-[#1e2023] border border-[#232629] text-white p-2 focus:outline-none focus:border-white">
                  <option>gemini-flash-latest</option>
                  <option>gemini-pro-vision</option>
                  <option>gpt-4o</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-[#8e9192] text-xs uppercase block">Grounding Level</label>
                <select className="w-full bg-[#1e2023] border border-[#232629] text-white p-2 focus:outline-none focus:border-white">
                  <option>Strict (Context Only)</option>
                  <option>Balanced</option>
                  <option>Lenient</option>
                </select>
              </div>
            </div>
          </div>

          <div className="mb-10 space-y-6">
            <div className="flex items-center gap-2 text-white border-b border-[#232629] pb-2">
              <Network className="h-4 w-4" />
              <h2 className="font-bold">Vector Database</h2>
            </div>
            
            <div className="space-y-4 text-[#e2e2e6]">
              <div className="flex items-center justify-between p-3 border border-[#232629] bg-[#1e2023]">
                <div>
                  <div className="font-bold">Qdrant Storage</div>
                  <div className="text-[#8e9192] text-xs mt-1">Currently using In-Memory ephemeral storage</div>
                </div>
                <button className="border border-[#232629] px-3 py-1 text-xs hover:border-white">Configure Persistence</button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex items-center gap-2 text-white border-b border-[#232629] pb-2">
              <Shield className="h-4 w-4" />
              <h2 className="font-bold">Security & API Keys</h2>
            </div>
            
            <div className="space-y-2">
              <label className="text-[#8e9192] text-xs uppercase block">Gemini API Key</label>
              <input 
                type="password" 
                value="••••••••••••••••••••••••••••••" 
                readOnly
                className="w-full bg-[#1e2023] border border-[#232629] text-white p-2 focus:outline-none focus:border-white opacity-50 cursor-not-allowed"
              />
              <p className="text-[10px] text-yellow-500 mt-1">Managed via environment variables (.env)</p>
            </div>
          </div>

        </div>
      </section>
    </main>
  );
}
