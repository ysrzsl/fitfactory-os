import { useState, useEffect } from 'react';
const API = 'https://fitfactory-os-production.up.railway.app/api';

export default function CostPage() {
  const [costs, setCosts] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [form, setForm] = useState({ order_number: '', order_amount: '', overhead: '0' });
  const [msg, setMsg] = useState('');
  const load = async () => { const [c,s]=await Promise.all([fetch(`${API}/cost/all`).then(r=>r.json()),fetch(`${API}/cost/summary`).then(r=>r.json())]); setCosts(c); setSummary(s); };
  useEffect(()=>{load()},[]);
  const calc = async () => { const r=await fetch(`${API}/cost/calculate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({order_number:form.order_number,order_amount:Number(form.order_amount),overhead:Number(form.overhead)})}); if(r.ok){setMsg('计算完成');load()}else setMsg('失败'); };
  const ic="bg-[var(--bg3)] text-[var(--text)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm outline-none";

  return (<div><h2 className="text-lg font-bold mb-3">💰 成本核算</h2>
    {summary&&<div className="grid grid-cols-4 gap-2 mb-3"><div className="card text-center py-2"><div className="text-lg font-bold">¥{summary.total_revenue?.toLocaleString()}</div><div className="text-[10px] text-[var(--text2)]">总营收</div></div><div className="card text-center py-2"><div className="text-lg font-bold">¥{summary.total_cost?.toLocaleString()}</div><div className="text-[10px] text-[var(--text2)]">总成本</div></div><div className={`card text-center py-2 ${summary.total_profit>=0?'alert-green':'alert-red'}`}><div className="text-lg font-bold">¥{summary.total_profit?.toLocaleString()}</div><div className="text-[10px] text-[var(--text2)]">毛利</div></div><div className="card text-center py-2"><div className="text-lg font-bold">{summary.avg_rate}%</div><div className="text-[10px] text-[var(--text2)]">平均毛利率</div></div></div>}
    <div className="card mb-3"><h3 className="text-sm font-bold mb-2">快速核算</h3><div className="flex gap-2 mb-2"><input className={`flex-1 ${ic}`} placeholder="订单号" value={form.order_number} onChange={e=>setForm({...form,order_number:e.target.value})}/><input className={`w-24 ${ic}`} placeholder="金额" type="number" value={form.order_amount} onChange={e=>setForm({...form,order_amount:e.target.value})}/></div><button onClick={calc} className="w-full bg-[var(--accent)] text-white py-2 rounded-lg text-sm font-bold">📊 核算成本</button>{msg&&<p className="text-xs mt-1">{msg}</p>}</div>
    <div className="space-y-1.5">{costs.map(c=>(<div key={c.order_number} className={`card flex items-center justify-between py-2 ${c.gross_profit<0?'alert-red':''}`}><div><div className="text-sm font-bold">{c.order_number}</div><div className="text-[10px] text-[var(--text2)]">物料¥{c.material_cost} + 人工¥{c.labor_cost}</div></div><div className="text-right"><div className={`text-sm font-bold ${c.gross_profit>=0?'text-[var(--green)]':'text-[var(--red)]'}`}>¥{c.gross_profit?.toLocaleString()}</div><div className="text-[10px] text-[var(--text2)]">毛利率 {c.profit_rate}%</div></div></div>))}</div></div>);
}
