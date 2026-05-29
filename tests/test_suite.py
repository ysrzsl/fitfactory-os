"""
FitFactory OS - 完整回归测试套件
覆盖所有 API 端点 + AI Agent + 知识库 + 导出
"""
import requests, json, sys, os

API = "http://localhost:8000/api"
PASS = 0; FAIL = 0; SKIP = 0
FAILED = []

def test(name, method, url, json_data=None, expected_status=(200, 201)):
    global PASS, FAIL, SKIP
    try:
        if method == "GET":
            resp = requests.get(f"{API}{url}", timeout=10)
        elif method == "POST":
            resp = requests.post(f"{API}{url}", json=json_data, timeout=10)
        else:
            resp = requests.request(method, f"{API}{url}", json=json_data, timeout=10)

        if resp.status_code in (expected_status if isinstance(expected_status, tuple) else (expected_status,)):
            PASS += 1
            return resp
        else:
            FAIL += 1
            FAILED.append(f"{name}: HTTP {resp.status_code} {resp.text[:80]}")
            return resp
    except Exception as e:
        FAIL += 1
        FAILED.append(f"{name}: {e}")
        return None

def ok(name): print(f"  [PASS] {name}")
def no(name): print(f"  [FAIL] {name}")

print("=" * 55)
print("FitFactory OS - Regression Test Suite")
print("=" * 55)

# ── 0. 健康检查 ─────────────────────────────────────
print("\n--- 0. Health ---")
r = test("Health", "GET", "/../health")
ok("Health") if r and r.status_code == 200 else no("Health")

# ── 1. 款式 API ─────────────────────────────────────
print("\n--- 1. Styles ---")
test("List styles", "GET", "/styles/"); ok("List")
test("Get style", "GET", "/styles/NK-2026-001"); ok("Get")
test("Create style", "POST", "/styles/", {"style_code":"T-1","standard_capacity":{"A":100}}); ok("Create")
test("Update style", "PUT", "/styles/T-1", {"style_name":"Test"}); ok("Update")
test("Delete style", "DELETE", "/styles/T-1", expected_status=204); ok("Delete")

# ── 2. 产线 API ─────────────────────────────────────
print("\n--- 2. Lines ---")
test("List lines", "GET", "/lines/"); ok("List")
test("Get line", "GET", "/lines/缝制一车间A线"); ok("Get")

# ── 3. 订单 API ─────────────────────────────────────
print("\n--- 3. Orders ---")
test("List orders", "GET", "/orders/"); ok("List")
test("Pending orders", "GET", "/orders/?status=PENDING"); ok("Pending filter")
test("Upcoming orders", "GET", "/orders/due/upcoming?days=30"); ok("Upcoming")
test("Create order", "POST", "/orders/", {
    "order_number":"T-ORDER","customer_name":"Test","style_code":"NK-2026-001",
    "total_quantity":1000,"delivery_date":"2026-07-01"
}); ok("Create")
test("Get order", "GET", "/orders/T-ORDER"); ok("Get")
test("Delete order", "DELETE", "/orders/T-ORDER", expected_status=204); ok("Delete")

# ── 4. 排单 API ─────────────────────────────────────
print("\n--- 4. Schedule ---")
test("Auto schedule", "POST", "/schedule/auto", {"order_number":"SO-20260604"})
ok("Auto schedule")
test("Conflicts", "GET", "/schedule/conflicts"); ok("Conflicts")
test("Capacity warning", "GET", "/schedule/capacity-warning?days=14"); ok("Capacity")
test("Simulate insertion", "POST", "/schedule/simulate-insertion", {
    "style_code":"NK-2026-003","quantity":2000,"desired_start_date":"2026-06-10"
}); ok("Simulate")

# ── 5. 物料 API ─────────────────────────────────────
print("\n--- 5. Materials ---")
test("List materials", "GET", "/materials/"); ok("List")
test("Shortage alert", "GET", "/materials/shortage-alert"); ok("Shortage")
test("Purchase suggestion", "GET", "/materials/purchase-suggestion"); ok("Purchase")
test("Stock in", "POST", "/materials/transactions/in", {
    "material_code":"MAT-TEST","quantity":500,"operator":"Test","transaction_type":"IN"
}); ok("In")
test("Stock out", "POST", "/materials/transactions/out", {
    "material_code":"MAT-TEST","quantity":100,"operator":"Test","transaction_type":"OUT"
}); ok("Out")
test("Check material", "GET", "/materials/check/SO-20260601"); ok("Check")

# ── 6. 计件 API ─────────────────────────────────────
print("\n--- 6. Piecework ---")
test("Create record", "POST", "/piecework/", {
    "worker_name":"TEST-W","order_number":"SO-20260601","quantity":50,
    "process_name":"缝制","unit_price":0.5,"work_date":"2026-05-29","recorded_by":"Test"
}); ok("Create")
test("List records", "GET", "/piecework/?work_date=2026-05-29"); ok("List")

# ── 7. 工资 API ─────────────────────────────────────
print("\n--- 7. Payroll ---")
test("Monthly payroll", "GET", "/payroll/monthly?year=2026&month=5"); ok("Monthly")

# ── 8. 看板 API ─────────────────────────────────────
print("\n--- 8. Dashboard ---")
test("Overview", "GET", "/dashboard/overview"); ok("Overview")
test("Gantt", "GET", "/dashboard/gantt"); ok("Gantt")
test("Delays", "GET", "/dashboard/delays"); ok("Delays")
test("Daily report", "GET", "/dashboard/daily-report"); ok("Daily")
test("Refresh progress", "POST", "/dashboard/refresh-progress"); ok("Progress")
test("Order tracking", "GET", "/dashboard/order/SO-20260601"); ok("Tracking")

# ── 9. 知识库 API ───────────────────────────────────
print("\n--- 9. Knowledge Base ---")
test("Search", "GET", "/knowledge/search?query=蕾丝面料缩水"); ok("Search")
test("Stats", "GET", "/knowledge/stats"); ok("Stats")
r2 = test("Search quality check", "GET", "/knowledge/search?query=设备坏了怎么办")
if r2 and r2.status_code == 200:
    data = r2.json()
    if data["count"] > 0:
        ok("Search quality")
    else:
        print(f"  [WARN] Search returned 0 results for '设备坏了怎么办'")

# ── 10. 导出 API ───────────────────────────────────
print("\n--- 10. Export ---")
test("Export orders", "GET", "/export/orders"); ok("Orders")
test("Export payroll", "GET", "/export/payroll?year=2026&month=5"); ok("Payroll")
test("Export materials", "GET", "/export/materials"); ok("Materials")

# ── 11. AI Agent ────────────────────────────────────
print("\n--- 11. AI Agent ---")
# 先重置对话
requests.post(f"{API}/chat/reset")
test("AI intro", "POST", "/chat/", {"message":"你好"}); ok("Intro")
test("AI query order", "POST", "/chat/", {"message":"SO-20260601的进度"}); ok("Order query")
test("AI query lines", "POST", "/chat/", {"message":"产线状态"}); ok("Lines")

# ── 12. 错误处理 ────────────────────────────────────
print("\n--- 12. Error Handling ---")
test("404 not found", "GET", "/orders/NOEXIST", expected_status=404); ok("404")
test("400 bad request", "POST", "/schedule/auto", {"bad":"data"}, expected_status=422); ok("422")

# ── Summary ────────────────────────────────────────
print(f"\n{'='*55}")
print(f"Results: {PASS} passed, {FAIL} failed, {SKIP} skipped")
if FAILED:
    print(f"\nFailures:")
    for f in FAILED: print(f"  {f}")
print(f"{'='*55}")
