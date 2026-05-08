"""
前置决策中台 - 核心数据模型

定义7层前置工作流所需的所有数据结构
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============ 枚举定义 ============

class ContentLane(str, Enum):
    """内容赛道"""
    STABLE_HIT = "保底爆款"       # 逆袭/情感复仇/女强修正
    RISING_MIX = "上升混搭"       # 穿越+情感/奇幻+亲情
    INNOVATION_PREMIUM = "创新精品"  # 民国传奇/悬疑现实


class FormatLane(str, Enum):
    """制作形态"""
    REAL = "真人精品"
    AI = "AI奇观"
    MIXED = "混合辅助"


class SourceTier(str, Enum):
    """信源分级"""
    OFFICIAL = "official"           # 官方平台
    MAINSTREAM = "mainstream"       # 主流媒体
    THIRD_PARTY = "third_party"     # 第三方数据
    INDUSTRY = "industry_media"     # 行业媒体
    SELF_MEDIA = "self_media"      # 自媒体


class AudienceZone(str, Enum):
    """受众敏感区域"""
    IMMUNE = "免疫区"        # 已不刺激
    FATIGUED = "疲惫区"      # 能看但不值钱
    HIGH_SENSITIVE = "高敏区"  # 轻微触发就能停留
    INTEGRATABLE = "可整合惊讶带"  # 最值得打
    OVERLOAD = "过载区"      # 直接弃


class ViewingMode(str, Enum):
    """观看形态"""
    REAL_EMOTION = "真人情绪型"
    REAL_RELATION = "真人关系型"
    AI_SPEC = "AI奇观型"
    SERIES_ADDICT = "系列成瘾型"
    SINGLE_BURST = "单部爆发型"


class RewriteDecision(str, Enum):
    """重写/淘汰决定"""
    PASS = "pass"
    REWRITE = "rewrite"
    KILL = "kill"


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """趋势方向"""
    UP = "up"
    FLAT = "flat"
    DOWN = "down"


# ============ 基础数据结构 ============

class SourceConfidenceItem(BaseModel):
    """信源可信度项"""
    source_name: str
    source_tier: SourceTier
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    published_at: Optional[str] = None
    is_fact: bool = True
    evidence_refs: List[str] = []


class HeatmapItem(BaseModel):
    """热力图项"""
    label: str
    score: int = Field(0, ge=0, le=100)
    trend: TrendDirection = TrendDirection.FLAT
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class FormatFitItem(BaseModel):
    """形态适配项"""
    format_lane: FormatLane
    fit_score: int = Field(0, ge=0, le=100)
    reasons: List[str] = []


class BayesiaFreeEnergyScore(BaseModel):
    """贝叶斯自由能评分"""
    surprise_score: float = Field(0.0, ge=0.0, le=1.0)
    confusion_score: float = Field(0.0, ge=0.0, le=1.0)
    integration_score: float = Field(0.0, ge=0.0, le=1.0)
    overall_score: float = Field(0.0, ge=0.0, le=1.0)


class AudiencePriorMatrix(BaseModel):
    """受众先验矩阵"""
    zone_distribution: Dict[AudienceZone, float] = {}
    viewing_mode_scores: Dict[ViewingMode, float] = {}
    integration_threshold: float = 0.7


class RouteDecision(BaseModel):
    """路由决策"""
    content_lane: ContentLane
    format_lane: FormatLane
    decision_rationale: str
    route_confidence: float = Field(0.0, ge=0.0, le=1.0)
    forbidden_cliche: List[str] = []
    production_burden: str = "medium"


class BranchScore(BaseModel):
    """方案评分"""
    branch_id: str
    branch_description: str
    platform_fit: int = Field(0, ge=0, le=100)
    hook_density: int = Field(0, ge=0, le=100)
    ip_potential: int = Field(0, ge=0, le=100)
    producibility: int = Field(0, ge=0, le=100)
    rights_risk: int = Field(0, ge=0, le=100)
    total_score: int = Field(0, ge=0, le=500)
    verdict: str = "unknown"  # winner/runner_up/kill


class NarrativeGraphNode(BaseModel):
    """叙事图谱节点"""
    node_id: str
    node_type: str  # character/conflict/plot_point/hook/cliffhanger
    content: str
    episode_range: str = ""  # e.g., "1-5"
    dependencies: List[str] = []


class HookNode(BaseModel):
    """钩子节点"""
    episode_no: int
    hook_type: str  # 悬念型/反转型/冲突升级型/情绪临界型
    hook_text: str
    intensity: int = Field(0, ge=0, le=100)
    emotional_debt_raised: int = 0  # 建立的债
    emotional_debt_repaid: int = 0  # 偿还的债


class RiskItem(BaseModel):
    """风险项"""
    category: str  # rights/compliance/production/market
    level: RiskLevel
    description: str
    mitigation: Optional[str] = None


# ============ Layer 输出包 ============

class Layer0Output(BaseModel):
    """Layer0 信源净化输出"""
    cleaned_sources: List[Dict[str, Any]] = []
    source_confidence_map: List[SourceConfidenceItem] = []
    metric_normalization_note: Dict[str, str] = {}
    content_form_tags: List[str] = []  # 真人短剧/AI奇观/混合
    rights_risk_signals: List[str] = []


class Layer1Output(BaseModel):
    """Layer1 市场雷达输出"""
    platform_state_snapshot: Dict[str, Any] = {}
    lane_heatmap: List[HeatmapItem] = []
    format_fit_map: List[FormatFitItem] = []
    innovation_opportunity_map: List[HeatmapItem] = []
    risk_heatmap: List[HeatmapItem] = []
    bayesian_scores: Optional[BayesiaFreeEnergyScore] = None


class Layer2Output(BaseModel):
    """Layer2 受众建模输出"""
    audience_prior_matrix: AudiencePriorMatrix
    prediction_error_band: Dict[str, Any] = {}
    viewing_mode_scores: Dict[ViewingMode, float] = {}
    audience_segment_fit: Dict[str, float] = {}
    redfruit_fit_hypothesis: str = ""


class Layer3Output(BaseModel):
    """Layer3 赛道分流输出"""
    route_decision: RouteDecision
    route_matrix_scorecard: List[BranchScore] = []


class Layer4Output(BaseModel):
    """Layer4 概念竞技输出"""
    concept_branches: List[Dict[str, Any]] = []
    branch_scorecard: List[BranchScore] = []
    winner_branch: Optional[BranchScore] = None
    runner_up_branch: Optional[BranchScore] = None
    kill_list: List[Dict[str, str]] = []  # {branch_id, reason}


class Layer5Output(BaseModel):
    """Layer5 叙事图谱输出"""
    narrative_graph: List[NarrativeGraphNode] = []
    knowledge_state_map: List[Dict[str, Any]] = []
    emotional_debt_ledger: List[Dict[str, Any]] = []
    hook_chain_map: List[HookNode] = []
    format_constraint_sheet: Dict[str, Any] = {}
    rights_compliance_stub: Dict[str, Any] = {}


class Layer6Output(BaseModel):
    """Layer6 对抗验证输出"""
    adversarial_report: Dict[str, Any] = {}
    fatal_flaw_list: List[RiskItem] = []
    route_mismatch_flag: bool = False
    rights_risk_pack: List[RiskItem] = []
    rewrite_or_kill: RewriteDecision = RewriteDecision.PASS
    must_fix_before_prod: List[str] = []


class Layer7Output(BaseModel):
    """Layer7 生产准入输出"""
    preflight_passport: "PreflightPassport"
    context_bundle: "ContextBundleForParser"


# ============ 核心数据包 ============

class ProjectCapsule(BaseModel):
    """项目胶囊"""
    project_id: str
    author_id: str = "default"
    project_title: str
    one_line_premise: str = ""
    theme_tags: List[str] = []
    emotion_core: str = ""
    visual_core: str = ""
    target_platform: str = "redfruit"
    target_episode_count: int = Field(60, ge=20, le=120)
    target_duration_sec: int = Field(90, ge=60, le=180)
    preferred_format: FormatLane = FormatLane.REAL
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MarketContextPack(BaseModel):
    """市场上下文包"""
    pack_id: str
    project_id: str
    as_of_date: str
    market_window_days: int = 90
    source_confidence_map: List[SourceConfidenceItem] = []
    lane_heatmap: List[HeatmapItem] = []
    format_fit_map: List[FormatFitItem] = []
    risk_heatmap: List[HeatmapItem] = []
    bayesian_scores: Optional[BayesiaFreeEnergyScore] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class NarrativeSeedPack(BaseModel):
    """叙事种子包"""
    pack_id: str
    project_id: str
    winner_branch: Optional[BranchScore] = None
    narrative_graph: List[NarrativeGraphNode] = []
    knowledge_state_map: List[Dict[str, Any]] = []
    emotional_debt_ledger: List[Dict[str, Any]] = []
    hook_chain_map: List[HookNode] = []
    format_constraint: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RiskPack(BaseModel):
    """风险包"""
    pack_id: str
    project_id: str
    rights_risks: List[RiskItem] = []
    compliance_flags: List[str] = []
    fatal_flaw_list: List[RiskItem] = []
    adversarial_report: Dict[str, Any] = {}
    rewrite_or_kill: RewriteDecision = RewriteDecision.PASS
    must_fix_before_prod: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PreflightPassport(BaseModel):
    """准入护照"""
    passport_id: str
    project_id: str
    is_pass: bool = False
    total_score: int = Field(0, ge=0, le=100)
    gate_scores: Dict[str, int] = {}  # 各关卡得分
    blocking_issues: List[str] = []
    required_actions: List[str] = []
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expiry_at: datetime


class ContextBundleForParser(BaseModel):
    """喂给现有流水线的总包"""
    bundle_id: str
    project_id: str
    project_capsule: ProjectCapsule
    market_context: MarketContextPack
    narrative_seed: NarrativeSeedPack
    risk_pack: RiskPack
    preflight_passport: PreflightPassport
    prompt_injection: Dict[str, str] = {}
    token_budget: Dict[str, int] = {}
    integrity_hash: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_injection_prompt(self) -> str:
        """生成注入到 parser 的 system prompt"""
        capsule = self.project_capsule
        market = self.market_context
        narrative = self.narrative_seed
        risk = self.risk_pack

        lines = [
            "=== 项目背景 ===",
            f"项目ID: {capsule.project_id}",
            f"标题: {capsule.project_title}",
            f"一句话: {capsule.one_line_premise}",
            f"情绪核心: {capsule.emotion_core}",
            f"视觉核心: {capsule.visual_core}",
            f"目标平台: {capsule.target_platform}",
            f"集数: {capsule.target_episode_count}集",
            f"单集时长: {capsule.target_duration_sec}秒",
            f"制作形态: {capsule.preferred_format.value if capsule.preferred_format else 'auto'}",
            "",
            "=== 市场上下文 ===",
            f"数据日期: {market.as_of_date}",
        ]

        if market.bayesian_scores:
            bs = market.bayesian_scores
            lines.append(f"贝叶斯评分: 新鲜度={bs.surprise_score:.2f}, 困惑度={bs.confusion_score:.2f}, 可整合度={bs.integration_score:.2f}")

        lines.extend([
            "",
            "=== 赛道与形态决策 ===",
            f"内容赛道: {narrative.winner_branch.branch_description if narrative.winner_branch else '待定'}",
        ])

        if risk.compliance_flags:
            lines.append(f"合规注意: {', '.join(risk.compliance_flags)}")

        if risk.must_fix_before_prod:
            lines.append(f"生产前必须修复: {', '.join(risk.must_fix_before_prod)}")

        lines.extend([
            "",
            "=== 写作约束 ===",
            f"禁用套路: {narrative.format_constraint.get('forbidden_cliche', '无')}" if narrative.format_constraint else "",
        ])

        return "\n".join(filter(None, lines))


# 解决 forward reference
Layer7Output.model_rebuild()
PreflightPassport.model_rebuild()
ContextBundleForParser.model_rebuild()
