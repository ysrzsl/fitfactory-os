import { useState, useEffect } from 'react';
const API = 'https://fitfactory-os-production.up.railway.app/api';

export default function CostPage() {
  const [costs, setCosts] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [msg, setMsg] = useState('');
  const [calculating, setCalculating] = useState(false);

  const load = async () => {
    const [c,s]=await Promise.all([fetch(`${API}/cost/all`).then(r=>r.json()),fetch(`${API}/cost/summary`).then(r=>r.json())]);
    setCosts(c); setSummary(s);
  };
  useEffect(()=>{load()},[]);

  const calcAll = async () => {
    setCalculating(true); setMsg('正在核算...');
    try {
      await fetch(`${API}/cost/reset`,{method:'POST'});
      const orders = await fetch(`${API}/orders/`).then(r=>r.json());
      for (const o of orders) {
        await fetch(`${API}/cost/calculate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({order_number:o.order_number})});
      }
      setMsg('核算完成');
      load();
    } catch { setMsg('核算失败'); }
    setCalculating(false);
  };

  const calcOne = async (on: string) => {
    await fetch(`${API}/cost/calculate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({order_number:on})});
    load();
  };

  return (<div><h2 className="text-lg font-bold mb-3">💰 成本核算</h2>
    <p className="text-xs text-[var(--text2)] mb-2">
      物料成本 = BOM用量 × 单价 &nbsp;|&nbsp; 人工 = 计件汇总 &nbsp;|&nbsp; 营收 = 售价 × 件数（自动估算）
    </p>

    {summary && summary.count > 0 && (
      <div className="grid grid-cols-4 gap-2 mb-3">
        <div className="card text-center py-2"><div className="text-lg font-bold">¥{summary.total_revenue?.toLocaleString()}</div><div className="text-[10px] text-[var(--text2)]">总营收</div></div>
        <div className="card text-center py-2"><div className="text-lg font-bold">¥{summary.total_cost?.toLocaleString()}</div><div className="text-[10px] text-[var(--text2)]">总成本</div></div>
        <div className={`card text-center py-2 ${summary.total_profit>=0?'alert-green':'alert-red'}`}><div className="text-lg font-bold">¥{summary.total_profit?.toLocaleString()}</div><div className="text-[10px] text-[var(--text2)]">毛利</div></div>
        <div className="card text-center py-2"><div className="text-lg font-bold">{summary.avg_rate}%</div><div className="text-[10px] text-[var(--text2)]">平均毛利率</div></div>
      </div>
    )}

    <button onClick={calcAll} disabled={calculating} className="w-full bg-[var(--accent)] text-white py-2.5 rounded-lg text-sm font-bold mb-3 disabled:opacity-50">
      {calculating ? '核算中...' : '📊 一键核算全部订单'}
    </button>
    {msg && <p className="text-xs text-center mb-2 text-[var(--text2)]">{msg}</p>}

    <div className="space-y-1.5">
      {costs.length===0 && !calculating && <p className="text-[var(--text3)] text-center py-8">点击上方按钮核算成本</p>}
      {costs.map(c=>(
        <div key={c.order_number} className={`card flex items-center justify-between py-2 ${c.gross_profit<0?'alert-red':''}`}>
          <div>
            <div className="text-sm font-bold">{c.order_number}</div>
            <div className="text-[10px] text-[var(--text2)]">营收¥{c.order_amount?.toLocaleString()} · 物料¥{c.material_cost?.toLocaleString()} · 人工¥{c.labor_cost?.toLocaleString()}</div>
          </div>
          <div className="text-right">
            <div className={`text-sm font-bold ${c.gross_profit>=0?'text-[var(--green)]':'text-[var(--red)]'}`}>¥{c.gross_profit?.toLocaleString()}</div>
            <div className="text-[10px] text-[var(--text2)]">毛利率 {c.profit_rate}%</div>
          </div>
        </div>
      ))}
    </div></div>);
}
