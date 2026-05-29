import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Dashboard({ autoRefresh, showToast: _ }: { autoRefresh?: boolean; showToast?: (m: string) => void }) {
  const [data, setData] = useState<any>(null);
  const [delays, setDelays] = useState<any>(null);

  const load = () => {
    api.dashboard.overview().then(setData);
    api.dashboard.delays().then(setDelays);
  };

  useEffect(() => { load(); }, []);
  useEffect(() => {
    if (!autoRefresh) return;
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [autoRefresh]);

  if (!data) return <p className="text-[var(--text2)] text-center py-8">加载中...</p>;

  const s = data.stats;
  const delayedCount = s.delayed || 0;
  const atRiskCount = delays?.at_risk?.length || 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold">📊 生产看板</h2>
        {autoRefresh && <span className="text-[10px] text-[var(--green)] animate-pulse">● 自动刷新中</span>}
      </div>

      {/* 统计卡片 - 紧凑网格 */}
      <div className="grid grid-cols-4 gap-2 mb-3">
        {[
          {l:'总订单',v:s.total_orders},
          {l:'待排',v:s.pending,c:s.pending>3?'stat-warn':''},
          {l:'在产',v:s.in_progress},
          {l:'完成',v:s.completed,c:'stat-ok'},
        ].map(i=>(
          <div key={i.l} className="card text-center py-2">
            <div className={`text-xl font-bold ${i.c||''}`}>{i.v}</div>
            <div className="text-[10px] text-[var(--text2)]">{i.l}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="card text-center py-2">
          <div className="text-lg font-bold">{s.today_output||0}</div>
          <div className="text-[10px] text-[var(--text2)]">今日产量</div>
        </div>
        <div className="card text-center py-2">
          <div className="text-lg font-bold">{s.due_this_week||0}</div>
          <div className="text-[10px] text-[var(--text2)]">本周到期</div>
        </div>
        <div className={`card text-center py-2 ${delayedCount>0?'alert-red':''}`}>
          <div className={`text-lg font-bold ${delayedCount>0?'stat-danger':''}`}>{delayedCount}</div>
          <div className={`text-[10px] ${delayedCount>0?'text-[var(--red)]':'text-[var(--text2)]'}`}>延期</div>
        </div>
      </div>

      {/* 产线 */}
      <h3 className="text-sm font-bold mb-2">🏭 产线</h3>
      <div className="space-y-1.5 mb-3">
        {data.lines?.map((l:any) => (
          <div key={l.line_name} className="card card-hover flex items-center justify-between py-2">
            <div>
              <div className="font-bold text-sm">{l.line_name}</div>
              <div className="text-[10px] text-[var(--text2)]">{l.active_order||'空闲'} · {l.operator_count}人</div>
            </div>
            <span className={`badge ${l.status==='IDLE'?'badge-completed':l.status==='BUSY'?'badge-progress':'badge-delayed'}`}>
              {l.status==='IDLE'?'空闲':l.status==='BUSY'?'忙碌':'维护'}
            </span>
          </div>
        ))}
      </div>

      {/* 延期预警 - 强化红黄 */}
      {delays?.delayed?.length > 0 && (
        <div className="card alert-red mb-2">
          <h3 className="text-sm font-bold mb-1" style={{color:'var(--red)'}}>🚨 已延期 ({delays.delayed.length})</h3>
          {delays.delayed.map((d:any) => (
            <div key={d.order_number} className="text-sm font-bold" style={{color:'var(--red)'}}>{d.order_number} {d.customer}</div>
          ))}
        </div>
      )}
      {atRiskCount > 0 && (
        <div className="card alert-yellow">
          <h3 className="text-sm font-bold mb-1" style={{color:'var(--yellow)'}}>⚠️ 进度落后 ({atRiskCount})</h3>
          {delays.at_risk.map((a:any) => (
            <div key={a.order_number} className="text-sm" style={{color:'var(--yellow)'}}>
              {a.order_number}: 预期{a.expected_rate} / 实际{a.actual_rate}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
