import { useState, useEffect } from 'react';

export default function ProcessPage() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [form, setForm] = useState({ style_code: '', steps_json: '[{"step":1,"process":"裁剪","machine":"裁床","time_min":2,"qc_required":true},{"step":2,"process":"缝制","machine":"平缝机","time_min":8,"qc_required":false},{"step":3,"process":"质检","machine":"-","time_min":3,"qc_required":true},{"step":4,"process":"包装","machine":"-","time_min":1,"qc_required":false}]' });

  const load = () => { fetch('/api/processes/').then(r => r.json()).then(setTemplates); };
  useEffect(() => { load(); }, []);

  const submit = async () => {
    try {
      const steps = JSON.parse(form.steps_json);
      await fetch('/api/processes/', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ style_code:form.style_code, steps }) });
      setShowForm(false); load();
    } catch { alert('JSON 格式错误'); }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold">🔗 工艺路线</h2>
        <button onClick={() => setShowForm(!showForm)} className="bg-[var(--accent)] text-white px-3 py-1.5 rounded-lg text-sm font-bold">+ 新建</button>
      </div>

      {showForm && (
        <div className="card mb-3 space-y-2">
          <input className="w-full bg-[var(--bg3)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm" placeholder="款号" value={form.style_code} onChange={e => setForm({...form, style_code: e.target.value})} />
          <textarea className="w-full bg-[var(--bg3)] border border-[var(--border)] rounded-lg px-3 py-2 text-xs h-32" value={form.steps_json} onChange={e => setForm({...form, steps_json: e.target.value})} />
          <button onClick={submit} className="w-full bg-[var(--green)] text-white py-2 rounded-lg text-sm font-bold">✅ 保存</button>
        </div>
      )}

      <div className="space-y-2">
        {templates.map((t: any) => (
          <div key={t.style_code} className="card cursor-pointer" onClick={() => setSelected(selected?.style_code===t.style_code?null:t)}>
            <div className="text-sm font-bold">{t.style_code} · 总工时 {t.total_time_min}分钟/件</div>
            {selected?.style_code === t.style_code && (
              <div className="mt-2 pt-2 border-t border-[var(--border)]">
                {t.steps.map((s: any, i: number) => (
                  <div key={i} className="flex items-center gap-2 py-1 text-xs text-[var(--text2)]">
                    <span className="w-5 h-5 rounded-full bg-[var(--accent)]/20 text-[var(--accent)] text-[10px] font-bold flex items-center justify-center">{s.step}</span>
                    <span>{s.process} · {s.machine} · {s.time_min}min</span>
                    {s.qc_required && <span className="badge badge-pending text-[9px]">需质检</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
