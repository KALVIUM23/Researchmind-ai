import type { Metadata } from "next";
import { Geist, Geist_Mono, EB_Garamond, Hanken_Grotesk, JetBrains_Mono, Libre_Caslon_Text } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const ebGaramond = EB_Garamond({
  variable: "--font-eb-garamond",
  subsets: ["latin"],
});

const hankenGrotesk = Hanken_Grotesk({
  variable: "--font-hanken-grotesk",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

const libreCaslonText = Libre_Caslon_Text({
  variable: "--font-libre-caslon-text",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "ResearchMind AI Workspace",
  description: "Advanced AI-powered research platform and neural query protocol.",
};

import GlobalShell from "@/components/GlobalShell";
import { AuthProvider } from "@/contexts/AuthContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${ebGaramond.variable} ${hankenGrotesk.variable} ${jetbrainsMono.variable} ${libreCaslonText.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#111316] text-[#e2e2e6]">
        <AuthProvider>
          <GlobalShell>{children}</GlobalShell>
        </AuthProvider>
      </body>
    </html>
  );
}
