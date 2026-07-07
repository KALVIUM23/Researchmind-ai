"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { X, ChevronRight, ChevronLeft, Check, HelpCircle } from "lucide-react";

interface TourStep {
  id: string;
  title: string;
  content: string;
  path: string; // The route this step belongs on
  position: "top" | "bottom" | "left" | "right";
}

const TOUR_STEPS: TourStep[] = [
  {
    id: "cmdk",
    title: "1. Global Navigation",
    content: "Welcome! Press CMD+K anywhere to search documents or quickly jump between subsystems.",
    path: "/workspace",
    position: "bottom"
  },
  {
    id: "upload-btn",
    title: "2. Data Ingestion",
    content: "Upload a PDF document here. The system will vectorize it and prepare it for reasoning. Wait for the status to say 'Ready'.",
    path: "/workspace",
    position: "right"
  },
  {
    id: "action-btns",
    title: "3. Neural Synthesis",
    content: "Once a document is ready, select it and click these buttons to instantly stream a summary or generate deep research notes.",
    path: "/workspace",
    position: "bottom"
  },
  {
    id: "nav-chat",
    title: "4. Agent Chat",
    content: "Navigate to the Chat interface to ask follow-up questions and interact with your documents.",
    path: "/workspace",
    position: "bottom"
  },
  {
    id: "chat-input",
    title: "5. Ask Anything",
    content: "Type your query here. The Agent will cross-reference your documents and provide cited answers.",
    path: "/chat",
    position: "top"
  }
];

export default function OnboardingTour() {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  
  const router = useRouter();
  const pathname = usePathname();

  // Initialize tour on first visit
  useEffect(() => {
    const hasSeenTour = localStorage.getItem("rm_tour_completed");
    if (!hasSeenTour) {
      // Small delay to let UI mount
      setTimeout(() => setIsActive(true), 1500);
    }

    // Listen for custom event to restart tour
    const handleRestart = () => {
      setCurrentStep(0);
      setIsActive(true);
      if (pathname !== "/workspace") {
        router.push("/workspace");
      }
    };
    window.addEventListener("restart-tour", handleRestart);
    return () => window.removeEventListener("restart-tour", handleRestart);
  }, [pathname, router]);

  // Update target rect when step changes or window resizes
  const updateRect = useCallback(() => {
    if (!isActive) return;
    
    const step = TOUR_STEPS[currentStep];
    
    // Auto-navigate if wrong page
    if (pathname !== step.path) {
      router.push(step.path);
      return;
    }

    // Find element
    const el = document.querySelector(`[data-tour="${step.id}"]`);
    if (el) {
      // Scroll into view if needed
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Add slight delay after scroll
      setTimeout(() => {
        setTargetRect(el.getBoundingClientRect());
      }, 300);
    } else {
      // Retry in case it hasn't rendered yet
      setTimeout(() => {
        const retryEl = document.querySelector(`[data-tour="${step.id}"]`);
        if (retryEl) setTargetRect(retryEl.getBoundingClientRect());
      }, 500);
    }
  }, [isActive, currentStep, pathname, router]);

  useEffect(() => {
    updateRect();
    window.addEventListener("resize", updateRect);
    return () => window.removeEventListener("resize", updateRect);
  }, [updateRect]);

  if (!isActive) return null;

  const step = TOUR_STEPS[currentStep];
  const isLast = currentStep === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLast) {
      setIsActive(false);
      localStorage.setItem("rm_tour_completed", "true");
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleClose = () => {
    setIsActive(false);
    localStorage.setItem("rm_tour_completed", "true");
  };

  // Calculate popover position
  let popoverStyle: React.CSSProperties = { top: "50%", left: "50%", transform: "translate(-50%, -50%)" };
  
  if (targetRect) {
    const spacing = 16;
    if (step.position === "bottom") {
      popoverStyle = { top: targetRect.bottom + spacing, left: targetRect.left + (targetRect.width / 2), transform: "translateX(-50%)" };
    } else if (step.position === "top") {
      popoverStyle = { top: targetRect.top - spacing, left: targetRect.left + (targetRect.width / 2), transform: "translate(-50%, -100%)" };
    } else if (step.position === "right") {
      popoverStyle = { top: targetRect.top + (targetRect.height / 2), left: targetRect.right + spacing, transform: "translateY(-50%)" };
    } else if (step.position === "left") {
      popoverStyle = { top: targetRect.top + (targetRect.height / 2), left: targetRect.left - spacing, transform: "translate(-100%, -50%)" };
    }
  }

  return (
    <>
      {/* Backdrop (Darkens screen) */}
      <div className="fixed inset-0 bg-black/50 z-[9998] transition-opacity"></div>
      
      {/* Highlight Box (shows exactly over the target element to make it appear lit) */}
      {targetRect && (
        <div 
          className="fixed z-[9999] pointer-events-none border-2 border-[#4edea3] transition-all duration-300 ease-out"
          style={{
            top: targetRect.top - 4,
            left: targetRect.left - 4,
            width: targetRect.width + 8,
            height: targetRect.height + 8,
            boxShadow: "0 0 0 9999px rgba(0,0,0,0.4)"
          }}
        ></div>
      )}

      {/* Popover Card */}
      <div 
        className="fixed z-[10000] bg-[#111316] border border-[#4edea3] w-[320px] shadow-2xl transition-all duration-300 ease-out font-jetbrains"
        style={popoverStyle}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-3 border-b border-[#232629] bg-[#4edea3]/10">
          <span className="text-[#4edea3] text-xs font-bold uppercase">{step.title}</span>
          <button onClick={handleClose} className="text-[#8e9192] hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          <p className="text-[#e2e2e6] text-sm leading-relaxed font-hanken">
            {step.content}
          </p>
        </div>

        {/* Footer Controls */}
        <div className="flex items-center justify-between p-3 border-t border-[#232629] bg-[#0c0e11]">
          <span className="text-[#8e9192] text-[10px]">
            {currentStep + 1} / {TOUR_STEPS.length}
          </span>
          <div className="flex gap-2">
            <button 
              onClick={handlePrev} 
              disabled={currentStep === 0}
              className="px-2 py-1 border border-[#232629] text-[#8e9192] hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button 
              onClick={handleNext} 
              className="px-3 py-1 bg-[#4edea3] text-[#0A0A0A] font-bold text-xs uppercase flex items-center gap-1 hover:brightness-110 transition-colors"
            >
              {isLast ? (
                <>Finish <Check className="w-3 h-3" /></>
              ) : (
                <>Next <ChevronRight className="w-3 h-3" /></>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
