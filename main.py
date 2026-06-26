from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="学伴 Study Agent - 主动服务型学习 AI Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="生成学习计划")
    plan.add_argument("--course", required=True, help="课程名称，例如：高等数学")
    plan.add_argument("--exam-date", required=True, help="考试日期，格式：YYYY-MM-DD")
    plan.add_argument("--daily-hours", type=float, default=2.0, help="每日可投入学习时长")

    mistake = subparsers.add_parser("mistake", help="分析错题")
    mistake.add_argument("--course", default="未指定课程", help="课程名称")
    mistake.add_argument("--description", required=True, help="错题描述")

    summary = subparsers.add_parser("summary", help="生成学习总结")
    summary.add_argument("--content", required=True, help="今日学习内容")

    proactive = subparsers.add_parser("proactive", help="生成主动提醒卡片")
    proactive.add_argument("--simulate", action="store_true", help="模拟一天中的所有时间触发")

    subparsers.add_parser("demo", help="运行完整演示流程")
    return parser


def run_demo() -> None:
    from study_agent.agents.mistake_analyzer import MistakeAnalysisAgent
    from study_agent.agents.planner import LearningPlanAgent
    from study_agent.agents.summary_agent import LearningSummaryAgent
    from study_agent.memory.storage import JsonMemoryStore
    from study_agent.scheduler.proactive_scheduler import ProactiveScheduler
    from study_agent.utils.json_tools import pretty_json

    memory = JsonMemoryStore()
    planner = LearningPlanAgent(memory=memory)
    mistake_agent = MistakeAnalysisAgent(memory=memory)
    summary_agent = LearningSummaryAgent(memory=memory)
    scheduler = ProactiveScheduler(memory=memory)

    print("\n[1/4] 错题分析 Agent")
    print(
        pretty_json(
            mistake_agent.analyze(
                course="高等数学",
                description="在极限计算题中看错等价无穷小的使用条件，公式套错，最后符号也算错。",
            )
        )
    )

    print("\n[2/4] 学习计划生成 Agent")
    print(pretty_json(planner.generate(course="高等数学", exam_date="2026-07-10", daily_hours=2.5)))

    print("\n[3/4] 学习总结 Agent")
    print(pretty_json(summary_agent.summarize("复习了极限、连续和导数定义，做了 12 道题，其中等价无穷小和洛必达法则还不稳定。")))

    print("\n[4/4] 主动提醒 Scheduler")
    print(pretty_json(scheduler.generate_cards(simulate=True)))


def main() -> None:
    from study_agent.agents.mistake_analyzer import MistakeAnalysisAgent
    from study_agent.agents.planner import LearningPlanAgent
    from study_agent.agents.summary_agent import LearningSummaryAgent
    from study_agent.memory.storage import JsonMemoryStore
    from study_agent.scheduler.proactive_scheduler import ProactiveScheduler
    from study_agent.utils.json_tools import pretty_json

    parser = build_parser()
    args = parser.parse_args()

    memory = JsonMemoryStore()

    if args.command == "plan":
        result = LearningPlanAgent(memory=memory).generate(args.course, args.exam_date, args.daily_hours)
    elif args.command == "mistake":
        result = MistakeAnalysisAgent(memory=memory).analyze(args.description, args.course)
    elif args.command == "summary":
        result = LearningSummaryAgent(memory=memory).summarize(args.content)
    elif args.command == "proactive":
        result = ProactiveScheduler(memory=memory).generate_cards(simulate=args.simulate)
    elif args.command == "demo":
        run_demo()
        return
    else:
        parser.error("未知命令")
        return

    print(pretty_json(result))


if __name__ == "__main__":
    main()
