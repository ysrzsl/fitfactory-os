import { useState, useRef, useEffect } from 'react';
import { api } from '../api';

interface Msg { role: 'user' | 'assistant'; content: string; }

const CACHE_KEY = 'ffos_chat_msgs';
const DEFAULT: Msg[] = [
  { role: 'assistant', content: '你好！我是 AI 厂长助理 👋\n\n你可以问我订单进度、产线状态、排产、插单模拟等问题。' }
];

function loadCache(): Msg[] {
  try { const d = sessionStorage.getItem(CACHE_KEY); return d ? JSON.parse(d) : [...DEFAULT]; }
  catch { return [...DEFAULT]; }
}

export default function Chat({ showToast: _ }: { showToast?: (m: string) => void }) {
  const [msgs, setMsgs] = useState<Msg[]>(loadCache);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // 每次消息变化写入缓存
  useEffect(() => { sessionStorage.setItem(CACHE_KEY, JSON.stringify(msgs)); }, [msgs]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput('');
    setMsgs(prev => [...prev, { role: 'user', content: q }]);
    setLoading(true);
    try {
      const { reply } = await api.chat.send(q);
      setMsgs(prev => [...prev, { role: 'assistant', content: reply }]);
    } catch {
      setMsgs(prev => [...prev, { role: 'assistant', content: '⚠️ 请求失败，请检查后端是否运行' }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      <h2 className="text-lg font-bold mb-3">💬 AI 厂长助理</h2>
      <div className="flex-1 overflow-auto space-y-2 mb-3">
        {msgs.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap ${
              m.role === 'user'
                ? 'bg-[var(--accent)] text-white rounded-br-md'
                : 'bg-[var(--bg2)] text-[var(--text)] rounded-bl-md border border-[var(--border)]'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-[var(--text3)] text-sm pl-4">思考中...</div>}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 bg-[var(--bg2)] text-[var(--text)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-[var(--accent)] placeholder:text-[var(--text3)]"
          placeholder="输入问题..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
        />
        <button onClick={send} disabled={loading} className="bg-[var(--accent)] text-white px-5 rounded-xl font-bold disabled:opacity-50">
          发送
        </button>
      </div>
    </div>
  );
}
