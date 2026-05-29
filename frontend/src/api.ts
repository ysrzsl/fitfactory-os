// 生产环境使用 Railway 后端
const BASE = window.location.hostname === 'localhost' ? '/api' : 'https://fitfactory-os-production.up.railway.app/api';

async function get<T>(url: string): Promise<T> {
  const r = await fetch(BASE + url);
  if (!r.ok) throw new Error(r.statusText);
  return r.json();
}

async function post<T>(url: string, body?: unknown): Promise<T> {
  const r = await fetch(BASE + url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export const api = {
  orders: {
    list: (s?: string) => get<any[]>(`/orders/${s ? '?status=' + s : ''}`),
    get: (on: string) => get<any>(`/orders/${on}`),
    create: (d: any) => post<any>('/orders/', d),
  },
  schedule: {
    auto: (order_number: string) => post<any>('/schedule/auto', { order_number }),
    simulate: (style_code: string, quantity: number, desired_start_date: string) =>
      post<any>('/schedule/simulate-insertion', { style_code, quantity, desired_start_date }),
    conflicts: () => get<any>('/schedule/conflicts'),
  },
  dashboard: {
    overview: () => get<any>('/dashboard/overview'),
    gantt: () => get<any>('/dashboard/gantt'),
    delays: () => get<any>('/dashboard/delays'),
  },
  chat: {
    send: (message: string) => post<{ reply: string }>('/chat/', { message }),
  },
};
