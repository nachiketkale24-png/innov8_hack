'use client';

import { useEffect, useState } from 'react';
import { api, Note } from '../lib/api';
import { BookOpen, Sparkles, Lightbulb, HelpCircle, Loader2, ArrowRight, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';

type Action = 'summarize' | 'simplify' | 'revise';

type ActionConfig = {
  label: string;
  icon: React.ReactNode;
  fn: (note_id: string, batch: number) => Promise<{ note_id: string; type: string; content: string; start_page: number; end_page: number; total_pages: number; has_next: boolean }>;
};

const actionConfig: { [K in Action]: ActionConfig } = {
  summarize: { label: 'Summarize', icon: <BookOpen className="w-3.5 h-3.5" />, fn: api.summarize },
  simplify: { label: 'Explain Simply', icon: <Lightbulb className="w-3.5 h-3.5" />, fn: api.simplify },
  revise: { label: 'Generate Quiz', icon: <HelpCircle className="w-3.5 h-3.5" />, fn: api.revise },
};

const catColors: { [key: string]: string } = {
  PHYSICS: 'bg-blue-900/40 text-blue-300',
  HISTORY: 'bg-amber-900/40 text-amber-300',
  BIOLOGY: 'bg-emerald-900/40 text-emerald-300',
  LITERATURE: 'bg-purple-900/40 text-purple-300',
  DEFAULT: 'bg-indigo-900/40 text-indigo-300',
};

function getCat(title: string) {
  const t = title.toUpperCase();
  for (const k of Object.keys(catColors)) if (t.includes(k)) return k;
  return 'DEFAULT';
}

export default function StudyPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState<Action | null>(null);
  const [currentBatch, setCurrentBatch] = useState(0);
  const [startPage, setStartPage] = useState(0);
  const [endPage, setEndPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNextBatch, setHasNextBatch] = useState(false);
  const [followUp, setFollowUp] = useState('');

  useEffect(() => {
    api.getNotes().then(d => setNotes(d.notes ?? []));
  }, []);

  async function runAction(action: Action) {
    if (!selectedNote) { alert('Please select a note first.'); return; }
    setLoading(true);
    setActiveAction(action);
    setResult('');
    setCurrentBatch(0);
    try {
      const d = await actionConfig[action].fn(selectedNote._id, 0);
      setResult(d.content ?? 'No response from AI.');
      setStartPage(d.start_page);
      setEndPage(d.end_page);
      setTotalPages(d.total_pages);
      setHasNextBatch(d.has_next);
    } catch (e: unknown) {
      setResult(`Error: ${e instanceof Error ? e.message : 'Something went wrong.'}`);
    } finally { setLoading(false); }
  }

  async function loadNextPages() {
    if (!selectedNote || !activeAction) return;
    setLoading(true);
    try {
      const d = await actionConfig[activeAction].fn(selectedNote._id, currentBatch + 1);
      setResult(prev => prev + '\n\n--- PAGES ' + d.start_page + '-' + d.end_page + ' ---\n\n' + (d.content ?? ''));
      setCurrentBatch(currentBatch + 1);
      setStartPage(d.start_page);
      setEndPage(d.end_page);
      setHasNextBatch(d.has_next);
    } catch (e: unknown) {
      alert(`Error loading next pages: ${e instanceof Error ? e.message : 'Something went wrong.'}`);
    } finally { setLoading(false); }
  }

  return (
    <div className="flex overflow-hidden" style={{ height: 'calc(100vh - 52px)' }}>

      {/* Left panel */}
      <div style={{ width: 280, minWidth: 280 }} className="flex flex-col border-r border-[#252530] overflow-hidden bg-[#111117]">
        <div className="p-4 border-b border-[#252530] flex-shrink-0">
          <h2 className="text-[14px] font-semibold text-white">Select a Note</h2>
          <p className="text-[11.5px] text-[#7777aa]">Choose a source for your AI session</p>
        </div>
        <div className="flex-1 overflow-y-auto p-2.5 flex flex-col gap-2">
          {notes.length === 0 ? (
            <p className="text-center text-[#44445a] text-[12px] py-8 px-4">No notes yet. Upload a PDF first.</p>
          ) : (
            notes.map((n, i) => {
              const cat = getCat(n.title);
              const color = catColors[cat];
              const active = selectedNote?._id === n._id;
              const timeLabels = ['2m ago', '4h ago', 'Yesterday', '3 days ago', '1 week ago'];
              return (
                <div key={n._id}
                  onClick={() => { setSelectedNote(n); setResult(''); setActiveAction(null); }}
                  className={clsx(
                    'p-3.5 rounded-xl cursor-pointer border',
                    active
                      ? 'bg-[#1a1a2a] border-indigo-700/50'
                      : 'bg-[#15151b] border-[#252530] hover:border-[#353545]'
                  )}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${color}`}>
                      {cat === 'DEFAULT' ? 'Note' : cat}
                    </span>
                    <span className="text-[10px] text-[#55556a]">{timeLabels[i % timeLabels.length]}</span>
                  </div>
                  <h3 className="text-[12.5px] font-semibold text-white mb-1 line-clamp-2 leading-snug">{n.title}</h3>
                  <p className="text-[11px] text-[#55556a] line-clamp-2 leading-relaxed">
                    {n.total_pages} pages · {n.total_chunks} chunks indexed
                  </p>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 min-w-0 flex flex-col overflow-hidden">
        {!selectedNote ? (
          <div className="flex-1 flex items-center justify-center text-center p-10">
            <div>
              <div className="w-14 h-14 rounded-2xl bg-[#1c1c24] border border-[#252530] flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-7 h-7 text-indigo-400" />
              </div>
              <h2 className="text-[18px] font-semibold text-white mb-1.5">AI Study Buddy</h2>
              <p className="text-[13px] text-[#55556a]">Select a note from the left panel to begin your AI session.</p>
            </div>
          </div>
        ) : (
          <>
            {/* Workspace header */}
            <div className="px-6 py-4 border-b border-[#252530] flex items-start justify-between gap-4 flex-shrink-0">
              <div className="min-w-0">
                <div className="text-[10px] text-[#55556a] uppercase tracking-widest mb-1">
                  Workspace / {selectedNote.title.split(' ').slice(0, 3).join(' ').toUpperCase()}
                </div>
                <h1 className="text-[22px] font-bold text-white leading-snug">
                  Digital <span className="text-indigo-400">Architect</span>
                </h1>
              </div>
              <div className="flex flex-col gap-2 flex-shrink-0">
                {(Object.entries(actionConfig) as [Action, ActionConfig][]).map(([key, cfg]) => (
                  <button key={key} onClick={() => runAction(key)}
                    disabled={loading}
                    className={clsx(
                      'flex items-center gap-2 px-3.5 py-2 rounded-xl border text-[12.5px] font-medium',
                      activeAction === key && !loading
                        ? 'bg-indigo-900/30 border-indigo-700/50 text-indigo-300'
                        : 'bg-[#1c1c24] border-[#252530] text-white hover:border-[#353545]'
                    )}>
                    {cfg.icon}
                    {cfg.label}
                    {loading && activeAction === key && <Loader2 className="w-3 h-3 animate-spin ml-1" />}
                  </button>
                ))}
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                <span className="text-[10.5px] text-indigo-400 font-semibold uppercase tracking-wider">AI Synthesis Active</span>
              </div>

              <AnimatePresence mode="wait">
                {loading ? (
                  <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="flex flex-col gap-2.5">
                    {[100, 85, 90, 70].map((w, i) => (
                      <div key={i} className="h-2.5 rounded bg-[#252530] animate-pulse" style={{ width: `${w}%` }} />
                    ))}
                  </motion.div>
                ) : result ? (
                  <motion.div key="result" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
                    <div className="text-[13px] text-[#c0c0d0] leading-relaxed whitespace-pre-wrap mb-5">{result}</div>
                    
                    {/* Pagination info */}
                    {totalPages > 0 && (
                      <div className="flex items-center justify-between mb-4 p-3 bg-[#1c1c24] border border-[#252530] rounded-xl">
                        <span className="text-[11px] text-[#7777aa]">
                          Viewing pages <span className="text-white font-semibold">{startPage}–{endPage}</span> of <span className="text-white font-semibold">{totalPages}</span> pages
                        </span>
                        {hasNextBatch && (
                          <button
                            onClick={loadNextPages}
                            disabled={loading}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-[11px] font-medium"
                          >
                            {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <ArrowRight className="w-3 h-3" />}
                            Next Pages
                          </button>
                        )}
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 gap-3 mt-4">
                      {[
                        { icon: <Zap className="w-3.5 h-3.5 text-indigo-400" />, title: 'Key Concept', body: 'Main insight extracted from the AI analysis.' },
                        { icon: <Sparkles className="w-3.5 h-3.5 text-purple-400" />, title: 'AI Observation', body: 'Cross-referenced with your other notes for deeper context.' },
                      ].map((c, i) => (
                        <div key={i} className="bg-[#1c1c24] border border-[#252530] rounded-xl p-3.5">
                          {c.icon}
                          <div className="text-[12.5px] font-semibold text-white mt-2 mb-1">{c.title}</div>
                          <div className="text-[11.5px] text-[#7777aa] leading-relaxed">{c.body}</div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                ) : (
                  <motion.div key="placeholder" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <h2 className="text-[20px] font-bold text-white mb-2">{selectedNote.title}</h2>
                    <p className="text-[13px] text-[#7777aa] leading-relaxed mb-2">
                      This note has <span className="text-white">{selectedNote.total_pages} pages</span> and{' '}
                      <span className="text-white">{selectedNote.total_chunks} knowledge chunks</span> indexed.
                    </p>
                    <p className="text-[13px] text-[#55556a]">
                      Use the action buttons on the right to summarize, simplify, or generate quiz questions.
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Follow-up bar */}
            <div className="px-5 py-3.5 border-t border-[#252530] flex-shrink-0">
              <div className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-[#1c1c24] border border-[#252530] focus-within:border-indigo-700">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
                <input value={followUp} onChange={e => setFollowUp(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && followUp.trim() && selectedNote) {
                      setFollowUp('');
                      alert('Follow-up questions are coming soon! For now, use the action buttons to re-analyze this note.');
                    }
                  }}
                  placeholder="Follow-up questions coming soon..."
                  disabled={loading}
                  className="flex-1 bg-transparent text-white placeholder-[#44445a] text-[12.5px] outline-none disabled:opacity-50" />
                <button onClick={() => {
                  if (followUp.trim() && selectedNote) {
                    setFollowUp('');
                    alert('Follow-up questions are coming soon! For now, use the action buttons to re-analyze this note.');
                  }
                }}
                  disabled={!followUp.trim() || loading || !selectedNote}
                  className="w-7 h-7 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 flex items-center justify-center flex-shrink-0">
                  <ArrowRight className="w-3 h-3 text-white" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
