"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Fingerprint, Key, RefreshCw, ArrowRight, QrCode, Shield } from "lucide-react";

export default function AuthenticationTerminal() {
  const router = useRouter();
  const [operativeId, setOperativeId] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [isCalibrating, setIsCalibrating] = useState(true);

  React.useEffect(() => {
    const timer = setTimeout(() => setIsCalibrating(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (operativeId && accessToken) {
      // Navigate to the brutalist workspace
      router.push("/workspace");
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-geist bg-[#111316] text-[#e2e2e6] overflow-hidden relative">
      {/* CRT Overlay Effect */}
      <div className="fixed inset-0 crt-overlay mix-blend-overlay"></div>

      {/* Main Container */}
      <main className="flex-grow flex items-center justify-center p-6 relative z-10 grid-bg-brutalist">
        {/* Brutalist Registration Marks */}
        <div className="absolute top-8 left-8 w-4 h-4 border-t-2 border-l-2 border-[#232629]"></div>
        <div className="absolute top-8 right-8 w-4 h-4 border-t-2 border-r-2 border-[#232629]"></div>
        <div className="absolute bottom-16 left-8 w-4 h-4 border-b-2 border-l-2 border-[#232629]"></div>
        <div className="absolute bottom-16 right-8 w-4 h-4 border-b-2 border-r-2 border-[#232629]"></div>

        {/* Coordinate Stamps */}
        <div className="absolute top-8 left-14 font-jetbrains text-[10px] tracking-wider text-[#8e9192] uppercase">
          [X: 0.00, Y: 0.00]
        </div>
        <div className="absolute bottom-16 right-14 font-jetbrains text-[10px] tracking-wider text-[#8e9192] uppercase">
          [SYS_READY]
        </div>

        {/* Terminal Card */}
        <div className="w-full max-w-md bg-[#111316]/95 border-2 border-[#232629] p-8 relative shadow-2xl">
          {/* Card Corner Accents */}
          <div className="absolute top-0 left-0 w-2.5 h-2.5 bg-[#232629]"></div>
          <div className="absolute top-0 right-0 w-2.5 h-2.5 bg-[#232629]"></div>
          <div className="absolute bottom-0 left-0 w-2.5 h-2.5 bg-[#232629]"></div>
          <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-[#232629]"></div>

          <div className="text-center mb-8 border-b border-[#232629] pb-4">
            <h1 className="font-libre text-3xl font-bold tracking-tighter text-white uppercase">
              Authentication Terminal
            </h1>
            <p className="font-jetbrains text-[11px] text-[#c4c7c8] mt-2 uppercase tracking-widest">
              Protocol_01: Identity_Verification
            </p>
          </div>

          {/* System Calibration Sequence */}
          <div className="h-24 w-full border-2 border-[#232629] mb-8 relative overflow-hidden bg-[#0c0e11] flex items-center justify-center">
            {isCalibrating ? (
              <div className="flex items-center text-[#8e9192] font-jetbrains text-[10px] tracking-widest uppercase">
                <RefreshCw className="mr-2 h-4.5 w-4.5 animate-spin text-white" />
                CALIBRATING SYSTEM...
              </div>
            ) : (
              <div className="text-center">
                <div className="text-[#4edea3] font-jetbrains text-[10px] tracking-widest uppercase mb-1">
                  CALIBRATION COMPLETED
                </div>
                <div className="text-[#8e9192] font-jetbrains text-[8px]">
                  ALL NEURAL PATHWAYS ALIGNED
                </div>
              </div>
            )}
            <div className="absolute bottom-0 left-0 h-0.5 bg-[#4edea3] transition-all duration-1000" style={{ width: isCalibrating ? '30%' : '100%' }}></div>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label
                className="block font-jetbrains text-[10px] text-[#c4c7c8] mb-2 uppercase flex items-center tracking-wider"
                htmlFor="operative_id"
              >
                <Fingerprint className="h-4 w-4 mr-2 text-white" />
                REF_OPERATIVE_ID
              </label>
              <input
                className="input-bracket w-full px-4 py-3 font-jetbrains text-sm text-white placeholder-[#333538] uppercase"
                id="operative_id"
                name="operative_id"
                placeholder="OP-882-ALPHA"
                required
                type="text"
                value={operativeId}
                onChange={(e) => setOperativeId(e.target.value)}
              />
            </div>

            <div>
              <label
                className="block font-jetbrains text-[10px] text-[#c4c7c8] mb-2 uppercase flex items-center tracking-wider"
                htmlFor="access_token"
              >
                <Key className="h-4 w-4 mr-2 text-white" />
                SEC_ACCESS_TOKEN
              </label>
              <input
                className="input-bracket w-full px-4 py-3 font-jetbrains text-sm text-white placeholder-[#333538]"
                id="access_token"
                name="access_token"
                placeholder="••••••••••••"
                required
                type="password"
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
              />
            </div>

            <div className="flex justify-between items-center font-jetbrains text-[10px] text-[#c4c7c8] uppercase tracking-wider">
              <span className="flex items-center">
                <span className="w-2 h-2 rounded-full bg-[#E4F222] mr-2 animate-pulse"></span>
                UPLINK ESTABLISHED
              </span>
              <span className="text-[#8e9192]">T-MINUS 00:00:00</span>
            </div>

            <button
              className="w-full bg-white text-[#111316] font-libre font-bold py-3 hover:bg-[#c4c7c8] transition-colors border-2 border-white uppercase tracking-wider flex items-center justify-center group cursor-pointer"
              type="submit"
            >
              INITIATE LOGIN
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </form>

          {/* Card Footer */}
          <div className="mt-6 pt-4 border-t border-[#232629] flex justify-between items-center font-jetbrains text-[10px] text-[#8e9192]">
            <span>V.1.0.4 [STABLE]</span>
            <QrCode className="h-4 w-4" />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-[#0c0e11] fixed bottom-0 w-full flex justify-between items-center px-8 py-3 z-50 border-t border-[#232629]">
        <div className="font-jetbrains text-[11px] text-white flex items-center gap-4">
          <Shield className="h-4 w-4" />
          <span>SYS_REF: 2026.Q2 // ALL RIGHTS RESERVED</span>
        </div>
        <div className="flex gap-6">
          <span className="font-jetbrains text-[10px] text-[#c4c7c8] uppercase">STATUS: OPERATIONAL</span>
          <span className="font-jetbrains text-[10px] text-[#c4c7c8] uppercase">ENCRYPTION: AES-256</span>
          <span className="font-jetbrains text-[10px] text-[#c4c7c8] uppercase">CORE_ID: RM-882</span>
        </div>
      </footer>
    </div>
  );
}
