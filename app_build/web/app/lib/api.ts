const BASE_URL = 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  return res.json();
}

export const api = {
  // Dashboard
  getScore: () => request<{ score: number; metrics: Record<string, number> }>('/api/score'),
  getActivity: () => request<{ activities: Activity[] }>('/api/activity'),

  // Library / Notes
  getNotes: () => request<{ notes: Note[] }>('/api/notes'),
  getNote: (id: string) => request<{ note: Note }>(`/api/notes/${id}`),
  deleteNote: (id: string) =>
    request(`/api/notes/${id}`, { method: 'DELETE', headers: {} }),
  uploadPdf: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE_URL}/api/ingest/pdf`, { method: 'POST', body: form }).then(r => r.json());
  },

  // Search
  search: (query: string, top_k = 5) =>
    request<{ results: SearchResult[] }>('/api/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k }),
    }),

  // Suggestions
  summarize: (text: string) =>
    request<{ result: string }>('/api/suggest/summarize', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),
  simplify: (text: string) =>
    request<{ result: string }>('/api/suggest/simplify', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),
  revise: (text: string) =>
    request<{ result: string }>('/api/suggest/revise', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),

  // Planner
  createPlan: (goal: string, timeframe: string) =>
    request<{ status: string; plan: Plan }>('/api/planner/create', {
      method: 'POST',
      body: JSON.stringify({ goal, timeframe }),
    }),
  getPlans: () => request<{ plans: Plan[] }>('/api/planner'),
};

// ── Types ────────────────────────────────────────────────

export interface Note {
  _id: string;
  title: string;
  total_pages: number;
  total_chunks: number;
  created_at: string;
  content?: string;
}

export interface Activity {
  _id: string;
  action: string;
  details: string;
  timestamp: string;
  note_id?: string;
}

export interface SearchResult {
  chunk_text: string;
  note_title: string;
  note_id: string;
  score: number;
}

export interface PlanWeek {
  week: number;
  title: string;
  tasks: string[];
  linked_note_ids: string[];
}

export interface Plan {
  _id: string;
  goal: string;
  roadmap: PlanWeek[];
  created_at: string;
}
