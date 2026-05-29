"""
RAG 知识检索服务（轻量版）
使用关键词匹配 + 简单语义相似度，无需外部向量数据库
"""
import json
import re
from typing import Optional


class KnowledgeBase:
    """工艺标准 + SOP 知识库"""

    def __init__(self):
        self.documents: list[dict] = []
        self._load()

    def _load(self):
        """加载知识库数据"""
        self.documents = CRAFT_STANDARDS + SOP_DOCUMENTS

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """搜索最相关的文档"""
        scored = []
        query_lower = query.lower()
        query_chars = set(query_lower)

        for doc in self.documents:
            score = self._score(query_lower, query_chars, doc)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def _score(self, query: str, query_chars: set, doc: dict) -> float:
        """简单评分：关键词匹配 + 字符重叠"""
        text = (doc.get("title", "") + " " + doc.get("content", "") + " " +
                " ".join(doc.get("tags", []))).lower()

        # 精确关键词匹配
        score = 0
        for tag in doc.get("tags", []):
            if tag.lower() in query:
                score += 10
        for kw in doc.get("keywords", []):
            if kw.lower() in query:
                score += 8

        # 标题匹配
        if doc.get("title", "").lower() in query:
            score += 15

        # 字符重叠率
        text_chars = set(text)
        if query_chars:
            overlap = len(query_chars & text_chars) / len(query_chars)
            score += overlap * 3

        return score

    def add(self, title: str, content: str, tags: list[str] = None, keywords: list[str] = None):
        self.documents.append({
            "title": title, "content": content,
            "tags": tags or [], "keywords": keywords or [],
        })


# ── 工艺标准数据 ────────────────────────────────────────
CRAFT_STANDARDS: list[dict] = [
    {
        "title": "蕾丝面料裁剪规范",
        "content": "蕾丝面料裁剪前需自然松弛24小时。裁剪时注意花纹对齐，单层裁剪不可叠层。刀片需锋利，每500件更换一次刀片。裁片误差控制在±2mm以内。",
        "tags": ["裁剪", "蕾丝", "面料", "刀片"],
        "keywords": ["蕾丝", "裁剪", "面料处理", "刀片更换"],
    },
    {
        "title": "内衣缝制质量标准",
        "content": "缝制针距要求：平缝12-14针/3cm，包缝10-12针/3cm。肩带缝合处需回针加固3次。背钩安装需加衬布加固。缝线颜色必须与面料一致。断线接头不可出现在正面。",
        "tags": ["缝制", "质量", "针距", "肩带", "背钩"],
        "keywords": ["缝制", "针距", "质量", "肩带", "背钩", "断线"],
    },
    {
        "title": "面料缩水处理标准",
        "content": "纯棉面料缩水率约5-8%，蕾丝面料缩水率约2-3%，弹力面料缩水率约3-5%。所有面料裁剪前必须预缩处理：40°C温水浸泡30分钟→自然晾干→熨烫平整。不可跳过预缩步骤。",
        "tags": ["面料", "缩水", "预缩", "处理"],
        "keywords": ["缩水", "面料", "预缩", "纯棉", "蕾丝", "弹力", "浸泡"],
    },
    {
        "title": "质检工序标准",
        "content": "质检分为三步：1）外观检查：无线头、无污渍、无色差、花纹对称；2）尺寸检查：各部位尺寸误差±5mm；3）功能检查：肩带弹性测试、背钩开合测试10次。AQL抽样标准：AQL2.5正常检验。",
        "tags": ["质检", "标准", "AQL", "尺寸"],
        "keywords": ["质检", "检查", "AQL", "尺寸", "外观", "功能"],
    },
    {
        "title": "包装出货标准",
        "content": "每件独立包装袋封装，加防潮剂。吊牌挂在左肩带。每箱装50件，箱内垫防潮纸。箱外贴标签：款号、色号、尺码、数量、箱号。外箱用打包带十字捆扎。",
        "tags": ["包装", "出货", "吊牌", "装箱"],
        "keywords": ["包装", "装箱", "出货", "吊牌", "标签"],
    },
    {
        "title": "缝制设备日常维护",
        "content": "平缝机每日清理梭床毛絮，每8小时加一次机油。包缝机每4小时清理一次刀片碎料。设备异常响动立即停机报修。月保养：更换机针、清理电机散热口。",
        "tags": ["设备", "维护", "平缝机", "包缝机"],
        "keywords": ["设备", "维护", "保养", "机针", "机油", "清理"],
    },
]

# ── SOP 异常处理文档 ─────────────────────────────────────
SOP_DOCUMENTS: list[dict] = [
    {
        "title": "SOP-001: 订单延期处理流程",
        "content": "当检测到订单将延期时：1）立即通知销售与客户沟通，确认能否接受新交期；2）评估能否通过加班/加人/外发赶工；3）调整排产计划，将延期订单优先级提升；4）记录延期原因到exception_events表；5）每日跟进进度直至交付。",
        "tags": ["SOP", "延期", "订单", "处理"],
        "keywords": ["延期", "超期", "赶工", "加班", "外发"],
    },
    {
        "title": "SOP-002: 质量问题处理流程",
        "content": "发现批量质量问题时：1）立即停线，通知质检主管和车间主任；2）隔离问题批次，标识清晰；3）追溯问题工序和责任人；4）评估返工工时和成本；5）分析根因并更新工艺标准。问题未解决前不得复产。",
        "tags": ["SOP", "质量", "停线", "返工"],
        "keywords": ["质量", "问题", "停线", "返工", "追溯", "隔离"],
    },
    {
        "title": "SOP-003: 设备故障应急处理",
        "content": "设备故障时：1）操作工立即停机；2）挂'故障待修'标识牌；3）通知设备维修组，描述故障现象；4）预估修复时间，超过4小时需协调其他产线调配；5）记录故障时长到exception_events表。",
        "tags": ["SOP", "设备", "故障", "应急"],
        "keywords": ["设备故障", "停机", "维修", "标识"],
    },
    {
        "title": "SOP-004: 客户插单处理流程",
        "content": "客户要求插单时：1）确认款式、数量和交期；2）运行插单模拟，评估影响；3）如果影响A级客户订单，需厂长审批；4）如果仅影响普通订单且延期≤3天，助理可直接确认；5）插单确认后排入产线并通知相关销售。",
        "tags": ["SOP", "插单", "客户", "审批"],
        "keywords": ["插单", "插入", "加急", "审批"],
    },
    {
        "title": "SOP-005: 缺料应急处理",
        "content": "物料库存低于安全库存时：1）立即通知采购下紧急订单；2）检查在途订单，催促供应商确认交期；3）如果影响在产订单，评估替代物料可行性；4）调整排产计划，将缺料订单后移；5）记录缺料事件到exception_events。",
        "tags": ["SOP", "缺料", "采购", "应急"],
        "keywords": ["缺料", "库存不足", "采购", "紧急", "替代"],
    },
]


# 全局单例
_kb: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


def search_knowledge(query: str, top_k: int = 3) -> list[dict]:
    return get_knowledge_base().search(query, top_k)
