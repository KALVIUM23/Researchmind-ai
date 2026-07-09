"use client";

import React, { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Search, MessageSquare, Terminal, Settings, LayoutDashboard, Database, Activity, FileText, HelpCircle, LogOut, User } from "lucide-react";
import { Command } from "cmdk";
import OnboardingTour from "./OnboardingTour";
import { useAuth } from "@/contexts/AuthContext";

export default function GlobalShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [cmdkOpen, setCmdkOpen] = useState(false);
  const { user, logout } = useAuth();
  
  const isAuthPage = pathname.startsWith("/login") || pathname.startsWith("/register");

  // CMDK Keyboard shortcut
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCmdkOpen((open) => !open);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = (command: () => void) => {
    setCmdkOpen(false);
    command();
  };

  return (
    <div className="h-screen w-screen flex flex-col font-geist bg-[#111316] text-[#e2e2e6] overflow-hidden relative cursor-crosshair">
      {/* CRT Overlay Effect */}
      <div className="fixed inset-0 crt-overlay mix-blend-overlay pointer-events-none z-0"></div>

      {/* CMDK Modal */}
      {cmdkOpen && (
        <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#111316] border border-[#232629] w-full max-w-lg rounded shadow-2xl overflow-hidden flex flex-col">
            <Command className="flex flex-col w-full h-full">
              <Command.Input 
                autoFocus 
                placeholder="Search global commands..." 
                className="w-full bg-transparent border-b border-[#232629] text-white p-4 font-jetbrains text-sm focus:outline-none"
              />
              <Command.List className="max-h-[300px] overflow-y-auto p-2 custom-scrollbar">
                <Command.Empty className="p-4 text-center text-[#8e9192] font-jetbrains text-xs">No results found.</Command.Empty>
                
                <Command.Group heading="Navigation" className="text-[#8e9192] font-jetbrains text-[10px] uppercase p-2">
                  <Command.Item 
                    onSelect={() => runCommand(() => router.push("/workspace"))}
                    className="flex items-center gap-2 p-2 mt-1 rounded cursor-pointer text-white hover:bg-[#333538]/50 aria-selected:bg-[#333538]/50"
                  >
                    <LayoutDashboard className="w-4 h-4" /> Go to Workspace
                  </Command.Item>
                  <Command.Item 
                    onSelect={() => runCommand(() => router.push("/chat"))}
                    className="flex items-center gap-2 p-2 mt-1 rounded cursor-pointer text-white hover:bg-[#333538]/50 aria-selected:bg-[#333538]/50"
                  >
                    <MessageSquare className="w-4 h-4" /> Go to Agent Chat
                  </Command.Item>
                  <Command.Item 
                    onSelect={() => runCommand(() => router.push("/archives"))}
                    className="flex items-center gap-2 p-2 mt-1 rounded cursor-pointer text-white hover:bg-[#333538]/50 aria-selected:bg-[#333538]/50"
                  >
                    <Database className="w-4 h-4" /> Go to Archives
                  </Command.Item>
                  <Command.Item 
                    onSelect={() => runCommand(() => router.push("/logs"))}
                    className="flex items-center gap-2 p-2 mt-1 rounded cursor-pointer text-white hover:bg-[#333538]/50 aria-selected:bg-[#333538]/50"
                  >
                    <Activity className="w-4 h-4" /> Go to System Logs
                  </Command.Item>
                  <Command.Item 
                    onSelect={() => runCommand(() => router.push("/settings"))}
                    className="flex items-center gap-2 p-2 mt-1 rounded cursor-pointer text-white hover:bg-[#333538]/50 aria-selected:bg-[#333538]/50"
                  >
                    <Settings className="w-4 h-4" /> Go to Settings
                  </Command.Item>
                </Command.Group>
                
              </Command.List>
            </Command>
          </div>
        </div>
      )}

      {/* Top Nav Bar - Hidden on Auth pages */}
      {!isAuthPage && (
        <nav className="bg-[#111316] text-white font-jetbrains text-xs uppercase w-full border-b border-[#232629] flex justify-between items-center px-8 h-16 z-50 shrink-0 relative">
        <div className="flex items-center gap-6">
          <Link href="/workspace" className="font-libre text-lg font-bold tracking-tighter text-white hover:opacity-80 transition-opacity">
            RESEARCH_MIND_AI
          </Link>
          <div className="hidden md:block w-3 h-3 border-l border-t border-[#8e9192]/30"></div>
        </div>

        <div className="hidden md:flex gap-8 items-center h-full">
          <Link href="/workspace" className={`h-full flex items-center transition-colors duration-75 px-4 ${pathname.includes('/workspace') ? 'text-white border-b-2 border-white opacity-80' : 'text-[#8e9192] hover:text-white'}`}>
            WORKSPACE
          </Link>
          <Link href="/chat" data-tour="nav-chat" className={`h-full flex items-center transition-colors duration-75 px-4 ${pathname.includes('/chat') ? 'text-white border-b-2 border-white opacity-80' : 'text-[#8e9192] hover:text-white'}`}>
            AGENT CHAT
          </Link>
          <Link href="/archives" className={`h-full flex items-center transition-colors duration-75 px-4 ${pathname.includes('/archives') ? 'text-white border-b-2 border-white opacity-80' : 'text-[#8e9192] hover:text-white'}`}>
            ARCHIVES
          </Link>
          <Link href="/logs" className={`h-full flex items-center transition-colors duration-75 px-4 ${pathname.includes('/logs') ? 'text-white border-b-2 border-white opacity-80' : 'text-[#8e9192] hover:text-white'}`}>
            LOGS
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative hidden sm:block" data-tour="cmdk">
            <button 
              onClick={() => setCmdkOpen(true)}
              className="flex items-center gap-2 bg-[#1e2023] border border-[#232629] hover:border-white transition-colors text-[#8e9192] font-jetbrains text-xs px-3 py-1.5 w-48 text-left"
            >
              <Search className="h-3.5 w-3.5" />
              <span>CMD+K</span>
            </button>
          </div>

          <Link 
            href="/chat"
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 bg-[#4edea3]/10 hover:bg-[#4edea3]/20 border border-[#4edea3]/40 text-[#4edea3] rounded font-jetbrains text-[10px] uppercase transition-colors"
          >
            <MessageSquare className="h-3 w-3" />
            AGENT CHAT
          </Link>

          <Link href="/settings" className="text-[#8e9192] hover:text-white transition-colors p-2">
            <Settings className="h-4 w-4" />
          </Link>
          <button 
            onClick={() => window.dispatchEvent(new Event('restart-tour'))}
            className="text-[#8e9192] hover:text-[#4edea3] transition-colors p-2"
            title="Restart Interactive Tour"
          >
            <HelpCircle className="h-4 w-4" />
          </button>
          
          {user && (
            <>
              <div className="w-px h-6 bg-[#232629] mx-2"></div>
              <div className="flex items-center gap-2 text-[#8e9192] font-jetbrains text-[10px]">
                <User className="h-3.5 w-3.5" />
                <span className="truncate max-w-[120px]">{user.email}</span>
              </div>
              <button 
                onClick={logout}
                className="text-[#8e9192] hover:text-red-400 transition-colors p-2 ml-1"
                title="Sign Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      </nav>
      )}

      {/* Main Content Area */}
      {children}

      {/* Interactive Tour Overlay */}
      <OnboardingTour />

      {/* Footer */}
      <footer className="bg-[#0c0e11] text-[#8e9192] font-jetbrains text-[9px] w-full flex justify-between items-center px-8 py-2 z-50 border-t border-[#232629] shrink-0 relative">
        <div className="text-white opacity-85">
          SYS_REF: 2026.Q2 // ALL RIGHTS RESERVED
        </div>
        <div className="flex gap-6 items-center">
          <span className="hover:text-white cursor-pointer transition-colors uppercase">STATUS: OPERATIONAL</span>
          <span className="hover:text-white cursor-pointer transition-colors uppercase">ENCRYPTION: AES-256</span>
          <span className="hover:text-white cursor-pointer transition-colors uppercase">CORE_ID: RM-882</span>
        </div>
      </footer>
    </div>
  );
}
