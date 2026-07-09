"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Fingerprint, RefreshCw, QrCode } from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setIsLoading(true);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Registration failed");
      }

      // Automatically redirect to login after successful registration
      router.push("/login");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#111316] text-[#e2e2e6] min-h-screen flex flex-col font-geist overflow-hidden relative">
      <main className="flex-grow flex items-center justify-center p-4 relative z-10 grid-bg-brutalist">
        
        {/* Registration Marks */}
        <div className="absolute top-8 left-8 w-4 h-4 border-t border-l border-[#232629]"></div>
        <div className="absolute top-8 right-8 w-4 h-4 border-t border-r border-[#232629]"></div>
        <div className="absolute bottom-16 left-8 w-4 h-4 border-b border-l border-[#232629]"></div>
        <div className="absolute bottom-16 right-8 w-4 h-4 border-b border-r border-[#232629]"></div>
        
        {/* Coordinate Stamps */}
        <div className="absolute top-8 left-14 font-jetbrains text-[10px] tracking-[0.1em] text-[#8e9192] uppercase">
          [X: 0.00, Y: 0.00]
        </div>
        <div className="absolute bottom-16 right-14 font-jetbrains text-[10px] tracking-[0.1em] text-[#8e9192] uppercase">
          [SYS_READY]
        </div>

        <div className="w-full max-w-md bg-[#111316] border border-[#232629] p-6 relative shadow-2xl">
          {/* Card Corner Accents */}
          <div className="absolute top-0 left-0 w-2 h-2 bg-[#232629]"></div>
          <div className="absolute top-0 right-0 w-2 h-2 bg-[#232629]"></div>
          <div className="absolute bottom-0 left-0 w-2 h-2 bg-[#232629]"></div>
          <div className="absolute bottom-0 right-0 w-2 h-2 bg-[#232629]"></div>

          <div className="text-center mb-8 border-b border-[#232629] pb-4">
            <h1 className="font-garamond text-[32px] md:text-[48px] tracking-tighter text-white uppercase font-semibold leading-[1.1]">Create Account</h1>
            <p className="font-jetbrains text-[12px] text-[#c4c7c8] mt-2 uppercase tracking-wider">Protocol_02: Operative_Enrollment</p>
          </div>

          {/* System Calibration Sequence */}
          <div className="h-16 w-full border border-[#232629] mb-8 relative overflow-hidden bg-[#0c0e11]">
            <div className="absolute inset-0 flex items-center justify-center text-[#444748] font-jetbrains text-[10px] tracking-widest opacity-50">
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> ESTABLISHING SECURE LINK...
            </div>
            
            {error && (
              <div className="absolute inset-0 flex items-center justify-center bg-red-900/30 text-red-200 text-xs font-jetbrains font-bold uppercase backdrop-blur-sm z-10">
                ERR: {error}
              </div>
            )}
          </div>

          <form onSubmit={handleRegister} className="space-y-6">
            <div>
              <label className="flex items-center font-jetbrains text-[10px] tracking-[0.1em] text-[#c4c7c8] mb-2 uppercase" htmlFor="operative_id">
                <span className="w-4 h-4 mr-2 text-white/50 border border-white/20 rounded-full flex items-center justify-center text-[8px] font-bold">@</span>
                NEW_OPERATIVE_ID (EMAIL)
              </label>
              <input 
                className="input-bracket w-full px-4 py-3 font-jetbrains text-[13px] text-white transition-all duration-200 placeholder-[#333538]" 
                id="operative_id" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="OP-XXXX-XXXX" 
                required 
                type="email"
              />
            </div>

            <div>
              <label className="flex items-center font-jetbrains text-[10px] tracking-[0.1em] text-[#c4c7c8] mb-2 uppercase" htmlFor="access_token">
                <span className="w-4 h-4 mr-2 text-white/50 border border-white/20 flex items-center justify-center text-[8px] font-bold">#</span>
                SET_ACCESS_TOKEN (PASSWORD)
              </label>
              <input 
                className="input-bracket w-full px-4 py-3 font-jetbrains text-[13px] text-white transition-all duration-200 placeholder-[#333538]" 
                id="access_token" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="MIN 8 CHARACTERS" 
                required 
                type="password"
              />
            </div>

            <div>
              <label className="flex items-center font-jetbrains text-[10px] tracking-[0.1em] text-[#c4c7c8] mb-2 uppercase" htmlFor="confirm_token">
                <span className="w-4 h-4 mr-2 text-white/50 border border-white/20 flex items-center justify-center text-[8px] font-bold">#</span>
                CONFIRM_ACCESS_TOKEN
              </label>
              <input 
                className="input-bracket w-full px-4 py-3 font-jetbrains text-[13px] text-white transition-all duration-200 placeholder-[#333538]" 
                id="confirm_token" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••••••" 
                required 
                type="password"
              />
            </div>

            <div className="flex justify-between items-center font-jetbrains text-[10px] tracking-[0.1em] text-[#c4c7c8] uppercase">
              <span className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-[#E4F222] mr-2 animate-pulse"></div> 
                ENROLLMENT READY
              </span>
              <span className="font-jetbrains text-[13px] text-[#444748]">
                {isLoading ? "T-MINUS 00:00:01" : "T-MINUS 00:00:00"}
              </span>
            </div>

            <button 
              disabled={isLoading}
              className="w-full bg-white text-[#1a1c1e] font-garamond text-[24px] font-semibold py-3 hover:bg-[#333538] hover:text-white transition-colors border border-white uppercase tracking-wider flex items-center justify-center group disabled:opacity-50" 
              type="submit"
            >
              {isLoading ? "REGISTERING..." : "INITIATE ENROLLMENT"} 
              {!isLoading && <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />}
            </button>
          </form>
          
          <div className="mt-4 pt-4 text-center font-jetbrains text-[10px] tracking-[0.1em] text-[#8e9192] uppercase cursor-pointer hover:text-white transition-colors" onClick={() => router.push("/login")}>
            [ EXISTING OPERATIVE? LOGIN HERE ]
          </div>

          <div className="mt-6 pt-4 border-t border-[#232629] flex justify-between items-center font-jetbrains text-[10px] tracking-[0.1em] text-[#444748]">
            <span>V.1.0.4 [STABLE]</span>
            <QrCode className="w-4 h-4" />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-[#111316] w-full flex justify-between items-center px-8 py-2 z-50 border-t border-[#232629]">
        <div className="font-jetbrains text-[12px] text-white flex items-center gap-4">
          <Fingerprint className="w-4 h-4" />
          <span>SYS_REF: 2026.Q2 // ALL RIGHTS RESERVED</span>
        </div>
        <div className="hidden md:flex gap-6">
          <span className="font-jetbrains text-[10px] tracking-[0.1em] text-[#c4c7c8] uppercase">STATUS: OPERATIONAL</span>
          <span className="font-jetbrains text-[10px] tracking-[0.1em] text-[#c4c7c8] uppercase">ENCRYPTION: AES-256</span>
          <span className="font-jetbrains text-[10px] tracking-[0.1em] text-[#c4c7c8] uppercase">CORE_ID: RM-882</span>
        </div>
      </footer>
    </div>
  );
}
