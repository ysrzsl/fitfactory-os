import { useState, useEffect } from 'react';
const API = 'https://fitfactory-os-production.up.railway.app/api';

export default function CustomerPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [filter, setFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ customer_name: '', level: 'B', contact_person: '', contact_phone: '' });
  const load = () => { fetch(`${API}/customers/`).then(r=>r.json()).then(setCustomers); };
  useEffect(()=>{load()},[]);
  const submit = async () => { await fetch(`${API}/customers/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(form)}); setShowForm(false); load(); };
  const ic="bg-[var(--bg3)] text-[var(--text)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm outline-none";
  return (<div><div className="flex items-center justify-between mb-3"><h2 className="text-lg font-bold">👥 客户管理</h2><button onClick={()=>setShowForm(!showForm)} className="bg-[var(--accent)] text-white px-3 py-1.5 rounded-lg text-sm font-bold">+ 新增</button></div>
    {showForm&&<div className="card mb-3 space-y-2"><input className={ic} placeholder="客户名称 *" value={form.customer_name} onChange={e=>setForm({...form,customer_name:e.target.value})}/><div className="flex gap-2"><select className={ic} value={form.level} onChange={e=>setForm({...form,level:e.target.value})}><option value="A">A 级</option><option value="B">B 级</option><option value="C">C 级</option></select><input className={ic} placeholder="联系人" value={form.contact_person} onChange={e=>setForm({...form,contact_person:e.target.value})}/></div><input className={ic} placeholder="电话" value={form.contact_phone} onChange={e=>setForm({...form,contact_phone:e.target.value})}/><button onClick={submit} className="w-full bg-[var(--green)] text-white py-2 rounded-lg text-sm font-bold">✅ 添加客户</button></div>}
    <div className="flex gap-1.5 mb-3">{['','A','B','C'].map(l=>(<button key={l} onClick={()=>setFilter(l)} className={`px-3 py-1 rounded-full text-xs ${filter===l?'bg-[var(--accent)] text-white':'bg-[var(--bg3)] text-[var(--text2)]'}`}>{l||'全部'}</button>))}</div>
    <div className="space-y-2">{customers.filter(c=>!filter||c.level===filter).map(c=>(<div key={c.customer_name} className="card flex items-center justify-between py-2.5"><div><div className="text-sm font-bold flex items-center gap-2">{c.customer_name} <span className={`badge ${c.level==='A'?'badge-progress':c.level==='B'?'badge-scheduled':'badge-pending'}`}>{c.level}级</span></div><div className="text-[10px] text-[var(--text2)]">{c.contact_person} · {c.contact_phone} · {c.total_orders}单</div></div>{c.outstanding>0&&<span className="text-xs text-[var(--red)] font-bold">欠¥{c.outstanding?.toLocaleString()}</span>}</div>))}</div></div>);
}
