import { useEffect, useMemo, useState } from 'react';
import { api } from './lib/api';

const tabs = ['Dashboard', 'Memory Explorer', 'Ask AI'];

function AuthPanel({ onAuth }) {
  const [isSignup, setIsSignup] = useState(true);
  const [email, setEmail] = useState('demo@memoryvault.ai');
  const [password, setPassword] = useState('Demo@123');
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const fn = isSignup ? api.signup : api.login;
      const data = await fn({ email, password });
      localStorage.setItem('mv_token', data.access_token);
      onAuth();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="mx-auto mt-16 max-w-md rounded-2xl border bg-white p-6 shadow">
      <h1 className="text-2xl font-bold text-slate-800">MemoryVault AI</h1>
      <p className="mt-2 text-sm text-slate-600">Adaptive external brain with smart forgetting</p>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <input className="w-full rounded-lg border p-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input className="w-full rounded-lg border p-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button className="w-full rounded-lg bg-slate-900 py-2 text-white">{isSignup ? 'Sign Up' : 'Login'}</button>
      </form>
      <button className="mt-4 text-sm text-blue-600" onClick={() => setIsSignup((v) => !v)}>
        {isSignup ? 'Already have an account? Login' : 'New user? Sign up'}
      </button>
    </div>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    api.stats().then(setStats);
    api.timeline().then(setTimeline);
  }, []);

  if (!stats) return <p>Loading dashboard...</p>;

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <Card label="Total Memories" value={stats.total_memories} />
        <Card label="High Value Memories" value={stats.high_value_memories} />
        <Card label="Average Score" value={stats.avg_score} />
      </div>
      <div className="rounded-xl border bg-white p-4">
        <h3 className="font-semibold">Proactive Reminders</h3>
        <ul className="mt-2 list-disc pl-6 text-sm text-slate-700">
          {stats.reminders.map((r) => <li key={r}>{r}</li>)}
        </ul>
      </div>
      <div className="rounded-xl border bg-white p-4">
        <h3 className="font-semibold">Activity Timeline</h3>
        <div className="mt-3 space-y-2 text-sm">
          {timeline.map((item) => (
            <div key={`${item.event_type}-${item.id}`} className="rounded border p-2">
              <p className="font-medium">{item.event_type.toUpperCase()}</p>
              <p>{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MemoryExplorer() {
  const [text, setText] = useState('');
  const [response, setResponse] = useState(null);
  const [memories, setMemories] = useState([]);
  const [selectedLinks, setSelectedLinks] = useState([]);

  const load = () => api.listMemories().then(setMemories);
  useEffect(() => {
    load();
  }, []);

  const ingest = async (e) => {
    e.preventDefault();
    const data = await api.ingest({ text });
    setResponse(data);
    setText('');
    load();
  };

  const fetchLinks = async (id) => {
    const links = await api.getLinks(id);
    setSelectedLinks(links);
  };

  return (
    <div className="space-y-4">
      <form onSubmit={ingest} className="rounded-xl border bg-white p-4">
        <h3 className="font-semibold">Memory Ingestion</h3>
        <textarea className="mt-2 w-full rounded border p-2" rows="4" value={text} onChange={(e) => setText(e.target.value)} placeholder="Add memory text..." />
        <button className="mt-2 rounded bg-slate-900 px-4 py-2 text-white">Ingest Memory</button>
      </form>

      {response && (
        <div className="rounded-xl border bg-emerald-50 p-4 text-sm">
          <p><strong>Decision:</strong> {response.decision}</p>
          <p><strong>Reason:</strong> {response.reason}</p>
          <p><strong>Score Breakdown:</strong> importance={response.score_breakdown.importance}, recency={response.score_breakdown.recency}, frequency={response.score_breakdown.frequency}, final={response.score_breakdown.final_score}</p>
        </div>
      )}

      <div className="rounded-xl border bg-white p-4">
        <h3 className="font-semibold">Stored Memories</h3>
        <div className="mt-3 space-y-2 text-sm">
          {memories.map((m) => (
            <div key={m.id} className="rounded border p-2">
              <p className="font-medium">#{m.id} | score {m.score}</p>
              <p>{m.stored_text}</p>
              <p className="text-xs text-slate-500">Keywords: {m.keywords.join(', ')}</p>
              <button className="mt-1 text-blue-600" onClick={() => fetchLinks(m.id)}>View Linked Memories</button>
            </div>
          ))}
        </div>
      </div>

      {selectedLinks.length > 0 && (
        <div className="rounded-xl border bg-white p-4">
          <h3 className="font-semibold">Knowledge Graph Links</h3>
          {selectedLinks.map((link, idx) => (
            <p key={`${link.source_memory_id}-${idx}`} className="text-sm">
              {link.source_memory_id} ↔ {link.target_memory_id} ({link.relation_type}, score: {link.link_score})
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

function AskAI() {
  const [query, setQuery] = useState('What are my top priorities this week?');
  const [result, setResult] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    const data = await api.ask({ query, top_k: 5 });
    setResult(data);
  };

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="rounded-xl border bg-white p-4">
        <h3 className="font-semibold">Ask AI</h3>
        <input className="mt-2 w-full rounded border p-2" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className="mt-2 rounded bg-slate-900 px-4 py-2 text-white">Ask</button>
      </form>
      {result && (
        <div className="rounded-xl border bg-white p-4 text-sm">
          <p><strong>Answer:</strong></p>
          <pre className="whitespace-pre-wrap">{result.answer}</pre>
          <p className="mt-2"><strong>Confidence:</strong> {result.confidence}</p>
          <p className="mt-2"><strong>Source Memories:</strong></p>
          <ul className="list-disc pl-6">
            {result.source_memories.map((m) => <li key={m.id}>#{m.id}: {m.stored_text}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

function Card({ label, value }) {
  return (
    <div className="rounded-xl border bg-white p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-2xl font-bold text-slate-800">{value}</p>
    </div>
  );
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem('mv_token')));
  const [activeTab, setActiveTab] = useState(tabs[0]);

  const Screen = useMemo(() => {
    if (activeTab === 'Dashboard') return Dashboard;
    if (activeTab === 'Memory Explorer') return MemoryExplorer;
    return AskAI;
  }, [activeTab]);

  if (!authenticated) {
    return <AuthPanel onAuth={() => setAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">MemoryVault AI</h1>
          <button
            className="rounded bg-rose-600 px-3 py-1 text-sm text-white"
            onClick={() => {
              localStorage.removeItem('mv_token');
              setAuthenticated(false);
            }}
          >
            Logout
          </button>
        </div>
        <div className="mb-4 flex gap-2">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={`rounded px-4 py-2 text-sm ${activeTab === tab ? 'bg-slate-900 text-white' : 'bg-white border'}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
        <Screen />
      </div>
    </div>
  );
}
