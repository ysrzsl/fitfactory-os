import { useState, useEffect } from 'react';
import { api } from '../api';

interface Order { order_number: string; customer_name: string; style_code: string; total_quantity: number; delivery_date: string; assigned_line: string | null; start_date: string | null; end_date: string | null; status: string; priority: string; }

const statusBadge = (s: string) => {
  const m: Record<string, string> = { PENDING: 'badge-pending', SCHEDULED: 'badge-scheduled', IN_PROGRESS: 'badge-progress', COMPLETED: 'badge-completed', DELAYED: 'badge-delayed' };
  const t: Record<string, string> = { PENDING: '⏳待排', SCHEDULED: '📅已排', IN_PROGRESS: '🔧在产', COMPLETED: '✅完成', DELAYED: '🚨延期' };
  return <span className={`badge ${m[s] || 'badge-pending'}`}>{t[s] || s}</span>;
};

export default function Orders({ showToast }: { showToast?: (m: string) => void }) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [filter, setFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ order_number: '', customer_name: '', style_code: 'NK-2026-001', total_quantity: 1000, delivery_date: '', priority: 'NORMAL' });

  useEffect(() => { api.orders.list(filter).then(setOrders).catch(() => {}); }, [filter]);

  const submit = async () => {
    await api.orders.create({ ...form, total_quantity: Number(form.total_quantity) });
    setShowForm(false);
    api.orders.list(filter).then(setOrders);
    showToast?.('订单创建成功');
  };

  const inputClass = "w-full bg-[var(--bg3)] text-[var(--text)] rounded-lg p-2.5 text-sm outline-none border border-[var(--border)] focus:border-[var(--accent)] placeholder:text-[var(--text3)]";

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold">📋 订单管理</h2>
        <button onClick={() => setShowForm(!showForm)} className="bg-[var(--accent)] text-white px-3 py-1.5 rounded-lg text-sm font-bold">+ 新增</button>
      </div>

      {showForm && (
        <div className="card mb-3 space-y-2">
          <div><label className="text-[10px] text-[var(--text3)] uppercase mb-0.5 block">订单号 *</label>
          <input className={inputClass} placeholder="如 SO-20260701" value={form.order_number} onChange={e => setForm({...form, order_number: e.target.value})} /></div>
          <div><label className="text-[10px] text-[var(--text3)] uppercase mb-0.5 block">客户名称</label>
          <input className={inputClass} placeholder="如 金狐狸服饰" value={form.customer_name} onChange={e => setForm({...form, customer_name: e.target.value})} /></div>
          <div className="flex gap-2">
            <div className="flex-1"><label className="text-[10px] text-[var(--text3)] uppercase mb-0.5 block">款号</label>
            <input className={inputClass} placeholder="NK-2026-001" value={form.style_code} onChange={e => setForm({...form, style_code: e.target.value})} /></div>
            <div className="w-28"><label className="text-[10px] text-[var(--text3)] uppercase mb-0.5 block">件数</label>
            <input className={inputClass} type="number" value={form.total_quantity} onChange={e => setForm({...form, total_quantity: Number(e.target.value)})} /></div>
          </div>
          <div><label className="text-[10px] text-[var(--text3)] uppercase mb-0.5 block">交期 *（客户要求的交货日期）</label>
          <input className={inputClass} type="date" value={form.delivery_date} onChange={e => setForm({...form, delivery_date: e.target.value})} /></div>
          <button onClick={submit} className="w-full bg-[var(--green)] text-white py-2.5 rounded-lg text-sm font-bold">✅ 创建订单</button>
        </div>
      )}

      <div className="flex gap-1.5 mb-3 overflow-x-auto">
        {[
          {key:'',label:'全部'},
          {key:'PENDING',label:'⏳ 待排产'},
          {key:'SCHEDULED',label:'📅 已排产'},
          {key:'IN_PROGRESS',label:'🔧 生产中'},
          {key:'COMPLETED',label:'✅ 已完成'},
          {key:'DELAYED',label:'🚨 已延期'},
        ].map(s => (
          <button key={s.key} onClick={() => setFilter(s.key)} className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition ${filter === s.key ? 'bg-[var(--accent)] text-white' : 'bg-[var(--bg3)] text-[var(--text2)]'}`}>{s.label}</button>
        ))}
      </div>

      <div className="space-y-2">
        {orders.map(o => (
          <div key={o.order_number} className="card">
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-bold text-sm">{o.order_number}</span>
              {statusBadge(o.status)}
            </div>
            <div className="text-xs text-[var(--text2)] space-y-0.5">
              <div>{o.customer_name} · {o.style_code}</div>
              <div className="flex gap-2">{o.total_quantity}件 · 交期: {o.delivery_date}</div>
              {o.assigned_line && <div className="text-[var(--accent)]">🏭 {o.assigned_line} · {o.start_date} → {o.end_date}</div>}
            </div>
          </div>
        ))}
        {orders.length === 0 && <p className="text-[var(--text3)] text-center py-8">暂无订单</p>}
      </div>
    </div>
  );
}
