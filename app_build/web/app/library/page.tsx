'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { api, Note } from '../lib/api';
import { Upload, FileText, Trash2, Eye, LayoutGrid, List, Loader2, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';

function NoteCard({ note, onDelete, index }: { note: Note; onDelete: () => void; index: number }) {
  const [deleting, setDeleting] = useState(false);
  const icons = ['📘', '🔬', '🌿', '📖', '⚗️', '💡'];
  const icon = icons[index % icons.length];
  const gradients = [
    'from-indigo-600 to-purple-700',
    'from-purple-600 to-pink-700',
    'from-cyan-600 to-blue-700',
    'from-amber-600 to-orange-700',
  ];
  const grad = gradients[index % gradients.length];

  async function handleDelete() {
    if (!confirm(`Delete "${note.title}"?`)) return;
    setDeleting(true);
    try { await api.deleteNote(note._id); onDelete(); }
    catch { setDeleting(false); alert('Failed to delete.'); }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0, transition: { delay: index * 0.06 } }}
      className="group bg-[#15151b] border border-[#252530] rounded-xl p-4 flex flex-col hover:border-[#353545] cursor-pointer"
    >
      <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${grad} flex items-center justify-center text-base mb-3 flex-shrink-0`}>
        {icon}
      </div>
      <h3 className="text-[13px] font-semibold text-white mb-1 line-clamp-2 leading-snug">{note.title}</h3>
      <p className="text-[11px] text-[#55556a] mb-3 flex-1">
        {note.total_pages} pages · {note.total_chunks} chunks
      </p>
      <div className="flex items-center justify-between">
        <span className="text-[10px] text-[#44445a]">
          {new Date(note.uploaded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
        </span>
        <div className="flex gap-2.5 opacity-0 group-hover:opacity-100">
          <button className="text-[#7777aa] hover:text-indigo-400 text-[11px] flex items-center gap-1">
            <Eye className="w-3 h-3" /> View
          </button>
          <button onClick={handleDelete} disabled={deleting} className="text-[#7777aa] hover:text-red-400">
            {deleting ? <Loader2 className="w-3 h-3 animate-spin" /> : <Trash2 className="w-3 h-3" />}
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function NoteRow({ note, onDelete, index }: { note: Note; onDelete: () => void; index: number }) {
  const [deleting, setDeleting] = useState(false);

  async function handleDelete() {
    if (!confirm(`Delete "${note.title}"?`)) return;
    setDeleting(true);
    try { await api.deleteNote(note._id); onDelete(); }
    catch { setDeleting(false); alert('Failed to delete.'); }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0, transition: { delay: index * 0.04 } }}
      className="group flex items-center gap-4 p-3.5 bg-[#15151b] border border-[#252530] rounded-xl hover:border-[#353545] cursor-pointer"
    >
      <div className="w-8 h-8 rounded-lg bg-[#1c1c24] border border-[#252530] flex items-center justify-center flex-shrink-0">
        <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-medium text-white truncate">{note.title}</div>
        <div className="text-[11px] text-[#55556a]">{note.total_pages} pages · {note.total_chunks} chunks</div>
      </div>
      <div className="text-[11px] text-[#44445a] flex-shrink-0">
        {new Date(note.uploaded_at).toLocaleDateString()}
      </div>
      <div className="flex gap-2 opacity-0 group-hover:opacity-100 flex-shrink-0">
        <button className="text-[#7777aa] hover:text-indigo-400"><Eye className="w-3.5 h-3.5" /></button>
        <button onClick={handleDelete} disabled={deleting} className="text-[#7777aa] hover:text-red-400">
          {deleting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
        </button>
      </div>
    </motion.div>
  );
}

export default function LibraryPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [gridView, setGridView] = useState(true);
  const [uploadMsg, setUploadMsg] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const loadNotes = useCallback(() => {
    setLoading(true);
    api.getNotes().then(d => setNotes(d.notes ?? [])).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadNotes(); }, [loadNotes]);

  async function handleFile(file: File) {
    if (!file.name.endsWith('.pdf')) { alert('Only PDF files are supported.'); return; }
    setUploading(true);
    setUploadMsg(`Ingesting "${file.name}"...`);
    try {
      await api.uploadPdf(file);
      setUploadMsg('✅ Uploaded successfully!');
      loadNotes();
    } catch {
      setUploadMsg('❌ Upload failed. Please try again.');
    } finally {
      setUploading(false);
      setTimeout(() => setUploadMsg(''), 3000);
    }
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, []);

  return (
    <div className="p-6 max-w-[1100px] mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-[28px] font-bold text-white mb-1">Library</h1>
        <p className="text-[13px] text-[#7777aa]">Your collective intelligence, distilled. Access your uploaded research papers, textbooks, and meeting notes.</p>
      </motion.div>

      <div className="grid grid-cols-3 gap-5 mb-7">
        {/* Upload Zone */}
        <div className="col-span-2">
          <div
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => !uploading && inputRef.current?.click()}
            className={clsx(
              'border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center text-center cursor-pointer',
              dragOver
                ? 'border-indigo-500 bg-indigo-900/10'
                : 'border-[#252530] bg-[#15151b] hover:border-[#353545] hover:bg-[#18181f]'
            )}
          >
            <input ref={inputRef} type="file" accept=".pdf" className="hidden"
              onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
            <div className="w-12 h-12 rounded-2xl bg-[#1c1c24] border border-[#252530] flex items-center justify-center mb-4">
              {uploading
                ? <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
                : <Upload className="w-6 h-6 text-[#55556a]" />
              }
            </div>
            <h3 className="text-[15px] font-semibold text-white mb-1">Ingest New Knowledge</h3>
            <p className="text-[12.5px] text-[#7777aa] mb-4">
              Drag and drop your PDF research or{' '}
              <span className="text-indigo-400 underline underline-offset-2">browse files</span>
            </p>
            <div className="flex gap-2">
              {['PDF', 'TXT'].map(t => (
                <span key={t} className="px-3 py-1 rounded-lg bg-[#1c1c24] border border-[#252530] text-[11.5px] text-[#7777aa] flex items-center gap-1.5">
                  <FileText className="w-3 h-3" /> {t}
                </span>
              ))}
            </div>
            {uploadMsg && (
              <p className="mt-3 text-[12px] text-indigo-300">{uploadMsg}</p>
            )}
          </div>
        </div>

        {/* Quick Insight */}
        <div className="bg-[#15151b] border border-[#252530] rounded-2xl p-5 flex flex-col">
          <div className="text-[10px] text-indigo-400 uppercase tracking-widest font-semibold mb-2">Quick Insight</div>
          <h3 className="text-[14px] font-semibold text-white mb-1.5">Processing Queue</h3>
          <p className="text-[12px] text-[#7777aa] mb-4 flex-1 leading-relaxed">
            System is currently optimized. Ingestion speeds are at 450 pages/min.
          </p>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#1c1c24] border border-[#252530]">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse flex-shrink-0" />
            <span className="text-[11.5px] text-[#7777aa] flex-1">Neural indexing...</span>
            <span className="text-[10px] text-emerald-400 font-semibold uppercase flex-shrink-0">Active</span>
          </div>
        </div>
      </div>

      {/* Notes list */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <h2 className="text-[14px] font-semibold text-white">Recent Synapses</h2>
          <span className="px-2 py-0.5 rounded-full text-[11px] bg-[#1c1c24] border border-[#252530] text-[#7777aa]">
            {notes.length} Notes
          </span>
        </div>
        <div className="flex gap-1">
          <button onClick={() => setGridView(true)}
            className={clsx('p-1.5 rounded-lg', gridView ? 'bg-[#252530] text-white' : 'text-[#55556a] hover:text-white')}>
            <LayoutGrid className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => setGridView(false)}
            className={clsx('p-1.5 rounded-lg', !gridView ? 'bg-[#252530] text-white' : 'text-[#55556a] hover:text-white')}>
            <List className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-[#15151b] border border-[#252530] rounded-xl p-4 animate-pulse h-36" />
          ))}
        </div>
      ) : notes.length === 0 ? (
        <div className="py-16 text-center text-[#44445a]">
          <BookOpen className="w-8 h-8 mx-auto mb-3 opacity-30" />
          <p className="text-[13px]">No notes yet. Upload a PDF to get started!</p>
        </div>
      ) : (
        <div className={clsx(gridView ? 'grid grid-cols-3 gap-4' : 'flex flex-col gap-2')}>
          <AnimatePresence>
            {notes.map((n, i) =>
              gridView
                ? <NoteCard key={n._id} note={n} index={i} onDelete={loadNotes} />
                : <NoteRow key={n._id} note={n} index={i} onDelete={loadNotes} />
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
