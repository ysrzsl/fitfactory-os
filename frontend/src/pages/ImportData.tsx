import { useState, useRef } from 'react';
const API = 'https://fitfactory-os-production.up.railway.app/api';
const TABLES = [
  { key: 'orders', label: '📋 订单', template: 'order_number,customer_name,style_code,total_quantity,delivery_date,priority' },
  { key: 'styles', label: '👗 款式', template: 'style_code,style_name,category,standard_capacity(JSON)' },
  { key: 'materials', label: '📦 物料', template: 'material_code,material_name,category,unit,safety_stock,current_stock,supplier_name' },
  { key: 'piecework', label: '💰 计件', template: 'worker_name,order_number,quantity,process_name,unit_price,work_date' },
];
export default function ImportData() {
  const [table, setTable] = useState('orders');
  const [msg, setMsg] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const upload = async () => { const file=fileRef.current?.files?.[0]; if(!file) return; setMsg('导入中...'); const fd=new FormData(); fd.append('file',file); try { const r=await fetch(`${API}/import/${table}`,{method:'POST',body:fd}); const d=await r.json(); if(r.ok){setMsg(`导入成功: ${d.count} 条`); if(navigator.vibrate)navigator.vibrate(50)}else setMsg(`失败: ${d.detail||''}`) } catch { setMsg('网络错误') } };
  return (<div><h2 className="text-lg font-bold mb-3">📥 数据导入</h2><div className="flex gap-2 mb-3 overflow-x-auto">{TABLES.map(t=>(<button key={t.key} onClick={()=>{setTable(t.key);setMsg('')}} className={`px-3 py-1.5 rounded-lg text-xs whitespace-nowrap ${table===t.key?'bg-[var(--accent)] text-white':'bg-[var(--bg3)] text-[var(--text2)]'}`}>{t.label}</button>))}</div><div className="card mb-3"><div className="text-xs text-[var(--text2)] mb-1">CSV 列模板:</div><code className="text-[11px] text-[var(--accent)] break-all">{TABLES.find(t=>t.key===table)?.template}</code><a href={`${API}/import/template/${table}`} download className="inline-block mt-2 text-xs text-[var(--accent)] underline">📥 下载模板 CSV</a></div><div className="drop-zone mb-3" onClick={()=>fileRef.current?.click()}><input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={upload}/><div className="text-2xl mb-1">📁</div><div className="text-sm">点击选择 CSV 或 Excel 文件</div><div className="text-[11px] text-[var(--text3)] mt-1">支持 .csv / .xlsx / .xls</div></div>{msg&&<div className={`card text-center text-sm font-bold ${msg.includes('成功')?'alert-green':msg.includes('失败')||msg.includes('错误')?'alert-red':''}`}>{msg}</div>}</div>);
}
