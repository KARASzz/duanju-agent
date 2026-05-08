"""
前置决策中台 CLI

用法:
    python -m scripts.preflight "都市复仇"
    python -m scripts.preflight "穿越奇幻" --format ai
    python -m scripts.preflight "战神" --format mixed --author my_id
"""
import argparse
import json
import os
import sys

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pre_hub.pre_hub import PreHubOrchestrator
from pre_hub.schemas.pre_hub_models import FormatLane


def main():
    parser = argparse.ArgumentParser(description="前置决策中台 - 项目准入评审")
    parser.add_argument("topic", type=str, help="项目题材/关键词")
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["real", "ai", "mixed"],
        default="real",
        help="制作形态: real=真人精品, ai=AI奇观, mixed=混合辅助"
    )
    parser.add_argument(
        "--author",
        type=str,
        default="default",
        help="作者ID"
    )
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="禁用RAG增强"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="输出文件路径 (默认打印到控制台)"
    )
    parser.add_argument(
        "--save-bundle",
        type=str,
        help="保存ContextBundle到指定文件"
    )

    args = parser.parse_args()

    # 转换 format
    format_map = {
        "real": FormatLane.REAL,
        "ai": FormatLane.AI,
        "mixed": FormatLane.MIXED,
    }
    format_lane = format_map[args.format]

    print(f"[PreFlight] 启动前置评审: topic={args.topic}, format={args.format}")
    print("=" * 60)

    # 运行前置中台
    orchestrator = PreHubOrchestrator()
    bundle = orchestrator.run(
        topic=args.topic,
        format_lane=format_lane,
        author_id=args.author,
        use_rag=not args.no_rag,
    )

    # 输出准入结果
    passport = bundle.preflight_passport
    capsule = bundle.project_capsule

    print("\n" + "=" * 60)
    print("[PREFLIGHT PASSPORT] 准入护照")
    print("=" * 60)
    print(f"项目ID: {capsule.project_id}")
    print(f"项目标题: {capsule.project_title}")
    print(f"准入状态: {'[PASS] 通过' if passport.is_pass else '[FAIL] 拒绝'}")
    print(f"总分: {passport.total_score}/100")
    print(f"过期时间: {passport.expiry_at.strftime('%Y-%m-%d %H:%M')}")

    print("\n各关卡得分:")
    for gate, score in passport.gate_scores.items():
        bar = "#" * (score // 10) + "-" * (10 - score // 10)
        print(f"  {gate}: {bar} {score}")

    if passport.blocking_issues:
        print(f"\n[BLOCKING] 阻塞问题 ({len(passport.blocking_issues)}):")
        for issue in passport.blocking_issues:
            print(f"  - {issue}")

    if passport.required_actions:
        print(f"\n[TODO] 必须修复项 ({len(passport.required_actions)}):")
        for action in passport.required_actions:
            print(f"  - {action}")

    # 输出给流水线的注入内容
    print("\n" + "=" * 60)
    print("[CONTEXT BUNDLE] 注入给流水线的上下文")
    print("=" * 60)
    print(bundle.to_injection_prompt()[:500] + "..." if len(bundle.to_injection_prompt()) > 500 else bundle.to_injection_prompt())

    # 保存bundle
    if args.save_bundle:
        bundle_path = os.path.join(args.save_bundle, f"bundle_{capsule.project_id}.json")
        with open(bundle_path, "w", encoding="utf-8") as f:
            json.dump(bundle.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
        print(f"\n💾 Bundle已保存: {bundle_path}")

    # 输出到文件
    if args.output:
        report = f"""# 前置决策报告

## 项目信息
- 项目ID: {capsule.project_id}
- 标题: {capsule.project_title}
- 题材: {args.topic}
- 制作形态: {format_lane.value}
- 作者: {args.author}

## 准入结果
- 状态: {'[PASS] 通过' if passport.is_pass else '[FAIL] 拒绝'}
- 总分: {passport.total_score}/100
- 过期时间: {passport.expiry_at.strftime('%Y-%m-%d %H:%M')}

## 各关卡得分
{chr(10).join(f'- {gate}: {score}' for gate, score in passport.gate_scores.items())}

## 阻塞问题
{chr(10).join(f'- {i}' for i in passport.blocking_issues) if passport.blocking_issues else '无'}

## 必须修复项
{chr(10).join(f'- {a}' for a in passport.required_actions) if passport.required_actions else '无'}

## 流水线注入内容
{bundle.to_injection_prompt()}
"""
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📄 报告已保存: {args.output}")

    print("\n" + "=" * 60)
    if passport.is_pass:
        print("[SUCCESS] 项目通过准入，可以使用 ContextBundle 继续主流水线！")
    else:
        print("[WARNING] 项目未通过准入，请根据要求修复后重新评审")

    return 0 if passport.is_pass else 1


if __name__ == "__main__":
    sys.exit(main())
