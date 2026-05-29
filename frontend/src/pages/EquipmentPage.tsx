import { useState, useEffect } from 'react';

export default function EquipmentPage() {
  const [equips, setEquips] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [filter, setFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [maintForm, setMaintForm] = useState({ equip_code: '', record_type: 'MAINTAIN', description: '', cost: '0', technician: '', record_date: '', downtime_hours: '0' });
  const [maintList, setMaintList] = useState<any[]>([]);
  const [showMaintFor, setShowMaintFor] = useState('');

  const load = async () => {
    const [e, a] = await Promise.all([
      fetch('/api/equipment/').then(r => r.json()),
      fetch('/api/equipment/alerts?days=7').then(r => r.json()),
    ]);
    setEquips(e); setAlerts(a);
  };

  useEffect(() => { load(); }, []);

  const submitMaint = async () => {
    await fetch('/api/equipment/maintenance', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...maintForm, cost: Number(maintForm.cost), downtime_hours: Number(maintForm.downtime_hours) }),
    });
    setShowForm(false); load();
  };

  const viewMaint = async (code: string) => {
    setShowMaintFor(code);
    const r = await fetch(`/api/equipment/maintenance/${code}?limit=10`);
    setMaintList(await r.json());
  };

  const inputClass = "bg-[var(--bg3)] text-[var(--text)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm outline-none";
  const types = ['', '平缝机', '包缝机', '熨烫台', '裁床', '其他'];

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold">🔧 设备管理</h2>
        <button onClick={() => setShowForm(true)} className="bg-[var(--accent)] text-white px-3 py-1.5 rounded-lg text-sm font-bold">+ 维保记录</button>
      </div>

      {/* 保养预警 */}
      {alerts.length > 0 && (
        <div className="card alert-red mb-3">
          <h3 className="text-sm font-bold mb-1" style={{color:'var(--red)'}}>⚠️ 保养到期 ({alerts.length})</h3>
          {alerts.map(a => <div key={a.equip_code} className="text-xs text-[var(--red)]">{a.equip_name}({a.equip_code}) · {a.overdue?'已逾期':'即将到期'} · {a.due_date}</div>)}
        </div>
      )}

      {/* 类型筛选 */}
      <div className="flex gap-1.5 mb-3 overflow-x-auto">
        {types.map(t => (
          <button key={t} onClick={() => setFilter(t)} className={`px-3 py-1 rounded-full text-xs whitespace-nowrap ${filter===t?'bg-[var(--accent)] text-white':'bg-[var(--bg3)] text-[var(--text2)]'}`}>{t||'全部'}</button>
        ))}
      </div>

      {/* 维保表单 */}
      {showForm && (
        <div className="card mb-3 space-y-2">
          <input className={inputClass} placeholder="设备编号" value={maintForm.equip_code} onChange={e => setMaintForm({...maintForm, equip_code: e.target.value})} />
          <select className={inputClass} value={maintForm.record_type} onChange={e => setMaintForm({...maintForm, record_type: e.target.value})}>
            <option value="MAINTAIN">🛢️ 保养</option>
            <option value="REPAIR">🔧 维修</option>
          </select>
          <input className={inputClass} placeholder="描述" value={maintForm.description} onChange={e => setMaintForm({...maintForm, description: e.target.value})} />
          <div className="flex gap-2">
            <input className={inputClass} type="number" placeholder="费用" value={maintForm.cost} onChange={e => setMaintForm({...maintForm, cost: e.target.value})} />
            <input className={inputClass} type="number" step="0.5" placeholder="停机(小时)" value={maintForm.downtime_hours} onChange={e => setMaintForm({...maintForm, downtime_hours: e.target.value})} />
          </div>
          <input className={inputClass} placeholder="技术员" value={maintForm.technician} onChange={e => setMaintForm({...maintForm, technician: e.target.value})} />
          <input className={inputClass} type="date" value={maintForm.record_date} onChange={e => setMaintForm({...maintForm, record_date: e.target.value})} />
          <button onClick={submitMaint} className="w-full bg-[var(--green)] text-white py-2 rounded-lg text-sm font-bold">📝 记录</button>
        </div>
      )}

      {/* 维保历史 */}
      {showMaintFor && (
        <div className="card mb-3">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-bold">{showMaintFor} · 维保记录</h3>
            <button onClick={() => { setShowMaintFor(''); setMaintList([]); }} className="text-xs text-[var(--accent)]">关闭</button>
          </div>
          {maintList.map((m:any,i:number) => (
            <div key={i} className="text-xs text-[var(--text2)] py-0.5 flex justify-between">
              <span>{m.record_date} · {m.record_type==='MAINTAIN'?'🛢️保养':'🔧维修'} · {m.description}</span>
              <span>¥{m.cost} · {m.downtime_hours}h停机</span>
            </div>
          ))}
        </div>
      )}

      {/* 设备列表 */}
      <div className="space-y-1.5">
        {equips.filter(e => !filter || e.equip_type === filter).map(e => (
          <div key={e.equip_code} className={`card flex items-center justify-between py-2.5 ${e.status==='REPAIR'?'alert-red':e.status==='SCRAPPED'?'opacity-50':''}`} onClick={() => viewMaint(e.equip_code)}>
            <div>
              <div className="text-sm font-bold">{e.equip_name} <span className="text-[10px] text-[var(--text3)]">{e.equip_code}</span></div>
              <div className="text-[10px] text-[var(--text2)]">{e.equip_type} · {e.production_line || '未分配'} · 上次保养 {e.last_maintain || '-'}</div>
            </div>
            <span className={`badge ${e.status==='NORMAL'?'badge-completed':e.status==='REPAIR'?'badge-delayed':'badge-pending'}`}>
              {e.status==='NORMAL'?'正常':e.status==='REPAIR'?'维修中':'已报废'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
