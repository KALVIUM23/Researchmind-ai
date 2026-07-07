"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { 
  FolderOpen, Folder, Database, FileText, Settings, Terminal, Search, 
  MoreVertical, Save, Bold, Italic, Code, Link as LinkIcon, AlertTriangle, 
  HelpCircle, Shield, RefreshCw, ZoomIn, MessageSquare 
} from "lucide-react";

import { uploadDocument, generateSummary, generateResearchNotes } from "@/lib/api";

type DocumentState = "Ready" | "Processing" | "Error";

interface DocumentMeta {
  id: string;
  filename: string;
  state: DocumentState;
}

export default function NeuralWorkspace() {
  const router = useRouter();
  const [editorContent, setEditorContent] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Poll for document status
  useEffect(() => {
    const processingDocs = documents.filter(d => d.state === "Processing");
    if (processingDocs.length === 0) return;

    const interval = setInterval(async () => {
      let updated = false;
      const newDocs = [...documents];
      
      for (let i = 0; i < newDocs.length; i++) {
        const doc = newDocs[i];
        if (doc.state === "Processing") {
          try {
            const res = await fetch(`http://localhost:8000/api/v1/documents/status/${doc.id}`);
            if (res.ok) {
              const data = await res.json();
              if (data.status === "Ready" || data.status.startsWith("Error")) {
                newDocs[i].state = data.status === "Ready" ? "Ready" : "Error";
                updated = true;
              }
            }
          } catch (e) {
            console.error("Status check failed", e);
          }
        }
      }

      if (updated) {
        setDocuments(newDocs);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [documents]);



  const handleCommit = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      alert("Changes successfully committed to primary neural graph repository.");
    }, 1200);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const res = await uploadDocument(file);
      setDocuments(prev => [...prev, { id: res.document_id, filename: file.name, state: "Processing" }]);
      setActiveDocId(res.document_id);
      setEditorContent(`Document ${file.name} uploaded.\nStatus: Processing in background queue...`);
    } catch (err) {
      alert("Failed to upload document");
      console.error(err);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleGenerateSummary = async () => {
    if (!activeDocId) return alert("Select a document first");
    
    const doc = documents.find(d => d.id === activeDocId);
    if (doc?.state !== "Ready") return alert("Document is still processing or failed.");

    setIsGenerating(true);
    setEditorContent("");
    
    try {
      const res = await generateSummary(activeDocId);
      const reader = res.body?.getReader();
      const decoder = new TextDecoder("utf-8");
      
      if (!reader) return;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            if (data.type === 'token') {
              setEditorContent(prev => prev + data.data);
            } else if (data.type === 'error') {
              setEditorContent(prev => prev + "\n[ERROR: " + data.data + "]");
            }
          } catch (e) {
            console.error("Parse error on chunk:", line);
          }
        }
      }
    } catch (err) {
      setEditorContent(prev => prev + "\nFailed to generate summary.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateNotes = async () => {
    if (!activeDocId) return alert("Select a document first");
    const doc = documents.find(d => d.id === activeDocId);
    if (doc?.state !== "Ready") return alert("Document is still processing or failed.");

    setIsGenerating(true);
    setEditorContent("Synthesizing research notes...");
    try {
      const res = await generateResearchNotes(activeDocId);
      setEditorContent(res.notes);
    } catch (err) {
      setEditorContent("Failed to generate research notes.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
      <main className="flex-1 flex overflow-hidden grid-bg-brutalist relative w-full h-full border-x border-[#232629]">
        
        {/* Left Side Pane: SOURCE_INDEX (25% Width) */}
        <aside className="w-1/4 border-r border-[#232629] bg-[#0c0e11]/90 backdrop-blur-sm flex flex-col shrink-0 hidden md:flex min-w-[250px]">
          <div className="p-4 border-b border-[#232629] flex justify-between items-center bg-[#1e2023]/50">
            <span className="font-jetbrains text-[10px] tracking-wider text-[#8e9192] uppercase">DIR // SOURCE_INDEX</span>
            <span className="material-symbols-outlined text-[#8e9192] text-[14px]">filter_list</span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2 font-jetbrains text-[12px]">
            <div className="flex items-center gap-2 p-2 hover:bg-[#333538]/30 cursor-pointer border border-transparent hover:border-[#232629] transition-all group">
              <FolderOpen className="text-white h-4 w-4" />
              <span className="text-white font-medium">QUANTUM_SYS_V2</span>
            </div>

            <div className="flex justify-between items-center px-2 mt-6 mb-2 border-b border-[#232629] pb-2">
              <span className="font-jetbrains text-[10px] text-[#8e9192]">DOCUMENTS</span>
              <button 
                data-tour="upload-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="text-[#4edea3] hover:text-white transition-colors cursor-pointer disabled:opacity-50"
                title="Upload PDF"
              >
                {isUploading ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <span className="text-[14px] leading-none">+</span>}
              </button>
              <input 
                type="file" 
                accept=".pdf" 
                className="hidden" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
              />
            </div>

            <div className="pl-4 space-y-1">
              {documents.length === 0 ? (
                <div className="text-[10px] text-[#8e9192] p-2 italic">No documents uploaded</div>
              ) : (
                documents.map(doc => (
                  <div 
                    key={doc.id}
                    onClick={() => setActiveDocId(doc.id)}
                    className={`flex items-center justify-between p-2 cursor-pointer transition-colors border-l-2 ${
                      activeDocId === doc.id ? "bg-[#333538]/35 border-[#4edea3] text-white" : "border-transparent text-[#8e9192] hover:bg-[#333538]/30 hover:text-white"
                    }`}
                  >
                    <div className="flex items-center gap-2 overflow-hidden">
                      <FileText className="h-3.5 w-3.5 shrink-0" />
                      <span className="truncate">{doc.filename}</span>
                    </div>
                    {doc.state === "Processing" && <RefreshCw className="h-3 w-3 animate-spin shrink-0 text-yellow-500" />}
                    {doc.state === "Error" && <AlertTriangle className="h-3 w-3 shrink-0 text-red-500" />}
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        {/* Right Side Pane: NEURAL_EDITOR (75% Width) */}
        <section className="w-3/4 flex flex-col border-r border-[#232629] bg-[#111316]/95 backdrop-blur-sm z-10 relative shadow-2xl">
          <header className="p-4 border-b border-[#232629] flex justify-between items-end bg-[#0c0e11]/50">
            <div>
              <div className="font-jetbrains text-[9px] text-[#8e9192] mb-1">ID: RM-882-ALPHA // ACTIVE_SESSION</div>
              <h1 className="font-libre text-2xl text-white tracking-tight uppercase">Active Research Log</h1>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={handleCommit}
                className="bg-white text-[#111316] font-jetbrains text-[11px] font-bold px-4 py-1.5 hover:bg-[#c7c6c7] transition-colors flex items-center gap-2 cursor-pointer"
              >
                {isSaving ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                COMMIT
              </button>
              <button className="border border-[#232629] text-[#e2e2e6] font-jetbrains px-2 py-1.5 hover:bg-[#333538]/50 transition-colors">
                <MoreVertical className="h-4 w-4" />
              </button>
            </div>
          </header>

          {/* Editor Toolbar */}
          <div className="border-b border-[#232629] p-3 flex gap-4 bg-[#1e2023]/30">
            <div className="flex items-center gap-2 border-r border-[#232629] pr-4">
              <button className="text-[#8e9192] hover:text-white p-1"><Bold className="h-4 w-4" /></button>
              <button className="text-[#8e9192] hover:text-white p-1"><Italic className="h-4 w-4" /></button>
              <button className="text-[#8e9192] hover:text-white p-1"><Code className="h-4 w-4" /></button>
            </div>
            <div className="flex items-center gap-3" data-tour="action-btns">
              <button 
                onClick={handleGenerateSummary}
                disabled={!activeDocId || isGenerating}
                className="flex items-center gap-1.5 px-3 py-1.5 text-white font-jetbrains text-[10px] border border-[#232629] hover:border-[#4edea3] hover:text-[#4edea3] transition-colors bg-[#0c0e11] uppercase disabled:opacity-50"
              >
                <LinkIcon className="h-3.5 w-3.5" />
                STREAM_SUMMARY
              </button>
              <button 
                onClick={handleGenerateNotes}
                disabled={!activeDocId || isGenerating}
                className="flex items-center gap-1.5 px-3 py-1.5 text-[#E4F222] font-jetbrains text-[10px] border border-[#E4F222]/30 hover:border-[#E4F222] hover:bg-[#E4F222]/10 transition-colors bg-[#0c0e11] uppercase disabled:opacity-50"
              >
                <Shield className="h-3.5 w-3.5" />
                RESEARCH_NOTES
              </button>
            </div>
          </div>

          {/* Editor Content */}
          <div className="flex-1 overflow-y-auto p-8 font-hanken text-base text-[#e2e2e6] leading-relaxed relative">
            <div className="max-w-4xl mx-auto space-y-6">
              <p className="text-[#8e9192] text-sm">Timestamp: <span className="font-jetbrains text-white">[{new Date().toISOString().split('T')[0]}]</span></p>
              
              {editorContent ? (
                <div className="whitespace-pre-wrap font-hanken text-base leading-relaxed mt-8">
                  {editorContent}
                </div>
              ) : (
                <div className="text-center text-[#8e9192] mt-32 italic text-lg">
                  Upload a document and select an action to populate the neural editor. <br/> <span className="text-sm">Press CMD+K to search.</span>
                </div>
              )}
              {isGenerating && <span className="inline-block w-2.5 h-5 bg-[#4edea3] animate-pulse align-middle ml-1"></span>}
            </div>
          </div>
        </section>

      </main>
  );
}
