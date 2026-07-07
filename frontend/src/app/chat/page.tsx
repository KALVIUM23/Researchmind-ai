"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Sparkles, Settings, ArrowUp, Link2, Heart, Copy, Share2, 
  HelpCircle, Shield, Menu, MessageSquare, BookOpen, Layers, 
  Clock, Compass, User, Compass as RetrieverIcon, Compass as PlannerIcon
} from "lucide-react";

interface Citation {
  source?: string;
  page?: string;
  text: string;
}

interface Message {
  role: "user" | "agent";
  isThinking?: boolean;
  content: string;
  citations?: Citation[];
}

export default function AgenticResearchOS() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState("");
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState("chat");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    const userMessage: Message = { role: "user", content: inputVal };
    const agentMessage: Message = { role: "agent", isThinking: true, content: "Initiating research synthesis loops...", citations: [] };
    
    setMessages(prev => [...prev, userMessage, agentMessage]);
    setInputVal("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/questions/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.content })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Server error: ${response.status}`);
      }

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let finalContent = "";
      let buffer = "";
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            if (data.type === "token") {
              finalContent += data.data;
              setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = {
                  ...newMessages[newMessages.length - 1],
                  isThinking: false,
                  content: finalContent
                };
                return newMessages;
              });
            } else if (data.type === "sources") {
              setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = {
                  ...newMessages[newMessages.length - 1],
                  citations: data.data || []
                };
                return newMessages;
              });
            } else if (data.type === "done") {
              break;
            }
          } catch (err) {
            console.error("Error parsing chunk:", err);
          }
        }
      }
    } catch (err: any) {
      console.error(err);
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          isThinking: false,
          content: err.message || "Failed to connect to the reasoning backend."
        };
        return newMessages;
      });
    }
  };

  return (
        <main className="flex-1 flex flex-col relative w-full h-full overflow-hidden bg-[#0A0A0A] text-[#e4e1ed]">
          {/* Top pulse indicator line */}
          <div className="pulse-line absolute top-0 left-0 z-10"></div>

          {/* Sources Carousel */}
          <div className="px-8 py-4 border-b border-[#1F1F1F] bg-[#111111]/40 backdrop-blur-md shrink-0">
            <div className="flex items-center gap-2 mb-2 text-xs font-bold tracking-widest uppercase text-[#908fa0]">
              <Compass className="h-4.5 w-4.5 text-[#4edea3]" />
              <span>Verified Sources (8)</span>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-1 custom-scrollbar">
              <div className="flex-shrink-0 w-60 p-2.5 rounded-xl glass-panel hover:bg-[#1A1A1A] transition-all cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#1F1F1F] flex items-center justify-center text-xs text-[#908fa0] font-bold group-hover:text-white">
                    PDF
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <h4 className="text-xs font-semibold text-white truncate">Neural Synthesis in LLMs</h4>
                    <p className="text-[9px] text-[#908fa0] uppercase font-mono tracking-wider">nature.com/articles/24-x1</p>
                  </div>
                </div>
              </div>

              <div className="flex-shrink-0 w-60 p-2.5 rounded-xl glass-panel hover:bg-[#1A1A1A] transition-all cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#1F1F1F] flex items-center justify-center text-xs text-[#908fa0] font-bold group-hover:text-white">
                    DOC
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <h4 className="text-xs font-semibold text-white truncate">Agentic Frameworks v4.2</h4>
                    <p className="text-[9px] text-[#908fa0] uppercase font-mono tracking-wider">arxiv.org/pdf/2312.001</p>
                  </div>
                </div>
              </div>

              <div className="flex-shrink-0 w-60 p-2.5 rounded-xl glass-panel hover:bg-[#1A1A1A] transition-all cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#1F1F1F] flex items-center justify-center text-xs text-[#908fa0] font-bold group-hover:text-white">
                    API
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <h4 className="text-xs font-semibold text-white truncate">Distributed Reasoning</h4>
                    <p className="text-[9px] text-[#908fa0] uppercase font-mono tracking-wider">ieee.org/abstract/98321</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Messages List Container */}
          <div className="flex-grow overflow-y-auto custom-scrollbar px-6 py-8 space-y-8 pb-32">
            {messages.map((msg, idx) => (
              <div key={idx} className="max-w-[850px] mx-auto flex gap-4">
                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1 text-xs font-bold ${
                  msg.role === "user" ? "bg-[#1F1F1F] text-white" : "bg-[#4edea3]/20 text-[#4edea3]"
                }`}>
                  {msg.role === "user" ? "U" : "A"}
                </div>
                <div className="flex-1 space-y-4">
                  {msg.role === "user" ? (
                    <h3 className="text-lg font-medium text-white">{msg.content}</h3>
                  ) : (
                    <div className="space-y-4">
                      {/* Optional Expandable Thinking Trace */}
                      {msg.isThinking && (
                        <div className="p-4 glass-panel border-[#4edea3]/30 rounded-xl agent-glow flex items-center gap-3">
                          <div className="relative w-4 h-4">
                            <div className="absolute inset-0 border-2 border-[#4edea3] rounded-full border-t-transparent animate-spin"></div>
                          </div>
                          <span className="text-sm text-[#4edea3] font-medium italic">Synthesizing cross-domain architectures...</span>
                        </div>
                      )}

                      <div className="text-md text-[#e4e1ed] leading-relaxed space-y-4">
                        <p>{msg.content}</p>
                        
                        {!msg.isThinking && msg.citations && msg.citations.length > 0 && (
                          <>
                            <div className="mt-6 pt-4 border-t border-[#1F1F1F]/40 grid grid-cols-1 md:grid-cols-2 gap-4">
                              {msg.citations.map((c, i) => (
                                <div key={i} className="p-3.5 glass-panel rounded-xl text-xs flex flex-col gap-1 hover:bg-[#1A1A1A] transition-colors cursor-pointer border border-transparent hover:border-[#4edea3]/30">
                                  <div className="flex items-center justify-between">
                                    <span className="text-[#4edea3] font-bold">[{i+1}] {c.source || 'Document'}</span>
                                    <span className="text-[#908fa0] font-mono">Page {c.page || '1'}</span>
                                  </div>
                                  <p className="text-[#908fa0] italic mt-1 line-clamp-3">"{c.text}"</p>
                                </div>
                              ))}
                            </div>
                          </>
                        )}
                      </div>

                      {/* Message Actions */}
                      <div className="flex items-center gap-3 pt-2">
                        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full glass-panel hover:bg-[#1A1A1A] transition-all border-none text-xs text-[#908fa0] hover:text-white">
                          <Heart className="h-3.5 w-3.5" />
                          <span>Helpful</span>
                        </button>
                        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full glass-panel hover:bg-[#1A1A1A] transition-all border-none text-xs text-[#908fa0] hover:text-white">
                          <Copy className="h-3.5 w-3.5" />
                          <span>Copy</span>
                        </button>
                        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full glass-panel hover:bg-[#1A1A1A] transition-all border-none text-xs text-[#908fa0] hover:text-white">
                          <Share2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Floating Message Input Bar */}
          <div className="absolute bottom-0 left-0 w-full p-6 bg-gradient-to-t from-[#0A0A0A] via-[#0A0A0A]/95 to-transparent">
            <div className="max-w-[850px] mx-auto" data-tour="chat-input">
              <form onSubmit={handleSubmit} className="glass-panel rounded-full p-2 pl-6 flex items-center gap-3 shadow-2xl border-[#1F1F1F] focus-within:border-[#4edea3]/50 transition-all">
                {/* Active chip */}
                <div className="flex items-center gap-1 border-r border-[#1F1F1F] pr-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#4edea3]"></span>
                  <span className="text-xs font-semibold text-white tracking-wider">Research</span>
                </div>
                {/* Input */}
                <input 
                  className="flex-1 bg-transparent border-none focus:outline-none focus:ring-0 text-sm text-white placeholder:text-[#908fa0]/50" 
                  placeholder="Ask follow-up or research deeper..." 
                  type="text" 
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                />
                {/* Controls */}
                <div className="flex items-center gap-1.5">
                  <button type="button" className="p-2 text-[#908fa0] hover:text-white transition-colors">
                    <Link2 className="h-4 w-4" />
                  </button>
                  <button type="submit" className="w-9 h-9 flex items-center justify-center bg-[#4edea3] text-[#0A0A0A] rounded-full hover:brightness-110 active:scale-95 transition-all">
                    <ArrowUp className="h-4.5 w-4.5" />
                  </button>
                </div>
              </form>
              <div className="flex justify-center mt-2 text-[9px] text-[#908fa0]/50 uppercase tracking-widest">
                <span>Command + Enter to search web</span>
              </div>
            </div>
          </div>
        </main>
  );
}
