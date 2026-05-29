import { useState, useEffect } from 'react';

export default function PieceWork({ showToast }: { showToast?: (m: string) => void }) {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [workers, setWorkers] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadList = async () => {
    setDetail(null);
    setLoading(true);
    try {
      const r = await fetch(`/api/payroll/monthly?year=${year}&month=${month}`);
      const data = await r.json();
      setWorkers(data.workers || []);
      setSummary(data);
    } catch { showToast?.('加载失败'); }
    setLoading(false);
  };

  const loadDetail = async (name: string) => {
    setLoading(true);
    try {
      const r = await fetch(`/api/payroll/worker/${encodeURIComponent(name)}?year=${year}&month=${month}`);
      setDetail(await r.json());
    } catch { showToast?.('加载失败'); }
    setLoading(false);
  };

  useEffect(() => { loadList(); }, [year, month]);

  const inputClass = "bg-[var(--bg3)] text-[var(--text)] border border-[var(--border)] rounded-lg px-3 py-1.5 text-sm outline-none";

  // 明细视图
  if (detail) {
    return (
      <div>
        <button onClick={() => setDetail(null)} className="text-sm text-[var(--accent)] mb-3 flex items-center gap-1">← 返回列表</button>
        <h2 className="text-lg font-bold mb-3">{detail.worker_name} · {year}年{month}月工资条</h2>

        <div className="card mb-3">
          <div className="text-xs text-[var(--text2)] mb-2">基本信息: {detail.position} · 工号 {detail.worker_id}</div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div><span className="text-[var(--text2)]">底薪</span> <span className="float-right font-bold">¥{detail.base_salary?.toLocaleString()}</span></div>
            <div><span className="text-[var(--text2)]">计件工资</span> <span className="float-right font-bold">¥{detail.piece_total?.toLocaleString()}</span></div>
            <div><span className="text-[var(--text2)]">奖惩</span> <span className={`float-right font-bold ${detail.adj_total >= 0 ? 'text-[var(--green)]' : 'text-[var(--red)]'}`}>{detail.adj_total >= 0 ? '+' : ''}¥{detail.adj_total?.toLocaleString()}</span></div>
            <div><span className="text-[var(--text2)]">社保扣除</span> <span className="float-right font-bold text-[var(--red)]">-¥{detail.social_insurance}</span></div>
          </div>
          <div className="mt-3 pt-2 border-t border-[var(--border)] flex justify-between text-base">
            <span className="font-bold">实发工资</span>
            <span className="font-bold text-[var(--accent)]">¥{detail.net_pay?.toLocaleString()}</span>
          </div>
        </div>

        {/* 计件明细 */}
        {detail.piece_records?.length > 0 && (
          <div className="mb-3">
            <h3 className="text-sm font-bold mb-2">计件明细 ({detail.piece_records.length}条)</h3>
            <div className="card space-y-1 max-h-48 overflow-auto">
              {detail.piece_records.map((p: any, i: number) => (
                <div key={i} className="flex justify-between text-xs text-[var(--text2)]">
                  <span>{p.date} · {p.order} · {p.process} ×{p.qty}</span>
                  <span>¥{p.pay}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 奖惩明细 */}
        {detail.adjustments?.length > 0 && (
          <div>
            <h3 className="text-sm font-bold mb-2">奖惩明细</h3>
            <div className="card space-y-1">
              {detail.adjustments.map((a: any, i: number) => (
                <div key={i} className={`flex justify-between text-xs ${a.amount >= 0 ? 'text-[var(--green)]' : 'text-[var(--red)]'}`}>
                  <span>{a.date} · {a.type} · {a.reason}</span>
                  <span className="font-bold">{a.amount >= 0 ? '+' : ''}¥{a.amount}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // 列表视图
  return (
    <div>
      <h2 className="text-lg font-bold mb-3">💰 计件工资</h2>

      {/* 月份选择 */}
      <div className="flex gap-2 mb-3">
        <select className={inputClass} value={year} onChange={e => setYear(Number(e.target.value))}>
          {[2025, 2026, 2027].map(y => <option key={y} value={y}>{y}年</option>)}
        </select>
        <select className={inputClass} value={month} onChange={e => setMonth(Number(e.target.value))}>
          {Array.from({length:12},(_,i)=>i+1).map(m => <option key={m} value={m}>{m}月</option>)}
        </select>
        {summary && (
          <span className="ml-auto text-xs text-[var(--text2)] self-center">
            {summary.worker_count}人 · 合计 ¥{summary.total_payroll?.toLocaleString()}
          </span>
        )}
      </div>

      {loading && <p className="text-[var(--text3)] text-center py-4">加载中...</p>}

      {/* 人员列表 */}
      <div className="space-y-1.5">
        {workers.map((w, i) => (
          <div key={w.worker_name} className="card card-hover flex items-center justify-between py-2.5 cursor-pointer"
               onClick={() => loadDetail(w.worker_name)}>
            <div className="flex items-center gap-3">
              <span className="text-xs text-[var(--text3)] w-6 text-right">{i+1}</span>
              <div>
                <div className="text-sm font-bold flex items-center gap-2">
                  {w.worker_name}
                  {w.anomaly && <span className="badge badge-delayed text-[10px]">⚠️ 异常</span>}
                </div>
                <div className="text-[10px] text-[var(--text2)]">{w.position} · 计件{w.piece_qty}件 ¥{w.piece_pay?.toLocaleString()}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-bold">¥{w.net_pay?.toLocaleString()}</div>
              <div className={`text-[10px] ${w.deviation_pct > 0 ? 'text-[var(--green)]' : w.deviation_pct < 0 ? 'text-[var(--red)]' : 'text-[var(--text3)]'}`}>
                {w.deviation_pct > 0 ? '+' : ''}{w.deviation_pct}%
              </div>
            </div>
          </div>
        ))}
        {!loading && workers.length === 0 && (
          <p className="text-[var(--text3)] text-center py-8">暂无工资数据，请先录入计件记录和工人信息</p>
        )}
      </div>
    </div>
  );
}
