"""
前置决策中台 - 主协调器

负责串联7层工作流，协调各层输入输出
"""
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pre_hub.schemas.pre_hub_models import (
    AudiencePriorMatrix,
    AudienceZone,
    BayesiaFreeEnergyScore,
    BranchScore,
    ContentLane,
    ContextBundleForParser,
    FormatFitItem,
    FormatLane,
    HeatmapItem,
    HookNode,
    Layer0Output,
    Layer1Output,
    Layer2Output,
    Layer3Output,
    Layer4Output,
    Layer5Output,
    Layer6Output,
    Layer7Output,
    MarketContextPack,
    NarrativeGraphNode,
    NarrativeSeedPack,
    PreflightPassport,
    ProjectCapsule,
    RiskItem,
    RiskLevel,
    RiskPack,
    RewriteDecision,
    RouteDecision,
    SourceConfidenceItem,
    TrendDirection,
    ViewingMode,
)


class PreHubOrchestrator:
    """
    前置决策中台协调器

    使用方式:
        orchestrator = PreHubOrchestrator()
        bundle = orchestrator.run("都市复仇", format_lane=FormatLane.REAL)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.project_id = str(uuid.uuid4())[:8]

    def run(
        self,
        topic: str,
        format_lane: FormatLane = FormatLane.REAL,
        author_id: str = "default",
        use_rag: bool = True,
    ) -> ContextBundleForParser:
        """
        运行完整的前置决策流程

        Args:
            topic: 项目题材/关键词
            format_lane: 制作形态偏好
            author_id: 作者ID
            use_rag: 是否使用RAG增强

        Returns:
            ContextBundleForParser: 喂给现有流水线的总包
        """
        print(f"[PreHub] Starting pre-flight for topic: {topic}")

        # Layer 0: 信源净化
        l0_output = self._run_layer0(topic)
        print(f"[PreHub] Layer0 done: {len(l0_output.cleaned_sources)} sources cleaned")

        # Layer 1: 市场雷达
        l1_output = self._run_layer1(topic, l0_output)
        print(f"[PreHub] Layer1 done: {len(l1_output.lane_heatmap)} lanes analyzed")

        # Layer 2: 受众建模
        l2_output = self._run_layer2(topic, l1_output)
        print(f"[PreHub] Layer2 done: audience matrix built")

        # Layer 3: 赛道分流
        l3_output = self._run_layer3(topic, l2_output, format_lane)
        print(f"[PreHub] Layer3 done: route decided - {l3_output.route_decision.content_lane.value}")

        # Layer 4: 概念竞技
        l4_output = self._run_layer4(topic, l3_output)
        print(f"[PreHub] Layer4 done: winner branch - {l4_output.winner_branch.branch_id if l4_output.winner_branch else 'N/A'}")

        # Layer 5: 叙事图谱
        l5_output = self._run_layer5(l4_output)
        print(f"[PreHub] Layer5 done: {len(l5_output.narrative_graph)} graph nodes")

        # Layer 6: 对抗验证
        l6_output = self._run_layer6(l5_output, l3_output)
        print(f"[PreHub] Layer6 done: {l6_output.rewrite_or_kill.value}")

        # Layer 7: 生产准入
        l7_output = self._run_layer7(
            topic, author_id, l0_output, l1_output, l2_output,
            l3_output, l4_output, l5_output, l6_output
        )
        print(f"[PreHub] Layer7 done: passport issued - {l7_output.preflight_passport.is_pass}")

        return l7_output.context_bundle

    def _run_layer0(self, topic: str) -> Layer0Output:
        """Layer 0: 信源净化"""
        from pre_hub.layer0_source_guard.source_cleaner import SourceCleaner

        # 使用 Tavily 搜索获取原始数据
        raw_results = self._tavily_search(topic)

        # 净化
        cleaner = SourceCleaner(min_published_days=90)
        return cleaner.clean(raw_results)

    def _run_layer1(self, topic: str, l0_input: Layer0Output) -> Layer1Output:
        """Layer 1: 平台市场雷达"""
        # 构建赛道热力图
        lanes = [
            ("逆袭", 85, TrendDirection.UP),
            ("情感复仇", 80, TrendDirection.FLAT),
            ("女强修正", 75, TrendDirection.UP),
            ("穿越", 70, TrendDirection.DOWN),
            ("奇幻", 65, TrendDirection.UP),
            ("悬疑", 60, TrendDirection.FLAT),
        ]
        lane_heatmap = [
            HeatmapItem(label=name, score=score, trend=trend)
            for name, score, trend in lanes
        ]

        # 形态适配图
        format_fit_map = [
            FormatFitItem(format_lane=FormatLane.REAL, fit_score=85, reasons=["情感真实", "演员表演"]),
            FormatFitItem(format_lane=FormatLane.AI, fit_score=60, reasons=["视觉奇观", "成本优势"]),
            FormatFitItem(format_lane=FormatLane.MIXED, fit_score=70, reasons=["灵活适配"]),
        ]

        # 风险热区
        risk_heatmap = [
            HeatmapItem(label="IP改编边界", score=75, trend=TrendDirection.UP),
            HeatmapItem(label="AI素材合规", score=60, trend=TrendDirection.UP),
            HeatmapItem(label="同质化竞争", score=80, trend=TrendDirection.FLAT),
        ]

        # 贝叶斯自由能评分
        bayesian = BayesiaFreeEnergyScore(
            surprise_score=0.65,
            confusion_score=0.25,
            integration_score=0.72,
            overall_score=0.70,
        )

        return Layer1Output(
            platform_state_snapshot={"platform": "redfruit", "period": "2026Q1"},
            lane_heatmap=lane_heatmap,
            format_fit_map=format_fit_map,
            innovation_opportunity_map=[],
            risk_heatmap=risk_heatmap,
            bayesian_scores=bayesian,
        )

    def _run_layer2(self, topic: str, l1_input: Layer1Output) -> Layer2Output:
        """Layer 2: 受众先验建模"""
        # 简化实现：基于市场雷达输出构建受众矩阵
        matrix = AudiencePriorMatrix(
            zone_distribution={
                AudienceZone.HIGH_SENSITIVE: 0.35,
                AudienceZone.INTEGRATABLE: 0.30,
                AudienceZone.FATIGUED: 0.20,
                AudienceZone.IMMUNE: 0.10,
                AudienceZone.OVERLOAD: 0.05,
            },
            viewing_mode_scores={
                ViewingMode.REAL_EMOTION: 0.80,
                ViewingMode.SERIES_ADDICT: 0.65,
                ViewingMode.AI_SPEC: 0.45,
                ViewingMode.REAL_RELATION: 0.70,
                ViewingMode.SINGLE_BURST: 0.55,
            },
            integration_threshold=0.65,
        )

        return Layer2Output(
            audience_prior_matrix=matrix,
            prediction_error_band={"tolerance": 0.3, "ideal_range": "60-90s"},
            viewing_mode_scores=matrix.viewing_mode_scores,
            audience_segment_fit={
                "高频短剧用户": 0.75,
                "泛用户": 0.60,
                "AI尝鲜用户": 0.40,
            },
            redfruit_fit_hypothesis="高情绪代偿+强反转+清晰人物弧光",
        )

    def _run_layer3(
        self, topic: str, l2_input: Layer2Output, preferred_format: FormatLane
    ) -> Layer3Output:
        """Layer 3: 赛道分流"""
        # 基于题材判断内容赛道
        topic_lower = topic.lower()
        if any(k in topic_lower for k in ["逆袭", "复仇", "女强", "霸总"]):
            content_lane = ContentLane.STABLE_HIT
        elif any(k in topic_lower for k in ["穿越", "奇幻", "系统"]):
            content_lane = ContentLane.RISING_MIX
        else:
            content_lane = ContentLane.INNOVATION_PREMIUM

        route = RouteDecision(
            content_lane=content_lane,
            format_lane=preferred_format,
            decision_rationale=f"基于题材'{topic}'和市场分析，推荐'{content_lane.value}'赛道",
            route_confidence=0.75,
            forbidden_cliche=["渣男贱女标配", "五年契约", "失忆梗"],
            production_burden="medium",
        )

        return Layer3Output(
            route_decision=route,
            route_matrix_scorecard=[],
        )

    def _run_layer4(self, topic: str, l3_input: Layer3Output) -> Layer4Output:
        """Layer 4: 高概念竞技场"""
        # 生成3个候选方案
        branches = [
            BranchScore(
                branch_id="A",
                branch_description=f"{topic}：经典逆袭线",
                platform_fit=85,
                hook_density=80,
                ip_potential=70,
                producibility=90,
                rights_risk=20,
                total_score=345,
                verdict="winner",
            ),
            BranchScore(
                branch_id="B",
                branch_description=f"{topic}：高概念设定线",
                platform_fit=75,
                hook_density=90,
                ip_potential=85,
                producibility=60,
                rights_risk=40,
                total_score=350,
                verdict="runner_up",
            ),
            BranchScore(
                branch_id="C",
                branch_description=f"{topic}：情感深度线",
                platform_fit=70,
                hook_density=65,
                ip_potential=75,
                producibility=85,
                rights_risk=15,
                total_score=310,
                verdict="kill",
            ),
        ]

        return Layer4Output(
            concept_branches=[{"id": b.branch_id, "desc": b.branch_description} for b in branches],
            branch_scorecard=branches,
            winner_branch=branches[0],
            runner_up_branch=branches[1],
            kill_list=[{"branch_id": "C", "reason": "钩子密度不足，难以支撑付费转化"}],
        )

    def _run_layer5(self, l4_input: Layer4Output) -> Layer5Output:
        """Layer 5: 叙事图谱锁定"""
        winner = l4_input.winner_branch
        if not winner:
            return Layer5Output()

        # 构建叙事依赖图
        graph = [
            NarrativeGraphNode(
                node_id="hook_ep1",
                node_type="hook",
                content="开场建立核心冲突/不公",
                episode_range="1",
                dependencies=[],
            ),
            NarrativeGraphNode(
                node_id="char_fMC",
                node_type="character",
                content="建立女主坚韧人设",
                episode_range="1-3",
                dependencies=["hook_ep1"],
            ),
            NarrativeGraphNode(
                node_id="plot_reversal1",
                node_type="plot_point",
                content="第一次反转：身份揭示",
                episode_range="5-7",
                dependencies=["char_fMC"],
            ),
            NarrativeGraphNode(
                node_id="hook_mid",
                node_type="cliffhanger",
                content="中集钩子：大危机",
                episode_range="10",
                dependencies=["plot_reversal1"],
            ),
            NarrativeGraphNode(
                node_id="hook_final",
                node_type="cliffhanger",
                content="大结局：高潮+悬念",
                episode_range="20",
                dependencies=["hook_mid"],
            ),
        ]

        # 钩子链
        hooks = [
            HookNode(episode_no=1, hook_type="冲突升级型", hook_text="开场即冲突", intensity=75),
            HookNode(episode_no=5, hook_type="反转型", hook_text="身份反转", intensity=85),
            HookNode(episode_no=10, hook_type="悬念型", hook_text="危机降临", intensity=90),
            HookNode(episode_no=20, hook_type="情绪临界型", hook_text="高潮+系列钩子", intensity=95),
        ]

        return Layer5Output(
            narrative_graph=graph,
            knowledge_state_map=[],
            emotional_debt_ledger=[],
            hook_chain_map=hooks,
            format_constraint_sheet={"forbidden_cliche": ["失忆梗", "五年契约"]},
            rights_compliance_stub={"needs_auth": [], "high_risk_scenes": []},
        )

    def _run_layer6(self, l5_input: Layer5Output, l3_input: Layer3Output) -> Layer6Output:
        """Layer 6: 对抗验证"""
        # 简化检查清单
        checks = {
            "套路换皮": False,  # 假设检测通过
            "先验击穿": True,   # 假设有击穿
            "情绪负债": True,   # 假设有负债
            "反转合理性": True,
            "系列化潜力": True,
            "真人/AI路线正确": True,
            "平台保底依赖": False,
            "授权风险": False,
            "AI合规": True,
            "值得写": True,
        }

        passed = sum(checks.values())
        fatal_flaws = []
        must_fix = []

        if not checks["先验击穿"]:
            fatal_flaws.append(RiskItem(category="market", level=RiskLevel.HIGH, description="无新鲜感"))
            must_fix.append("增加独特视角")

        if checks["平台保底依赖"]:
            fatal_flaws.append(RiskItem(category="market", level=RiskLevel.MEDIUM, description="过度依赖平台扶持"))
            must_fix.append("强化内容自身竞争力")

        rewrite_decision = (
            RewriteDecision.PASS if passed >= 8
            else RewriteDecision.REWRITE if passed >= 5
            else RewriteDecision.KILL
        )

        return Layer6Output(
            adversarial_report={"checks": checks, "passed_count": passed},
            fatal_flaw_list=fatal_flaws,
            route_mismatch_flag=False,
            rights_risk_pack=[],
            rewrite_or_kill=rewrite_decision,
            must_fix_before_prod=must_fix,
        )

    def _run_layer7(
        self,
        topic: str,
        author_id: str,
        l0: Layer0Output,
        l1: Layer1Output,
        l2: Layer2Output,
        l3: Layer3Output,
        l4: Layer4Output,
        l5: Layer5Output,
        l6: Layer6Output,
    ) -> Layer7Output:
        """Layer 7: 生产准入"""
        project_id = f"proj_{self.project_id}_{int(time.time())}"

        # 构建项目胶囊
        capsule = ProjectCapsule(
            project_id=project_id,
            author_id=author_id,
            project_title=topic,
            one_line_premise=l3.route_decision.decision_rationale,
            emotion_core="高情绪代偿+反转刺激",
            visual_core=l3.route_decision.format_lane.value,
            preferred_format=l3.route_decision.format_lane,
        )

        # 构建市场上下文
        market = MarketContextPack(
            pack_id=f"mkt_{project_id}",
            project_id=project_id,
            as_of_date=datetime.now().strftime("%Y-%m-%d"),
            source_confidence_map=l0.source_confidence_map,
            lane_heatmap=l1.lane_heatmap,
            format_fit_map=l1.format_fit_map,
            risk_heatmap=l1.risk_heatmap,
            bayesian_scores=l1.bayesian_scores,
        )

        # 构建叙事种子
        seed = NarrativeSeedPack(
            pack_id=f"seed_{project_id}",
            project_id=project_id,
            winner_branch=l4.winner_branch,
            narrative_graph=l5.narrative_graph,
            hook_chain_map=l5.hook_chain_map,
            format_constraint=l5.format_constraint_sheet,
        )

        # 构建风险包
        risk = RiskPack(
            pack_id=f"risk_{project_id}",
            project_id=project_id,
            fatal_flaw_list=l6.fatal_flaw_list,
            rights_risk_pack=l6.rights_risk_pack,
            rewrite_or_kill=l6.rewrite_or_kill,
            must_fix_before_prod=l6.must_fix_before_prod,
        )

        # 准入护照
        passed_score = 100 if l6.rewrite_or_kill == RewriteDecision.PASS else (
            60 if l6.rewrite_or_kill == RewriteDecision.REWRITE else 30
        )
        passport = PreflightPassport(
            passport_id=f"pass_{project_id}",
            project_id=project_id,
            is_pass=l6.rewrite_or_kill != RewriteDecision.KILL,
            total_score=passed_score,
            gate_scores={
                "信源净化": 90,
                "市场雷达": 75,
                "受众建模": 70,
                "赛道分流": 80,
                "概念竞技": 85,
                "叙事图谱": 75,
                "对抗验证": passed_score,
            },
            blocking_issues=[f.description for f in l6.fatal_flaw_list],
            required_actions=l6.must_fix_before_prod,
            expiry_at=datetime.now() + timedelta(days=14),
        )

        # 构建总包
        bundle = ContextBundleForParser(
            bundle_id=f"bundle_{project_id}",
            project_id=project_id,
            project_capsule=capsule,
            market_context=market,
            narrative_seed=seed,
            risk_pack=risk,
            preflight_passport=passport,
        )

        # 生成注入prompt
        bundle.prompt_injection = {
            "system_addition": bundle.to_injection_prompt(),
        }

        return Layer7Output(
            preflight_passport=passport,
            context_bundle=bundle,
        )

    def _tavily_search(self, topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Tavily搜索"""
        try:
            from rag_engine.tavily_search import TavilySearcher
            searcher = TavilySearcher()
            results = searcher.search_hot_trends(topic, max_results=max_results)
            return [
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                    "source": r.get("source", ""),
                    "published_at": r.get("published_at", ""),
                }
                for r in results
            ]
        except Exception as e:
            print(f"[PreHub] Tavily search failed: {e}, using mock data")
            return _mock_search_results(topic)


def _mock_search_results(topic: str) -> List[Dict[str, Any]]:
    """模拟搜索结果（当Tavily不可用时）"""
    return [
        {
            "title": f"{topic}赛道分析报告",
            "content": f"2026年{topic}赛道表现强劲,逆袭题材持续领跑,分账金额同比增长40%",
            "url": "https://example.com/report",
            "source": "艾瑞咨询",
            "published_at": "2026-03-15",
        },
        {
            "title": f"红果平台{topic}爆款案例",
            "content": f"近期{topic}题材出现多部爆款,其中《{topic}之王》分账突破500万",
            "url": "https://example.com/case",
            "source": "红果官方",
            "published_at": "2026-03-20",
        },
        {
            "title": f"{topic}创作方法论",
            "content": f"如何写好{topic}题材:1)建立强反差人设 2)前三集必须抛钩子 3)付费点设在第5-7集",
            "url": "https://example.com/method",
            "source": "行业自媒体",
            "published_at": "2026-03-10",
        },
    ]
