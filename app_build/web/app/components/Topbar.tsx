'use client';

import { Bell, Zap } from 'lucide-react';

interface TopbarProps {
  placeholder?: string;
}

export default function Topbar({ placeholder = 'Search insights...' }: TopbarProps) {
  return (
    <header className="flex items-center gap-4 px-6 h-[52px] min-h-[52px] border-b border-[#252530] bg-[#111117]/90 backdrop-blur-md sticky top-0 z-40 flex-shrink-0">
      {/* Search */}
      <div className="flex-1 max-w-xs">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#18181f] border border-[#252530] text-[#44445a] text-[12.5px] hover:border-[#35353f] cursor-text">
          <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span className="truncate">{placeholder}</span>
        </div>
      </div>

      <div className="flex-1" />

      {/* Right actions */}
      <div className="flex items-center gap-2">
        <button className="p-1.5 rounded-lg text-[#44445a] hover:bg-[#18181f] hover:text-white">
          <Bell className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#18181f] border border-[#252530]">
          <Zap className="w-3 h-3 text-indigo-400" />
          <span className="text-[11.5px] text-[#7777aa] font-medium">NoteFlow</span>
        </div>

        <button className="px-2.5 py-1.5 rounded-lg bg-[#18181f] border border-[#252530] text-[11.5px] text-white font-medium hover:border-indigo-700 hover:bg-indigo-900/20">
          Upgrade Pro
        </button>

        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white text-[11px] font-bold cursor-pointer">
          U
        </div>
      </div>
    </header>
  );
}
