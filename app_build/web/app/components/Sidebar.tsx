'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  BookOpen,
  Search,
  Sparkles,
  Calendar,
  Settings,
  HelpCircle,
  Plus,
  Brain,
} from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/library', label: 'Library', icon: BookOpen },
  { href: '/search', label: 'Search', icon: Search },
  { href: '/study', label: 'Study Buddy', icon: Sparkles },
  { href: '/planner', label: 'Planner', icon: Calendar },
];

const bottomItems = [
  { href: '/settings', label: 'Settings', icon: Settings },
  { href: '/support', label: 'Support', icon: HelpCircle },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      style={{ width: '220px', minWidth: '220px' }}
      className="flex flex-col h-screen bg-[#111117] border-r border-[#252530] px-3 py-5 flex-shrink-0 overflow-y-auto"
    >
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-2 mb-7">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
          <Brain className="w-3.5 h-3.5 text-white" />
        </div>
        <div className="min-w-0">
          <div className="text-[13px] font-bold text-white leading-tight truncate">NoteFlow AI</div>
          <div className="text-[9px] text-[#55556a] uppercase tracking-widest truncate">Intelligent Learning</div>
        </div>
      </div>

      {/* New Insight Button */}
      <Link href="/library" className="mb-6">
        <div className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-[12px] font-semibold shadow-lg shadow-indigo-900/30 hover:shadow-indigo-700/40 hover:opacity-90 cursor-pointer transition-opacity">
          <Plus className="w-3.5 h-3.5 flex-shrink-0" />
          New Insight
        </div>
      </Link>

      {/* Nav Links */}
      <nav className="flex flex-col gap-0.5 flex-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link key={href} href={href}>
              <div
                className={clsx(
                  'flex items-center gap-2.5 px-3 py-2 rounded-lg text-[12.5px] font-medium cursor-pointer group',
                  active
                    ? 'bg-[#1e1e2e] text-indigo-400'
                    : 'text-[#7777aa] hover:bg-[#18181f] hover:text-[#c0c0d8]'
                )}
              >
                <Icon className={clsx('w-4 h-4 flex-shrink-0', active ? 'text-indigo-400' : 'text-[#444460] group-hover:text-[#8888aa]')} />
                <span className="truncate">{label}</span>
                {active && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0" />
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="flex flex-col gap-0.5 mt-4 pt-4 border-t border-[#252530]">
        {bottomItems.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href}>
            <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-[12.5px] text-[#7777aa] hover:bg-[#18181f] hover:text-[#c0c0d8] cursor-pointer group">
              <Icon className="w-4 h-4 flex-shrink-0 text-[#444460] group-hover:text-[#8888aa]" />
              {label}
            </div>
          </Link>
        ))}

        {/* User profile */}
        <div className="flex items-center gap-2.5 px-3 py-2.5 mt-2 rounded-xl bg-[#18181f] border border-[#252530]">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white text-[11px] font-bold flex-shrink-0">
            U
          </div>
          <div className="min-w-0">
            <div className="text-[12px] font-semibold text-white truncate">User</div>
            <div className="text-[10px] text-[#55556a]">Premium Member</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
