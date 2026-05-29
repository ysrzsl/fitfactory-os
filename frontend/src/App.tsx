import { useState, useEffect, useCallback } from 'react';
import Orders from './pages/Orders';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Schedule from './pages/Schedule';
import PieceWork from './pages/PieceWork';
import ImportData from './pages/ImportData';

import CostPage from './pages/CostPage';
import CustomerPage from './pages/CustomerPage';
import QualityPage from './pages/QualityPage';

import EquipmentPage from './pages/EquipmentPage';
import SOPPage from './pages/SOPPage';
import ProcessPage from './pages/ProcessPage';

const NAV = [
  { id: 'chat', label: '💬 AI 助手', icon: '💬', C: Chat },
  { id: 'orders', label: '📋 订单管理', icon: '📋', C: Orders },
  { id: 'schedule', label: '📅 生产排单', icon: '📅', C: Schedule },
  { id: 'dashboard', label: '📊 生产看板', icon: '📊', C: Dashboard },
  { id: 'piecework', label: '💰 计件工资', icon: '💰', C: PieceWork },
  { id: 'cost', label: '📈 成本核算', icon: '📈', C: CostPage },
  { id: 'customers', label: '👥 客户管理', icon: '👥', C: CustomerPage },
  { id: 'quality', label: '🔍 质量管理', icon: '🔍', C: QualityPage },
  { id: 'equipment', label: '🔧 设备管理', icon: '🔧', C: EquipmentPage },
  { id: 'processes', label: '🔗 工艺路线', icon: '🔗', C: ProcessPage },
  { id: 'sop', label: '📋 SOP流程', icon: '📋', C: SOPPage },
  { id: 'import', label: '📥 数据导入', icon: '📥', C: ImportData },
];

export default function App() {
  const [page, setPage] = useState('chat');
  const [theme, setTheme] = useState<'dark'|'light'>('dark');
  const [fontSize, setFontSize] = useState<'sm'|'md'|'lg'>('md');
  const [online, setOnline] = useState(navigator.onLine);
  const [searchOpen, setSearchOpen] = useState(false);
  const [toast, setToast] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);

  const Page = NAV.find(n => n.id === page)?.C || Chat;

  useEffect(() => { document.documentElement.setAttribute('data-theme', theme); }, [theme]);
  useEffect(() => { document.documentElement.setAttribute('data-font', fontSize); }, [fontSize]);

  useEffect(() => {
    const go = () => { setOnline(true); showToast('网络已恢复'); };
    const off = () => setOnline(false);
    window.addEventListener('online', go); window.addEventListener('offline', off);
    return () => { window.removeEventListener('online', go); window.removeEventListener('offline', off); };
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); setSearchOpen(v => !v); }
      if (e.key === 'Escape') setSearchOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const showToast = useCallback((msg: string) => { setToast(msg); setTimeout(() => setToast(''), 2000); }, []);

  return (
    <div className={!online ? 'offline' : ''}>
      <div className="offline-bar">⚠️ 网络已断开，部分功能不可用</div>
      {toast && <div className="toast">{toast}</div>}

      {/* 全局搜索 */}
      <div className={`search-overlay ${searchOpen ? 'active' : ''}`} onClick={() => setSearchOpen(false)}>
        <input className="search-box" placeholder="搜索订单号、客户名..." autoFocus
          onClick={e => e.stopPropagation()}
          onKeyDown={e => { if (e.key === 'Enter') { const v = (e.target as HTMLInputElement).value.trim(); if (v) { setPage('orders'); setSearchOpen(false); } } }} />
      </div>

      <div className="flex h-screen overflow-hidden">
        {/* ── PC 侧边栏 ── */}
        <aside className="hidden md:flex md:flex-col bg-[var(--bg2)] border-r border-[var(--border)] shrink-0" style={{width:'var(--sidebar-w)'}}>
          <div className="px-4 py-4 border-b border-[var(--border)]">
            <div className="flex items-center gap-2">
              <span className="text-xl">🏭</span>
              <div>
                <h1 className="text-sm font-bold text-[var(--text)]">FitFactory OS</h1>
                <p className="text-[10px] text-[var(--text3)]">服装厂智能工作台</p>
              </div>
            </div>
          </div>
          <nav className="flex-1 py-2 overflow-auto">
            {NAV.map(n => (
              <button key={n.id} onClick={() => setPage(n.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition ${
                  page === n.id
                    ? 'bg-[var(--accent)]/10 text-[var(--accent)] font-bold border-r-2 border-[var(--accent)]'
                    : 'text-[var(--text2)] hover:bg-[var(--bg3)] hover:text-[var(--text)]'
                }`}>
                <span className="text-lg">{n.icon}</span>
                <span>{n.label.slice(2)}</span>
              </button>
            ))}
          </nav>
          <div className="px-4 py-3 border-t border-[var(--border)] flex items-center gap-1">
            <button onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
              className="p-1.5 rounded text-xs text-[var(--text2)] hover:bg-[var(--bg3)]" title="切换主题">
              {theme === 'dark' ? '🌙' : '☀️'}
            </button>
            <button onClick={() => setFontSize(f => f === 'md' ? 'lg' : f === 'lg' ? 'sm' : 'md')}
              className="p-1.5 rounded text-xs text-[var(--text2)] hover:bg-[var(--bg3)]" title="字号">
              A{fontSize === 'sm' ? '小' : fontSize === 'lg' ? '大' : '中'}
            </button>
            <span className="text-[10px] text-[var(--text3)] ml-auto">Ctrl+K</span>
          </div>
        </aside>

        {/* ── 右侧主区域 ── */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* 顶栏（移动端 + 工具） */}
          <header className="md:hidden bg-[var(--bg2)] border-b border-[var(--border)] px-3 py-2 flex items-center gap-2 shrink-0 no-print">
            <span className="text-lg">🏭</span>
            <h1 className="text-sm font-bold">FitFactory OS</h1>
            <div className="flex items-center gap-1 ml-auto">
              <button onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
                className="p-1.5 rounded text-xs text-[var(--text2)] hover:bg-[var(--bg3)]">{theme === 'dark' ? '🌙' : '☀️'}</button>
              <button onClick={() => setFontSize(f => f === 'md' ? 'lg' : f === 'lg' ? 'sm' : 'md')}
                className="p-1.5 rounded text-xs text-[var(--text2)] hover:bg-[var(--bg3)]">A{fontSize === 'sm' ? '小' : fontSize === 'lg' ? '大' : '中'}</button>
              {page === 'dashboard' && (
                <button onClick={() => setAutoRefresh(r => !r)}
                  className={`p-1.5 rounded text-xs ${autoRefresh ? 'text-[var(--green)]' : 'text-[var(--text2)]'} hover:bg-[var(--bg3)]`}>
                  {autoRefresh ? '⏸' : '▶'}
                </button>
              )}
            </div>
          </header>

          {/* PC 顶栏（简洁） */}
          <header className="hidden md:flex bg-[var(--bg2)] border-b border-[var(--border)] px-4 py-2 items-center gap-2 shrink-0 no-print">
            <h2 className="text-sm font-bold text-[var(--text)]">{NAV.find(n => n.id === page)?.label}</h2>
            <div className="flex items-center gap-1 ml-auto">
              {page === 'dashboard' && (
                <button onClick={() => setAutoRefresh(r => !r)}
                  className={`px-2 py-1 rounded text-xs ${autoRefresh ? 'text-[var(--green)] bg-[var(--green)]/10' : 'text-[var(--text2)]'} hover:bg-[var(--bg3)]`}>
                  {autoRefresh ? '⏸ 停止刷新' : '▶ 自动刷新'}
                </button>
              )}
              <span className="text-[10px] text-[var(--text3)]">Ctrl+K 搜索</span>
            </div>
          </header>

          {/* 主内容 */}
          <main className="flex-1 overflow-auto px-4 py-4 md:px-6 md:py-5 pb-20 md:pb-5">
            <div className="mx-auto" style={{maxWidth:'var(--content-max)'}}>
            <Page autoRefresh={autoRefresh} showToast={showToast} />
            </div>
          </main>
        </div>

        {/* ── 移动端底部导航 ── */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-[var(--bg2)] border-t border-[var(--border)] flex justify-around py-1.5 z-50 no-print" style={{ height: 'var(--nav-h)' }}>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)}
              className={`flex flex-col items-center px-1.5 py-0.5 text-[11px] transition ${page === n.id ? 'text-[var(--accent)]' : 'text-[var(--text2)]'}`}>
              <span className="text-base">{n.icon}</span>
              <span className="text-[10px]">{n.label.slice(2, 4)}</span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}
