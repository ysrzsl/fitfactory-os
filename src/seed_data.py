"""
种子数据 v2 — 丰富演示数据
用法: python src/seed_data.py
先清空再填充
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.config import DATABASE_URL
from src.models import Base
from src.models.style import Style
from src.models.production_line import ProductionLine
from src.models.order import Order
from src.models.material import Material
from src.models.inventory import InventoryTransaction
from src.models.piece_work import PieceWorkRecord
from src.models.order_progress import OrderProgress
from src.models.worker import Worker
from src.models.salary_adjustment import SalaryAdjustment
from src.models.customer import Customer
from src.models.qc_record import QCRecord
from src.models.equipment import Equipment
from src.models.maintenance import MaintenanceRecord
from src.models.process_template import ProcessTemplate


def seed():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        today = date.today()

        # ── 1. 款式 (6款) ───────────────────────────────
        styles = [
            Style(style_code="NK-2026-001", style_name="蕾丝无钢圈内衣", category="内衣",
                  standard_capacity={"缝制一车间A线":500,"缝制二车间B线":450,"缝制三车间C线":400},
                  bom_data={"蕾丝面料":"0.15米","肩带":"2根","背钩":"1个","水洗标":"1个","包装袋":"1个"}),
            Style(style_code="NK-2026-002", style_name="运动无痕文胸", category="文胸",
                  standard_capacity={"缝制一车间A线":400,"缝制二车间B线":380,"缝制三车间C线":350},
                  bom_data={"弹力面料":"0.20米","胸垫":"2片","肩带":"2根","背钩":"2个"}),
            Style(style_code="NK-2026-003", style_name="纯棉家居睡裙", category="睡衣",
                  standard_capacity={"缝制一车间A线":600,"缝制二车间B线":550,"缝制三车间C线":500},
                  bom_data={"纯棉面料":"1.20米","蕾丝花边":"0.30米","水洗标":"1个","包装袋":"1个"}),
            Style(style_code="NK-2026-004", style_name="无缝运动内衣", category="内衣",
                  standard_capacity={"缝制一车间A线":450,"缝制二车间B线":420,"缝制三车间C线":380},
                  bom_data={"弹力网眼":"0.18米","胸垫":"2片","肩带":"2根"}),
            Style(style_code="NK-2026-005", style_name="真丝吊带睡裙", category="睡衣",
                  standard_capacity={"缝制一车间A线":300,"缝制二车间B线":280,"缝制三车间C线":250},
                  bom_data={"真丝面料":"0.90米","蕾丝花边":"0.20米","吊带":"2根","包装袋":"1个"}),
            Style(style_code="NK-2026-006", style_name="哺乳文胸", category="文胸",
                  standard_capacity={"缝制一车间A线":380,"缝制二车间B线":350,"缝制三车间C线":320},
                  bom_data={"纯棉面料":"0.20米","胸垫":"2片","哺乳扣":"2个","肩带":"2根"}),
        ]
        db.add_all(styles)

        # ── 2. 产线 (5条) ───────────────────────────────
        lines = [
            ProductionLine(line_name="缝制一车间A线", operator_count=25, status="BUSY", available_from=today+timedelta(days=8)),
            ProductionLine(line_name="缝制二车间B线", operator_count=22, status="BUSY", available_from=today+timedelta(days=4)),
            ProductionLine(line_name="缝制三车间C线", operator_count=20, status="IDLE", available_from=today),
            ProductionLine(line_name="缝制四车间D线", operator_count=18, status="IDLE", available_from=today),
            ProductionLine(line_name="后整包装线", operator_count=15, status="IDLE", available_from=today),
        ]
        db.add_all(lines)

        # ── 3. 物料 (8种) ───────────────────────────────
        materials = [
            Material(material_code="FAB-LACE-001", material_name="蕾丝面料", category="面料", unit="米", safety_stock=300, current_stock=800, supplier_name="绍兴纺织", lead_time_days=7),
            Material(material_code="FAB-ELASTIC-001", material_name="弹力面料", category="面料", unit="米", safety_stock=250, current_stock=150, supplier_name="绍兴纺织", lead_time_days=5),
            Material(material_code="FAB-COTTON-001", material_name="纯棉面料", category="面料", unit="米", safety_stock=500, current_stock=2000, supplier_name="新疆棉业", lead_time_days=10),
            Material(material_code="FAB-SILK-001", material_name="真丝面料", category="面料", unit="米", safety_stock=100, current_stock=80, supplier_name="苏州丝绸", lead_time_days=14),
            Material(material_code="FAB-MESH-001", material_name="弹力网眼面料", category="面料", unit="米", safety_stock=200, current_stock=600, supplier_name="绍兴纺织", lead_time_days=7),
            Material(material_code="ACC-STRAP-001", material_name="肩带", category="辅料", unit="根", safety_stock=5000, current_stock=12000, supplier_name="义乌辅料", lead_time_days=3),
            Material(material_code="ACC-HOOK-001", material_name="背钩", category="辅料", unit="个", safety_stock=3000, current_stock=8000, supplier_name="义乌辅料", lead_time_days=3),
            Material(material_code="ACC-PAD-001", material_name="胸垫", category="辅料", unit="片", safety_stock=4000, current_stock=2500, supplier_name="东莞海绵", lead_time_days=5),
            Material(material_code="PKG-BAG-001", material_name="包装袋", category="包装", unit="个", safety_stock=10000, current_stock=30000, supplier_name="本地包装厂", lead_time_days=2),
            Material(material_code="PKG-TAG-001", material_name="水洗标", category="包装", unit="个", safety_stock=8000, current_stock=20000, supplier_name="本地印刷厂", lead_time_days=2),
        ]
        db.add_all(materials)

        # ── 4. 订单 (12张，多种状态) ────────────────────
        orders = [
            # PENDING 待排产
            Order(order_number="SO-20260601", customer_name="金狐狸服饰", style_code="NK-2026-001", total_quantity=5000, delivery_date=today+timedelta(days=20), priority="HIGH", status="PENDING"),
            Order(order_number="SO-20260602", customer_name="曼妮芬内衣", style_code="NK-2026-002", total_quantity=3000, delivery_date=today+timedelta(days=15), priority="HIGH", status="PENDING"),
            Order(order_number="SO-20260603", customer_name="都市丽人", style_code="NK-2026-001", total_quantity=8000, delivery_date=today+timedelta(days=35), priority="NORMAL", status="PENDING"),
            Order(order_number="SO-20260604", customer_name="蕉内", style_code="NK-2026-003", total_quantity=2000, delivery_date=today+timedelta(days=10), priority="HIGH", status="PENDING"),
            # SCHEDULED 已排产
            Order(order_number="SO-20260501", customer_name="爱慕", style_code="NK-2026-002", total_quantity=4500, delivery_date=today+timedelta(days=18), priority="NORMAL", status="SCHEDULED",
                  assigned_line="缝制一车间A线", start_date=today+timedelta(days=8), end_date=today+timedelta(days=17)),
            Order(order_number="SO-20260502", customer_name="内外", style_code="NK-2026-004", total_quantity=3500, delivery_date=today+timedelta(days=12), priority="HIGH", status="SCHEDULED",
                  assigned_line="缝制二车间B线", start_date=today+timedelta(days=4), end_date=today+timedelta(days=12)),
            # IN_PROGRESS 在产
            Order(order_number="SO-20260401", customer_name="歌瑞尔", style_code="NK-2026-005", total_quantity=2000, delivery_date=today+timedelta(days=8), priority="HIGH", status="IN_PROGRESS",
                  assigned_line="缝制一车间A线", start_date=today-timedelta(days=5), end_date=today+timedelta(days=2)),
            Order(order_number="SO-20260402", customer_name="欧迪芬", style_code="NK-2026-003", total_quantity=6000, delivery_date=today+timedelta(days=14), priority="NORMAL", status="IN_PROGRESS",
                  assigned_line="缝制二车间B线", start_date=today-timedelta(days=8), end_date=today+timedelta(days=4)),
            Order(order_number="SO-20260403", customer_name="维多利亚", style_code="NK-2026-006", total_quantity=4000, delivery_date=today+timedelta(days=6), priority="HIGH", status="IN_PROGRESS",
                  assigned_line="缝制三车间C线", start_date=today-timedelta(days=6), end_date=today+timedelta(days=2)),
            # COMPLETED 已完成
            Order(order_number="SO-20260301", customer_name="Ubras", style_code="NK-2026-004", total_quantity=3000, delivery_date=today-timedelta(days=3), priority="NORMAL", status="COMPLETED",
                  assigned_line="缝制三车间C线", start_date=today-timedelta(days=14), end_date=today-timedelta(days=4)),
            Order(order_number="SO-20260302", customer_name="好奇蜜斯", style_code="NK-2026-001", total_quantity=2500, delivery_date=today-timedelta(days=5), priority="HIGH", status="COMPLETED",
                  assigned_line="缝制二车间B线", start_date=today-timedelta(days=18), end_date=today-timedelta(days=6)),
            # DELAYED 延期
            Order(order_number="SO-20260303", customer_name="安莉芳", style_code="NK-2026-002", total_quantity=5500, delivery_date=today-timedelta(days=2), priority="HIGH", status="DELAYED",
                  assigned_line="缝制一车间A线", start_date=today-timedelta(days=16), end_date=today-timedelta(days=2)),
        ]
        db.add_all(orders)

        # ── 5. 订单进度 ────────────────────────────────
        progresses = [
            OrderProgress(order_number="SO-20260401", completed_qty=1200, remaining_qty=800, completion_rate=60.0),
            OrderProgress(order_number="SO-20260402", completed_qty=3500, remaining_qty=2500, completion_rate=58.3),
            OrderProgress(order_number="SO-20260403", completed_qty=1800, remaining_qty=2200, completion_rate=45.0),
            OrderProgress(order_number="SO-20260301", completed_qty=3000, remaining_qty=0, completion_rate=100.0),
            OrderProgress(order_number="SO-20260302", completed_qty=2500, remaining_qty=0, completion_rate=100.0),
            OrderProgress(order_number="SO-20260303", completed_qty=5000, remaining_qty=500, completion_rate=90.9),
        ]
        db.add_all(progresses)

        # ── 6. 工人基础信息 ────────────────────────────
        workers_data = [
            Worker(worker_name="张丽", worker_id="W001", base_salary=2800, social_insurance=420, position="缝制组长", hire_date=today-timedelta(days=400)),
            Worker(worker_name="王芳", worker_id="W002", base_salary=2500, social_insurance=380, position="缝制", hire_date=today-timedelta(days=300)),
            Worker(worker_name="李秀兰", worker_id="W003", base_salary=2500, social_insurance=380, position="缝制", hire_date=today-timedelta(days=250)),
            Worker(worker_name="陈美玲", worker_id="W004", base_salary=2500, social_insurance=380, position="缝制", hire_date=today-timedelta(days=200)),
            Worker(worker_name="赵红", worker_id="W005", base_salary=2400, social_insurance=360, position="裁剪", hire_date=today-timedelta(days=350)),
            Worker(worker_name="刘小燕", worker_id="W006", base_salary=2400, social_insurance=360, position="裁剪", hire_date=today-timedelta(days=180)),
            Worker(worker_name="黄玉", worker_id="W007", base_salary=2300, social_insurance=350, position="质检", hire_date=today-timedelta(days=280)),
            Worker(worker_name="周桂英", worker_id="W008", base_salary=2300, social_insurance=350, position="质检", hire_date=today-timedelta(days=150)),
            Worker(worker_name="吴金花", worker_id="W009", base_salary=2200, social_insurance=340, position="包装", hire_date=today-timedelta(days=320)),
            Worker(worker_name="郑雪梅", worker_id="W010", base_salary=2200, social_insurance=340, position="包装", hire_date=today-timedelta(days=120)),
        ]
        db.add_all(workers_data)

        # ── 7. 奖惩记录 ────────────────────────────────
        adjustments = [
            SalaryAdjustment(worker_name="张丽", adjust_type="BONUS", amount=300, reason="本月全勤奖", adjust_date=today-timedelta(days=5)),
            SalaryAdjustment(worker_name="张丽", adjust_type="BONUS", amount=200, reason="组长津贴", adjust_date=today-timedelta(days=3)),
            SalaryAdjustment(worker_name="王芳", adjust_type="PENALTY", amount=-50, reason="迟到2次", adjust_date=today-timedelta(days=10)),
            SalaryAdjustment(worker_name="李秀兰", adjust_type="BONUS", amount=500, reason="月度优秀员工奖", adjust_date=today-timedelta(days=2)),
            SalaryAdjustment(worker_name="赵红", adjust_type="SUBSIDY", amount=150, reason="夜班补贴", adjust_date=today-timedelta(days=8)),
            SalaryAdjustment(worker_name="吴金花", adjust_type="PENALTY", amount=-100, reason="包装不合格返工", adjust_date=today-timedelta(days=12)),
            SalaryAdjustment(worker_name="黄玉", adjust_type="BONUS", amount=200, reason="质检零差错奖", adjust_date=today-timedelta(days=1)),
        ]
        db.add_all(adjustments)

        # ── 8. 计件记录 (近14天) ────────────────────────
        workers = ["张丽","王芳","李秀兰","陈美玲","赵红","刘小燕","黄玉","周桂英","吴金花","郑雪梅"]
        processes = {"裁剪":0.3, "缝制":0.5, "质检":0.2, "包装":0.15}
        in_progress_orders = ["SO-20260401","SO-20260402","SO-20260403"]
        records = []
        for d in range(14, 0, -1):
            day = today - timedelta(days=d)
            for w in workers[:8]:
                proc = list(processes.keys())[hash(w+str(d)) % 4]
                qty = 80 + (hash(w+str(d)) % 120)
                records.append(PieceWorkRecord(
                    worker_name=w, order_number=in_progress_orders[hash(w) % 3],
                    process_name=proc, quantity=qty, unit_price=processes[proc], work_date=day))
        db.add_all(records)

        # ── 9. 客户 (8个) ────────────────────────────────
        customers_data = [
            Customer(customer_name="金狐狸服饰", level="A", contact_person="陈总", contact_phone="138-0001", total_orders=12, total_amount=480000, outstanding=50000),
            Customer(customer_name="曼妮芬内衣", level="A", contact_person="李经理", contact_phone="139-0002", total_orders=8, total_amount=320000, outstanding=0),
            Customer(customer_name="都市丽人", level="B", contact_person="王主管", contact_phone="137-0003", total_orders=5, total_amount=180000, outstanding=30000),
            Customer(customer_name="蕉内", level="A", contact_person="赵总监", contact_phone="136-0004", total_orders=6, total_amount=250000, outstanding=0),
            Customer(customer_name="爱慕", level="B", contact_person="刘经理", contact_phone="135-0005", total_orders=4, total_amount=150000, outstanding=20000),
            Customer(customer_name="内外", level="B", contact_person="周小姐", contact_phone="134-0006", total_orders=3, total_amount=90000, outstanding=0),
            Customer(customer_name="歌瑞尔", level="C", contact_person="吴生", contact_phone="133-0007", total_orders=2, total_amount=45000, outstanding=45000),
            Customer(customer_name="Ubras", level="A", contact_person="郑总", contact_phone="132-0008", total_orders=10, total_amount=400000, outstanding=0),
        ]
        db.add_all(customers_data)

        # ── 10. 质检记录 (6条) ───────────────────────────
        qc_records = [
            QCRecord(order_number="SO-20260401", inspect_date=today-timedelta(days=2), batch_size=100, defect_count=2, defect_rate=2.0, defect_type="线头", severity="MINOR", inspector="黄玉", result="PASS"),
            QCRecord(order_number="SO-20260402", inspect_date=today-timedelta(days=1), batch_size=100, defect_count=0, defect_rate=0, inspector="黄玉", result="PASS"),
            QCRecord(order_number="SO-20260403", inspect_date=today-timedelta(days=1), batch_size=100, defect_count=5, defect_rate=5.0, defect_type="尺寸", severity="MAJOR", inspector="周桂英", result="REWORK"),
            QCRecord(order_number="SO-20260301", inspect_date=today-timedelta(days=8), batch_size=100, defect_count=1, defect_rate=1.0, defect_type="色差", severity="MINOR", inspector="黄玉", result="PASS"),
            QCRecord(order_number="SO-20260302", inspect_date=today-timedelta(days=10), batch_size=100, defect_count=0, defect_rate=0, inspector="周桂英", result="PASS"),
            QCRecord(order_number="SO-20260303", inspect_date=today-timedelta(days=5), batch_size=100, defect_count=8, defect_rate=8.0, defect_type="破洞", severity="CRITICAL", inspector="黄玉", result="REJECT"),
        ]
        db.add_all(qc_records)

        # ── 11. 设备 (8台) ───────────────────────────────
        equip_data = [
            Equipment(equip_code="EQ-001", equip_name="平缝机#1", equip_type="平缝机", production_line="缝制一车间A线", status="NORMAL", last_maintain=today-timedelta(days=20), maintain_interval_days=30),
            Equipment(equip_code="EQ-002", equip_name="平缝机#2", equip_type="平缝机", production_line="缝制一车间A线", status="NORMAL", last_maintain=today-timedelta(days=35), maintain_interval_days=30),
            Equipment(equip_code="EQ-003", equip_name="包缝机#1", equip_type="包缝机", production_line="缝制二车间B线", status="REPAIR", last_maintain=today-timedelta(days=45), maintain_interval_days=30),
            Equipment(equip_code="EQ-004", equip_name="包缝机#2", equip_type="包缝机", production_line="缝制二车间B线", status="NORMAL", last_maintain=today-timedelta(days=15), maintain_interval_days=30),
            Equipment(equip_code="EQ-005", equip_name="熨烫台#1", equip_type="熨烫台", production_line="后整包装线", status="NORMAL", last_maintain=today-timedelta(days=25), maintain_interval_days=60),
            Equipment(equip_code="EQ-006", equip_name="熨烫台#2", equip_type="熨烫台", production_line="后整包装线", status="NORMAL", last_maintain=today-timedelta(days=25), maintain_interval_days=60),
            Equipment(equip_code="EQ-007", equip_name="自动裁床", equip_type="裁床", production_line="缝制三车间C线", status="NORMAL", last_maintain=today-timedelta(days=10), maintain_interval_days=90),
            Equipment(equip_code="EQ-008", equip_name="平缝机#3", equip_type="平缝机", production_line="缝制四车间D线", status="SCRAPPED", last_maintain=today-timedelta(days=180), maintain_interval_days=30),
        ]
        db.add_all(equip_data)

        # ── 12. 维修记录 ─────────────────────────────────
        maint_data = [
            MaintenanceRecord(equip_code="EQ-003", record_type="REPAIR", description="刀片磨损导致跳线", cost=200, technician="李师傅", record_date=today-timedelta(days=2), downtime_hours=4),
            MaintenanceRecord(equip_code="EQ-002", record_type="MAINTAIN", description="定期保养：清梭床+加油", cost=50, technician="李师傅", record_date=today-timedelta(days=35), downtime_hours=1),
        ]
        db.add_all(maint_data)

        # ── 13. 工艺路线模板 ─────────────────────────────
        process_templates = [
            ProcessTemplate(style_code="NK-2026-001", steps=[
                {"step":1,"process":"裁剪","machine":"裁床","time_min":2,"qc_required":True},
                {"step":2,"process":"缝制","machine":"平缝机","time_min":5,"qc_required":False},
                {"step":3,"process":"质检","machine":"-","time_min":2,"qc_required":True},
                {"step":4,"process":"包装","machine":"-","time_min":1,"qc_required":False},
            ], total_time_min=10),
            ProcessTemplate(style_code="NK-2026-002", steps=[
                {"step":1,"process":"裁剪","machine":"裁床","time_min":3,"qc_required":True},
                {"step":2,"process":"缝制","machine":"平缝机","time_min":6,"qc_required":False},
                {"step":3,"process":"质检","machine":"-","time_min":2,"qc_required":True},
                {"step":4,"process":"包装","machine":"-","time_min":1,"qc_required":False},
            ], total_time_min=12),
        ]
        db.add_all(process_templates)

        db.commit()

        # 统计
        from sqlalchemy import func
        print("[OK] Rich seed data created!")
        print(f"  Styles:     {db.query(Style).count()}")
        print(f"  Lines:      {db.query(ProductionLine).count()}")
        print(f"  Orders:     {db.query(Order).count()} ({db.query(Order).filter(Order.status=='PENDING').count()} PENDING, {db.query(Order).filter(Order.status=='SCHEDULED').count()} SCHEDULED, {db.query(Order).filter(Order.status=='IN_PROGRESS').count()} IN_PROGRESS, {db.query(Order).filter(Order.status=='COMPLETED').count()} COMPLETED, {db.query(Order).filter(Order.status=='DELAYED').count()} DELAYED)")
        print(f"  Materials:  {db.query(Material).count()}")
        print(f"  Piecework:  {db.query(PieceWorkRecord).count()} records")
        print(f"  Progress:   {db.query(OrderProgress).count()} orders tracked")


if __name__ == "__main__":
    seed()
