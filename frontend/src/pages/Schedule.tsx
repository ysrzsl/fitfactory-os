import { useState } from 'react';
import { api } from '../api';

export default function Schedule({ showToast: _ }: { showToast?: (m: string) => void }) {
  const [tab, setTab] = useState<'auto' | 'sim' | 'conflicts'>('auto');
  const [orderNo, setOrderNo] = useState('');
  const [result, setResult] = useState<any>(null);
  const [simForm, setSimForm] = useState({ style_code: 'NK-2026-003', quantity: 3000, date: '' });
  const [conflicts, setConflicts] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const inputClass = "w-full bg-[var(--bg3)] text-[var(--text)] border border-[var(--border)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--accent)] placeholder:text-[var(--text3)]";

  const run = async () => {
    setLoading(true);
    try { const r = await api.schedule.auto(orderNo); setResult(r); } catch (e: any) { setResult({ error: e.message }); }
    setLoading(false);
  };

  const sim = async () => {
    setLoading(true);
    try { const r = await api.schedule.simulate(simForm.style_code, simForm.quantity, simForm.date); setResult(r); } catch (e: any) { setResult({ error: e.message }); }
    setLoading(false);
  };

  const checkConflicts = async () => {
    const r = await api.schedule.conflicts();
    setConflicts(r);
  };

  return (
    <div>
      <h2 className="text-lg font-bold mb-3">📅 生产排单</h2>
      <div className="flex gap-1.5 mb-3">
        {(['auto','sim','conflicts'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-3 py-1.5 rounded-lg text-xs transition ${tab===t?'bg-[var(--accent)] text-white':'bg-[var(--bg3)] text-[var(--text2)]'}`}>
            {{auto:'⚡ 自动排产',sim:'🔮 插单模拟',conflicts:'⚠️ 撞单'}[t]}
          </button>
        ))}
      </div>

      {tab === 'auto' && (
        <div className="space-y-2">
          <input className={inputClass} placeholder="输入订单号" value={orderNo} onChange={e => setOrderNo(e.target.value)} />
          <button onClick={run} disabled={loading} className="w-full bg-[var(--green)] py-2.5 rounded-lg font-bold text-sm disabled:opacity-50">{loading ? '排产中...' : '🚀 执行自动排产'}</button>
        </div>
      )}

      {tab === 'sim' && (
        <div className="space-y-2">
          <input className={inputClass} placeholder="款号" value={simForm.style_code} onChange={e => setSimForm({...simForm, style_code: e.target.value})} />
          <input className={inputClass} type="number" placeholder="件数" value={simForm.quantity} onChange={e => setSimForm({...simForm, quantity: Number(e.target.value)})} />
          <input className={inputClass} type="date" value={simForm.date} onChange={e => setSimForm({...simForm, date: e.target.value})} />
          <button onClick={sim} disabled={loading} className="w-full bg-[var(--accent2)] py-2.5 rounded-lg font-bold text-sm text-white disabled:opacity-50">{loading ? '模拟中...' : '🔮 模拟插单'}</button>
        </div>
      )}

      {tab === 'conflicts' && (
        <div>
          <button onClick={checkConflicts} className="w-full bg-[var(--red)] py-2.5 rounded-lg font-bold text-sm text-white mb-2">🔍 检测撞单</button>
          {conflicts && (
            conflicts.conflict_count === 0
              ? <div className="card alert-green text-center py-3 text-sm">✅ 无撞单</div>
              : conflicts.conflicts?.map((c: any, i: number) => (
                  <div key={i} className="card alert-red mb-1.5">
                    <div className="text-sm font-bold" style={{color:'var(--red)'}}>{c.line}</div>
                    <div className="text-xs text-[var(--text2)]">{c.order_a} ↔ {c.order_b} · 重叠{c.overlap_days}天</div>
                  </div>
                ))
          )}
        </div>
      )}

      {result && (
        <div className="card mt-3">
          {result.error ? <p className="text-[var(--red)] text-sm">{result.error}</p> : (
            <div className="space-y-1.5 text-sm">
              {result.recommended && (
                <>
                  <div className="text-[var(--green)] font-bold">✅ 推荐: {result.recommended.line}</div>
                  <div className="text-[var(--text2)]">{result.recommended.start_date} → {result.recommended.end_date} · {result.recommended.work_days}天 · {result.recommended.on_time ? '✅ 按时' : '⚠️ 延期'}</div>
                </>
              )}
              {result.affected_orders?.length > 0 && (
                <div className="mt-2 pt-2 border-t border-[var(--border)]">
                  <div className="font-bold" style={{color:'var(--yellow)'}}>⚠️ 影响 {result.affected_count} 张订单</div>
                  {result.affected_orders.map((a: any,i: number) => (
                    <div key={i} className="text-xs text-[var(--text2)]">{a.order_number}: {a.original_end} → {a.new_end} (+{a.delay_days}天)</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
