'use client';

import { useEffect, useState } from 'react';
import { api, Activity } from './lib/api';
import { Library, Zap, TrendingUp, ArrowUpRight, BookOpen, Brain, ChevronRight } from 'lucide-react';
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.06, duration: 0.35 } }),
};

function timeAgo(ts: string) {
  const diff = Date.now() - new Date(ts).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 2) return 'Just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function actionIcon(action: string) {
  if (action.includes('upload') || action.includes('ingest')) return <BookOpen className="w-3.5 h-3.5 text-indigo-400" />;
  if (action.includes('plan')) return <Brain className="w-3.5 h-3.5 text-purple-400" />;
  return <Zap className="w-3.5 h-3.5 text-amber-400" />;
}

function actionBadge(action: string) {
  if (action.includes('upload') || action.includes('ingest'))
    return { label: 'New Source', color: 'bg-indigo-900/40 text-indigo-300 border border-indigo-800/40' };
  if (action.includes('plan'))
    return { label: 'Plan Created', color: 'bg-purple-900/40 text-purple-300 border border-purple-800/40' };
  return { label: 'AI Session', color: 'bg-amber-900/40 text-amber-300 border border-amber-800/40' };
}

export default function DashboardPage() {
  const [score, setScore] = useState<number>(82);
  const [noteCount, setNoteCount] = useState<number>(0);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getScore().then(d => setScore(d.score ?? 82)).catch(() => {}),
      api.getNotes().then(d => setNoteCount(d.notes?.length ?? 0)).catch(() => {}),
      api.getActivity().then(d => setActivities(d.activities?.slice(0, 5) ?? [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const chartData = [{ name: 'Score', value: score, fill: 'url(#scoreGrad)' }];

  return (
    <div className="p-6 max-w-[1100px] mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-[26px] font-bold text-white mb-0.5">Welcome back, Architect.</h1>
        <p className="text-[13px] text-[#7777aa]">Your neural network is active. Here is your current cognitive snapshot.</p>
      </motion.div>

      {/* Top Row */}
      <div className="grid grid-cols-3 gap-4 mb-4">

        {/* Score Card */}
        <motion.div custom={0} variants={fadeUp} initial="hidden" animate="show"
          className="col-span-2 bg-[#15151b] border border-[#252530] rounded-2xl p-5">
          <div className="flex items-start justify-between mb-5">
            <div>
              <h2 className="text-[15px] font-semibold text-white">Understanding Score</h2>
              <p className="text-[12px] text-[#7777aa]">Based on quiz performance and synthesis depth.</p>
            </div>
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-900/20 border border-emerald-800/30 px-2.5 py-1 rounded-full whitespace-nowrap">
              <TrendingUp className="w-3 h-3" /> +12% from last week
            </span>
          </div>
          <div className="flex items-center gap-8">
            {/* Donut */}
            <div className="relative flex-shrink-0" style={{ width: 140, height: 140 }}>
              <div style={{ width: 140, height: 140 }}>
                <ResponsiveContainer width={140} height={140}>
                  <RadialBarChart
                    cx="50%" cy="50%"
                    innerRadius="68%" outerRadius="95%"
                    barSize={9}
                    data={chartData}
                    startAngle={90}
                    endAngle={90 - (score / 100) * 360}
                  >
                    <defs>
                      <linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#818cf8" />
                        <stop offset="100%" stopColor="#c084fc" />
                      </linearGradient>
                    </defs>
                    <RadialBar dataKey="value" cornerRadius={8} background={{ fill: '#252530' }} />
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-[30px] font-bold text-white leading-none">{score}</span>
                <span className="text-[9px] text-[#7777aa] uppercase tracking-widest mt-0.5">Optimized</span>
              </div>
            </div>

            {/* Metrics */}
            <div className="flex flex-col gap-4 flex-1 min-w-0">
              <div>
                <div className="flex justify-between text-[11px] mb-1.5">
                  <span className="text-[#7777aa] uppercase tracking-wider">Retention Rate</span>
                  <span className="text-white font-semibold">94%</span>
                </div>
                <div className="h-1.5 rounded-full bg-[#252530]">
                  <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" style={{ width: '94%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-[11px] mb-1.5">
                  <span className="text-[#7777aa] uppercase tracking-wider">Synthesis Speed</span>
                  <span className="text-white font-semibold">1.2s</span>
                </div>
                <div className="h-1.5 rounded-full bg-[#252530]">
                  <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" style={{ width: '65%' }} />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stat cards */}
        <div className="flex flex-col gap-4">
          <motion.div custom={1} variants={fadeUp} initial="hidden" animate="show"
            className="flex-1 bg-[#15151b] border border-[#252530] rounded-2xl p-4 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-900/30 border border-indigo-800/40 flex items-center justify-center flex-shrink-0">
              <Library className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] text-[#7777aa] mb-0.5">Library Growth</div>
              <div className="text-[20px] font-bold text-white leading-tight">{loading ? '—' : `${noteCount}`}</div>
              <div className="text-[11px] text-[#7777aa]">Sources</div>
            </div>
          </motion.div>

          <motion.div custom={2} variants={fadeUp} initial="hidden" animate="show"
            className="flex-1 bg-[#15151b] border border-[#252530] rounded-2xl p-4 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-900/30 border border-amber-800/40 flex items-center justify-center flex-shrink-0">
              <Zap className="w-4 h-4 text-amber-400" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] text-[#7777aa] mb-0.5">Study Sessions</div>
              <div className="text-[20px] font-bold text-white leading-tight">24.5</div>
              <div className="text-[11px] text-[#7777aa]">Hours</div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Recent Activity */}
      <motion.div custom={3} variants={fadeUp} initial="hidden" animate="show"
        className="bg-[#15151b] border border-[#252530] rounded-2xl p-5 mb-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-[14px] font-semibold text-white">Recent Activity</h2>
            <p className="text-[12px] text-[#7777aa]">Your latest interactions with the intelligence engine.</p>
          </div>
          <button className="text-[12px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
            View History <ChevronRight className="w-3 h-3" />
          </button>
        </div>

        <div className="flex flex-col divide-y divide-[#252530]">
          {loading ? (
            [...Array(3)].map((_, i) => (
              <div key={i} className="py-3 flex items-center gap-3 animate-pulse">
                <div className="w-8 h-8 rounded-xl bg-[#252530] flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="h-2.5 bg-[#252530] rounded w-48 mb-2" />
                  <div className="h-2 bg-[#252530] rounded w-32" />
                </div>
              </div>
            ))
          ) : activities.length === 0 ? (
            <p className="py-6 text-center text-[#44445a] text-[13px]">No activity yet. Upload a PDF to get started!</p>
          ) : (
            activities.map((a, i) => {
              const badge = actionBadge(a.action);
              return (
                <div key={a._id ?? i} className="py-3 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-[#1c1c24] border border-[#252530] flex items-center justify-center flex-shrink-0">
                    {actionIcon(a.action)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[13px] font-medium text-white truncate">{a.details}</div>
                    <div className="text-[11px] text-[#55556a]">{a.action}</div>
                  </div>
                  <div className="flex items-center gap-2.5 flex-shrink-0">
                    <span className="text-[11px] text-[#55556a]">{timeAgo(a.timestamp)}</span>
                    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${badge.color}`}>{badge.label}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </motion.div>

      {/* Bottom row */}
      <div className="grid grid-cols-2 gap-4">
        <motion.div custom={4} variants={fadeUp} initial="hidden" animate="show"
          className="bg-gradient-to-br from-[#191928] to-[#15151b] border border-[#252530] rounded-2xl p-5">
          <div className="text-[10px] text-indigo-400 uppercase tracking-widest font-semibold mb-2">Recommended Study</div>
          <h3 className="text-[17px] font-bold text-white mb-2">Advanced Neural Architectures</h3>
          <p className="text-[12.5px] text-[#7777aa] mb-4 leading-relaxed">
            Explore the cutting edge of deep learning model design and optimization techniques.
          </p>
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-[#55556a]">42 min read</span>
            <button className="w-7 h-7 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center">
              <ArrowUpRight className="w-3.5 h-3.5 text-white" />
            </button>
          </div>
        </motion.div>

        <motion.div custom={5} variants={fadeUp} initial="hidden" animate="show"
          className="bg-[#15151b] border border-[#252530] rounded-2xl p-5">
          <h3 className="text-[14px] font-semibold text-white mb-1.5">Network Insights</h3>
          <p className="text-[12.5px] text-[#7777aa] mb-4 leading-relaxed">
            Your knowledge graph is expanding. Keep uploading notes to unlock deeper connections.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#1c1c24] rounded-xl p-3">
              <div className="text-[10px] text-[#55556a] uppercase tracking-wide mb-1">Node Density</div>
              <div className="text-[15px] font-bold text-white">{(noteCount * 12.4).toFixed(1)}K</div>
            </div>
            <div className="bg-[#1c1c24] rounded-xl p-3">
              <div className="text-[10px] text-[#55556a] uppercase tracking-wide mb-1">Cross-links</div>
              <div className="text-[15px] font-bold text-white">{noteCount * 842}</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
