import type { Metadata } from 'next';
import './globals.css';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';

export const metadata: Metadata = {
  title: 'NoteFlow AI — Intelligent Learning',
  description: 'AI-powered learning assistant. Upload PDFs, search knowledge, and generate personalized study plans.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-[#0e0e10] text-white flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <Topbar />
          <main className="flex-1 overflow-y-auto bg-[#0e0e10]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
