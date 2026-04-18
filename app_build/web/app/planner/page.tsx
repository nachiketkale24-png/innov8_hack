'use client';

import { useEffect, useState } from 'react';
import { api, Plan } from '../lib/api';
import { Sparkles, Zap, TrendingUp, Calendar, Loader2, Lock, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';

const timeframes = ['1 Week', '2 Weeks', '1 Month', '3 Months', 'Flexible'];
const intensities = ['Casual', 'Moderate', 'Intensive'];

export default function PlannerPage() {
  const [goal, setGoal] = useState('');
  const [timeframe, setTimeframe] = useState('2 Weeks');
  const [intensity, setIntensity] = useState('Casual');
  const [loading, setLoading] = useState(false);
  const [activePlan, setActivePlan] = useState<Plan | null>(null);

  useEffect(() => {
    api.getPlans().then(d => {
      if (d.plans?.length > 0) setActivePlan(d.plans[0]);
    }).catch(() => {});
  }, []);

  async function generate() {
    if (!goal.trim()) { alert('Please enter a goal.'); return; }
    setLoading(true);
    try {
      const d = await api.createPlan(goal, timeframe);
      setActivePlan(d.plan);
    } catch (e: unknown) {
      alert(`Error: ${e instanceof Error ? e.message : 'Failed to generate plan.'}`);
    } finally { setLoading(false); }
  }

  const roadmap = activePlan?.roadmap ?? [];

  return (
    <div className="p-6 max-w-[1100px] mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-[26px] font-bold text-white mb-1">Learning Planner</h1>
        <p className="text-[13px] text-[#7777aa] max-w-xl">
          Map out your path to mastery. Define your goals, set your timeframe, and let NoteFlow AI architect your intelligence roadmap.
        </p>
      </motion.div>

      <div className="flex gap-5">
        {/* Left — Form, fixed width */}
        <div className="flex flex-col gap-4" style={{ width: 300, minWidth: 300 }}>
          <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
            className="bg-[#15151b] border border-[#252530] rounded-2xl p-5">
            <div className="text-[10px] text-indigo-400 uppercase tracking-widest font-semibold mb-3">Primary Goal</div>
            <textarea
              value={goal}
              onChange={e => setGoal(e.target.value)}
              placeholder="e.g. Master Neural Network fundamentals and build a transformer from scratch"
              rows={4}
              className="w-full bg-[#1c1c24] border border-[#252530] rounded-xl p-3 text-[12.5px] text-white placeholder-[#44445a] outline-none resize-none focus:border-indigo-700 leading-relaxed"
            />

            <div className="grid grid-cols-2 gap-2.5 mt-3">
              <div>
                <label className="text-[10px] text-[#55556a] uppercase tracking-wider block mb-1.5">Timeframe</label>
                <div className="relative">
                  <select value={timeframe} onChange={e => setTimeframe(e.target.value)}
                    className="w-full appearance-none bg-[#1c1c24] border border-[#252530] rounded-lg px-3 py-2 text-[12.5px] text-white outline-none focus:border-indigo-700 cursor-pointer">
                    {timeframes.map(t => <option key={t}>{t}</option>)}
                  </select>
                  <ChevronDown className="absolute right-2 top-2.5 w-3.5 h-3.5 text-[#55556a] pointer-events-none" />
                </div>
              </div>
              <div>
                <label className="text-[10px] text-[#55556a] uppercase tracking-wider block mb-1.5">Intensity</label>
                <div className="relative">
                  <select value={intensity} onChange={e => setIntensity(e.target.value)}
                    className="w-full appearance-none bg-[#1c1c24] border border-[#252530] rounded-lg px-3 py-2 text-[12.5px] text-white outline-none focus:border-indigo-700 cursor-pointer">
                    {intensities.map(i => <option key={i}>{i}</option>)}
                  </select>
                  <ChevronDown className="absolute right-2 top-2.5 w-3.5 h-3.5 text-[#55556a] pointer-events-none" />
                </div>
              </div>
            </div>

            <button
              onClick={generate}
              disabled={loading}
              className="w-full mt-4 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-[13px] shadow-lg shadow-indigo-900/30 disabled:opacity-60 hover:opacity-90"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {loading ? 'Generating...' : 'Generate Roadmap'}
            </button>
          </motion.div>

          {/* AI Tip */}
          <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0, transition: { delay: 0.1 } }}
            className="bg-[#15151b] border border-[#252530] rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[12.5px] font-semibold text-white">AI Optimizer Tip</span>
            </div>
            <p className="text-[12px] text-[#7777aa] leading-relaxed">
              Users with goals similar to yours have a 40% higher completion rate when setting a 3-month timeframe for deep technical concepts.
            </p>
          </motion.div>
        </div>

        {/* Right — Roadmap */}
        <div className="flex-1 min-w-0 flex flex-col gap-4">
          {!activePlan && !loading ? (
            <div className="flex-1 flex items-center justify-center py-20">
              <div className="text-center text-[#44445a]">
                <Sparkles className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p className="text-[13px]">Enter your goal and click Generate Roadmap to get started.</p>
              </div>
            </div>
          ) : (
            <>
              {/* Plan title */}
              {activePlan && !loading && (
                <div className="flex items-center gap-2">
                  <span className="text-[12.5px] text-[#7777aa]">Active Roadmap:</span>
                  <span className="text-[12.5px] font-semibold text-indigo-400 truncate">{activePlan.goal}</span>
                </div>
              )}

              {/* Skeleton */}
              {loading && (
                <div className="flex flex-col gap-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="bg-[#15151b] border border-[#252530] rounded-xl p-5 animate-pulse">
                      <div className="h-3.5 bg-[#252530] rounded w-40 mb-3" />
                      <div className="h-2.5 bg-[#252530] rounded w-full mb-2" />
                      <div className="h-2.5 bg-[#252530] rounded w-3/4" />
                    </div>
                  ))}
                </div>
              )}

              {/* Roadmap */}
              {!loading && roadmap.length > 0 && (
                <div className="relative flex flex-col gap-3">
                  {/* Vertical line */}
                  <div className="absolute left-[15px] top-8 bottom-8 w-px bg-[#252530]" />

                  <AnimatePresence>
                    {roadmap.map((week, i) => {
                      const isLocked = i >= 2 && roadmap.length > 3;
                      return (
                        <motion.div key={i}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0, transition: { delay: i * 0.08 } }}
                          className={clsx(
                            'relative flex gap-3.5 bg-[#15151b] border rounded-xl p-4',
                            isLocked ? 'border-[#1e1e26] opacity-55' : 'border-[#252530] hover:border-[#353545]'
                          )}>
                          <div className={clsx(
                            'w-7 h-7 rounded-full flex items-center justify-center text-[12px] font-bold flex-shrink-0 z-10',
                            isLocked
                              ? 'bg-[#252530] text-[#55556a]'
                              : 'bg-indigo-900/50 border border-indigo-700/50 text-indigo-300'
                          )}>
                            {i + 1}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2 mb-1.5">
                              <h3 className={clsx('font-semibold text-[13px] leading-snug', isLocked ? 'text-[#55556a]' : 'text-white')}>
                                {week.title}
                              </h3>
                              <span className="text-[10px] text-[#55556a] bg-[#1c1c24] border border-[#252530] px-2 py-0.5 rounded-full flex-shrink-0 whitespace-nowrap">
                                Week {week.week}
                              </span>
                            </div>
                            {isLocked ? (
                              <div className="flex items-center gap-1.5 text-[11.5px] text-[#55556a]">
                                <Lock className="w-3 h-3" />
                                <span>Unlocks after completing previous phases...</span>
                              </div>
                            ) : (
                              <>
                                <p className="text-[12px] text-[#7777aa] mb-2.5 leading-relaxed line-clamp-2">
                                  {week.tasks.join('. ')}
                                </p>
                                <div className="flex flex-wrap gap-1.5">
                                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#1c1c24] border border-[#252530] text-[#7777aa]">
                                    {week.tasks.length} Tasks
                                  </span>
                                  {week.linked_note_ids.length > 0 && (
                                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#1c1c24] border border-[#252530] text-[#7777aa]">
                                      {week.linked_note_ids.length} Notes Linked
                                    </span>
                                  )}
                                </div>
                              </>
                            )}
                          </div>
                        </motion.div>
                      );
                    })}
                  </AnimatePresence>
                </div>
              )}

              {/* Velocity cards */}
              {!loading && activePlan && (
                <div className="grid grid-cols-2 gap-3 mt-1">
                  <div className="bg-[#15151b] border border-[#252530] rounded-xl p-4">
                    <div className="text-[10px] text-[#55556a] uppercase tracking-wider mb-1">Current Velocity</div>
                    <div className="text-[18px] font-bold text-white">
                      1.2 <span className="text-[12px] text-[#7777aa] font-normal">Modules / day</span>
                    </div>
                    <div className="mt-2 h-1 rounded-full bg-[#252530]">
                      <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" />
                    </div>
                    <div className="flex items-center gap-1 mt-2">
                      <TrendingUp className="w-3 h-3 text-emerald-400" />
                      <span className="text-[10.5px] text-emerald-400">On track</span>
                    </div>
                  </div>
                  <div className="bg-[#15151b] border border-[#252530] rounded-xl p-4">
                    <div className="text-[10px] text-[#55556a] uppercase tracking-wider mb-1">Completion ETA</div>
                    <div className="text-[15px] font-bold text-white">
                      {new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </div>
                    <div className="flex items-center gap-1 mt-2">
                      <Calendar className="w-3 h-3 text-indigo-400" />
                      <span className="text-[10.5px] text-[#7777aa]">3 days ahead of schedule</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
