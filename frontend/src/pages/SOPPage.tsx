import { useState } from 'react';

export default function SOPPage() {
  const [sops] = useState([
    { id:'SOP-001', title:'订单延期处理', steps:['检测到延期','通知销售与客户沟通','评估加班/加人/外发','调整排产优先级','记录延期原因','每日跟进至交付'], color:'var(--red)' },
    { id:'SOP-002', title:'质量问题处理', steps:['发现批量问题','立即停线','隔离问题批次','追溯工序和责任人','评估返工成本','分析根因更新标准','问题未解决不复产'], color:'var(--yellow)' },
    { id:'SOP-003', title:'设备故障应急', steps:['操作工立即停机','挂故障待修标识','通知设备维修组','超4小时协调其他产线','记录故障时长'], color:'var(--red)' },
    { id:'SOP-004', title:'客户插单处理', steps:['确认款式数量和交期','运行插单模拟','A级客户需厂长审批','普通客户延期≤3天可直接确认','排入产线通知销售'], color:'var(--accent)' },
    { id:'SOP-005', title:'缺料应急处理', steps:['库存低于安全线','通知采购下紧急订单','检查在途催供应商','评估替代物料','调整排产将缺料订单后移','记录缺料事件'], color:'var(--yellow)' },
  ]);

  return (
    <div>
      <h2 className="text-lg font-bold mb-3">📋 SOP 流程设计</h2>
      <p className="text-xs text-[var(--text2)] mb-4">标准操作流程 — 遇到问题按图操作，减少决策失误</p>

      <div className="space-y-3">
        {sops.map(sop => (
          <div key={sop.id} className="card" style={{borderLeft:`4px solid ${sop.color}`}}>
            <div className="text-sm font-bold mb-2" style={{color:sop.color}}>{sop.id}: {sop.title}</div>
            <div className="flex items-start">
              {sop.steps.map((step, i) => (
                <div key={i} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div className="w-6 h-6 rounded-full text-[10px] font-bold flex items-center justify-center text-white" style={{background:sop.color}}>{i+1}</div>
                    <div className="text-[9px] text-[var(--text3)] mt-0.5 max-w-16 text-center leading-tight">{step}</div>
                  </div>
                  {i < sop.steps.length - 1 && (
                    <div className="w-4 h-0.5 mt-3" style={{background:sop.color,opacity:0.3}} />
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
