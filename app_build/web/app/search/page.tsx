'use client';

import { useState } from 'react';
import { api, SearchResult } from '../lib/api';
import { Search, Sparkles, BookOpen, Loader2, ArrowRight, Tag } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const suggestions = ['Quantum physics origins', 'Machine learning fundamentals', 'Cellular respiration'];

function highlight(text: string, query: string) {
  if (!query.trim()) return <>{text}</>;
  const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
  return (
    <>
      {parts.map((p, i) =>
        p.toLowerCase() === query.toLowerCase()
          ? <mark key={i} className="bg-indigo-500/25 text-indigo-300 rounded px-0.5 not-italic">{p}</mark>
          : p
      )}
    </>
  );
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [followUp, setFollowUp] = useState('');

  async function doSearch(q = query) {
    if (!q.trim()) return;
    setQuery(q);
    setLoading(true);
    setSearched(true);
    setResults([]);
    try {
      const d = await api.search(q, 5);
      setResults(d.results ?? []);
    } catch { setResults([]); }
    finally { setLoading(false); }
  }

  const topResult = results[0];
  const otherResults = results.slice(1, 4);
  const noteSet = [...new Set(results.map(r => r.note_title))];

  return (
    <div className="p-6 max-w-[1000px] mx-auto">
      {/* Hero */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-[36px] font-bold text-white leading-tight mb-0.5">
          Find deep{' '}
          <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            connections
          </span>
          <br />across your knowledge.
        </h1>
      </motion.div>

      {/* Search bar */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { delay: 0.08 } }}
        className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-[#15151b] border border-[#252530] mb-3.5 focus-within:border-indigo-700">
        <Sparkles className="w-4 h-4 text-indigo-400 flex-shrink-0" />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && doSearch()}
          placeholder="Ask your library anything..."
          className="flex-1 bg-transparent text-white placeholder-[#44445a] text-[14px] outline-none"
        />
        <kbd className="text-[10px] text-[#44445a] border border-[#252530] rounded px-1.5 py-0.5 hidden sm:block">⌘K</kbd>
        <button onClick={() => doSearch()}
          className="w-8 h-8 rounded-xl bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center flex-shrink-0">
          <ArrowRight className="w-3.5 h-3.5 text-white" />
        </button>
      </motion.div>

      {/* Suggestions */}
      {!searched && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1, transition: { delay: 0.15 } }}
          className="flex items-center gap-2 mb-6 flex-wrap">
          <span className="text-[12px] text-[#55556a]">Try searching for:</span>
          {suggestions.map(s => (
            <button key={s} onClick={() => doSearch(s)}
              className="px-2.5 py-1 rounded-full bg-[#1c1c24] border border-[#252530] text-[#7777aa] hover:text-white hover:border-[#353545] text-[11.5px]">
              {s}
            </button>
          ))}
        </motion.div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-3 py-12 justify-center text-[#55556a]">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-[13px]">Searching your knowledge base...</span>
        </div>
      )}

      {/* Results */}
      <AnimatePresence>
        {!loading && searched && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-3 gap-4">

            {/* Main results — 2 cols */}
            <div className="col-span-2 flex flex-col gap-3">
              {results.length === 0 ? (
                <div className="py-14 text-center text-[#44445a]">
                  <Search className="w-7 h-7 mx-auto mb-3 opacity-30" />
                  <p className="text-[13px]">No results found. Try a different query.</p>
                </div>
              ) : (
                <>
                  {/* Top result */}
                  {topResult && (
                    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                      className="bg-[#15151b] border border-[#252530] rounded-2xl p-5">
                      <div className="flex items-center gap-2.5 mb-3">
                        <span className="text-[10px] font-semibold text-indigo-400 bg-indigo-900/30 border border-indigo-800/40 px-2 py-0.5 rounded-full uppercase tracking-wider">
                          AI Semantic Match
                        </span>
                        <span className="text-[11px] text-[#55556a]">
                          {Math.round(topResult.score * 100)}% Relevance
                        </span>
                      </div>
                      <h2 className="text-[17px] font-bold text-white mb-2">{topResult.note_title}</h2>
                      <p className="text-[12.5px] text-[#b0b0c8] leading-relaxed mb-4">
                        {highlight(topResult.chunk_text.slice(0, 350) + '...', query)}
                      </p>
                      <div className="flex gap-4">
                        <button className="text-[12px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5">
                          <BookOpen className="w-3 h-3" /> View Full Note
                        </button>
                        <button className="text-[12px] text-[#7777aa] hover:text-white flex items-center gap-1.5">
                          <Tag className="w-3 h-3" /> Save Insight
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {/* Other results */}
                  {otherResults.length > 0 && (
                    <div className="grid grid-cols-3 gap-3">
                      {otherResults.map((r, i) => (
                        <motion.div key={i}
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0, transition: { delay: 0.08 + i * 0.05 } }}
                          className="bg-[#15151b] border border-[#252530] rounded-xl p-3.5 hover:border-[#353545] cursor-pointer">
                          <span className="text-[9px] font-bold text-[#55556a] uppercase tracking-widest">Match 0{i + 2}</span>
                          <h3 className="text-[12.5px] font-semibold text-white mt-1 mb-1.5 line-clamp-1">{r.note_title}</h3>
                          <p className="text-[11px] text-[#7777aa] line-clamp-3 leading-relaxed">
                            {highlight(`"${r.chunk_text.slice(0, 100)}..."`, query)}
                          </p>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Sidebar — 1 col */}
            <div className="flex flex-col gap-3">
              <div className="bg-[#15151b] border border-[#252530] rounded-2xl p-4">
                <div className="text-[10px] text-[#55556a] uppercase tracking-widest font-semibold mb-3">Related Sources</div>
                {noteSet.slice(0, 4).map((n, i) => (
                  <div key={i} className="flex items-center gap-2.5 py-2.5 border-b border-[#252530] last:border-0">
                    <div className="w-6 h-6 rounded-lg bg-[#1c1c24] flex items-center justify-center flex-shrink-0">
                      <BookOpen className="w-3 h-3 text-indigo-400" />
                    </div>
                    <div className="text-[12px] font-medium text-white truncate">{n}</div>
                  </div>
                ))}
                {noteSet.length === 0 && (
                  <p className="text-[11px] text-[#44445a]">No related sources found.</p>
                )}
              </div>

              <div className="bg-[#15151b] border border-[#252530] rounded-2xl p-4">
                <div className="text-[10px] text-[#55556a] uppercase tracking-widest font-semibold mb-3">Knowledge Cluster</div>
                <div className="flex flex-wrap gap-1.5">
                  {query.split(' ').filter(w => w.length > 3).slice(0, 4).map((w, i) => (
                    <span key={i} className="px-2 py-1 rounded-full bg-[#1c1c24] border border-[#252530] text-[11px] text-[#7777aa] hover:text-white cursor-pointer">
                      {w}
                    </span>
                  ))}
                  {['Deep Learning', 'Research'].map((w, i) => (
                    <span key={i} className="px-2 py-1 rounded-full bg-[#1c1c24] border border-[#252530] text-[11px] text-[#7777aa] hover:text-white cursor-pointer">
                      {w}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sticky follow-up */}
      {searched && !loading && results.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.3 } }}
          className="fixed bottom-5 left-1/2 -translate-x-1/2 w-full max-w-xl px-4 z-30"
        >
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-[#1c1c24] border border-[#252530] shadow-2xl shadow-black/50">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
            <input value={followUp} onChange={e => setFollowUp(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && followUp.trim()) { doSearch(followUp); setFollowUp(''); } }}
              placeholder="Ask a follow-up question..."
              className="flex-1 bg-transparent text-white placeholder-[#44445a] text-[13px] outline-none" />
            <button onClick={() => { if (followUp.trim()) { doSearch(followUp); setFollowUp(''); } }}
              className="w-7 h-7 rounded-xl bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center flex-shrink-0">
              <ArrowRight className="w-3 h-3 text-white" />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
