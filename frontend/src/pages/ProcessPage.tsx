import { useState, useEffect } from "react";
const API = "https://fitfactory-os-production.up.railway.app/api";
export default function ProcessPage() {
  const [templates, setTemplates] = useState<any[]>([]);
  const load = () => { fetch(API + "/processes/").then(r=>r.json()).then(setTemplates); };
  useEffect(() => { load(); }, []);
  return (
    <div><h2 className="text-lg font-bold mb-3">🔗 工艺路线</h2>
    <div className="space-y-2">{templates.map((t:any)=>(
      <div key={t.style_code} className="card">
        <div className="text-sm font-bold">{t.style_code} · 总工时 {t.total_time_min}分钟/件</div>
        {t.steps?.map((s:any,i:number)=>(
          <div key={i} className="flex items-center gap-2 py-1 text-xs text-[var(--text2)]">
            <span className="w-5 h-5 rounded-full bg-[var(--accent)]/20 text-[var(--accent)] text-[10px] font-bold flex items-center justify-center">{s.step}</span>
            <span>{s.process} · {s.machine} · {s.time_min}min</span>
            {s.qc_required && <span className="badge badge-pending text-[9px]">需质检</span>}
          </div>
        ))}
      </div>
    ))}</div></div>
  );
}
