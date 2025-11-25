#!/usr/bin/env python3
"""
Run Web Research - Execute knowledge gathering from community sources

This script coordinates the KnowledgeAgent to gather n8n workflows,
error patterns, and best practices from Reddit, YouTube, and Twitter.

Author: Project Automata - Cycle 02
Version: 2.2.0 (Architecture Simplification)
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents import AgentTask
from agents.knowledge import KnowledgeAgent
from skills.knowledge_base import KnowledgeBase


def main():
    """Execute web research across all sources"""

    print("=" * 70)
    print("PROJECT AUTOMATA - KNOWLEDGE GATHERING")
    print("Cycle-02: Community Knowledge Research")
    print("=" * 70)
    print()

    # Check if running in simulation mode
    from config import Config

    allow_simulated = Config.ALLOW_SIMULATED_DATA

    if allow_simulated:
        print("-" * 70)
        print("SIMULATION MODE ENABLED (ALLOW_SIMULATED_DATA=true)")
        print("-" * 70)
        print()
        print("Using built-in sample patterns (developer-curated, not from APIs)")
        print("To use real API data, configure API keys and set flags in .env")
        print()
        print("-" * 70)
        print()

    # Initialize knowledge base and agent
    kb = KnowledgeBase()
    agent = KnowledgeAgent(knowledge_base=kb)

    print(f"📚 Knowledge Base: {kb.base_dir}")
    print(f"🤖 Agent: {agent.name}")
    print(f"🔧 Mode: {'SIMULATION (Sample Data)' if allow_simulated else 'PRODUCTION (Real APIs)'}")
    print()

    # Phase 1: Reddit Research
    print("=" * 70)
    print("PHASE 1: REDDIT RESEARCH")
    print("=" * 70)

    reddit_task = AgentTask(
        task_id="research_reddit_001",
        task_type="research_reddit",
        parameters={
            "queries": ["n8n workflow examples", "n8n error handling", "n8n best practices"]
        },
    )

    print("🔍 Mining Reddit for n8n workflows and solutions...")
    reddit_result = agent.execute(reddit_task)

    if reddit_result.success:
        print(f"✅ {reddit_result.output['summary']}")
        print(f"   - Patterns: {reddit_result.output['patterns_found']}")
        print(f"   - Errors: {reddit_result.output['errors_found']}")
        for finding in reddit_result.output["findings"][:5]:
            print(f"   • {finding}")
        if len(reddit_result.output["findings"]) > 5:
            print(f"   • ... and {len(reddit_result.output['findings']) - 5} more")
    else:
        print(f"❌ Reddit research failed: {reddit_result.reasoning}")

    print()

    # Phase 2: YouTube Research
    print("=" * 70)
    print("PHASE 2: YOUTUBE RESEARCH")
    print("=" * 70)

    youtube_task = AgentTask(
        task_id="research_youtube_001", task_type="research_youtube", parameters={}
    )

    print("🎥 Analyzing YouTube n8n tutorials...")
    youtube_result = agent.execute(youtube_task)

    if youtube_result.success:
        print(f"✅ {youtube_result.output['summary']}")
        print(f"   - Patterns: {youtube_result.output['patterns_found']}")
        print(f"   - Insights: {youtube_result.output['insights_found']}")
        for finding in youtube_result.output["findings"][:5]:
            print(f"   • {finding}")
        if len(youtube_result.output["findings"]) > 5:
            print(f"   • ... and {len(youtube_result.output['findings']) - 5} more")
    else:
        print(f"❌ YouTube research failed: {youtube_result.reasoning}")

    print()

    # Phase 3: Twitter Research
    print("=" * 70)
    print("PHASE 3: TWITTER/X RESEARCH")
    print("=" * 70)

    twitter_task = AgentTask(
        task_id="research_twitter_001", task_type="research_twitter", parameters={}
    )

    print("🐦 Monitoring Twitter/X for n8n tips and patterns...")
    twitter_result = agent.execute(twitter_task)

    if twitter_result.success:
        print(f"✅ {twitter_result.output['summary']}")
        print(f"   - Patterns: {twitter_result.output['patterns_found']}")
        print(f"   - Tips: {twitter_result.output['tips_found']}")
        for finding in twitter_result.output["findings"][:5]:
            print(f"   • {finding}")
        if len(twitter_result.output["findings"]) > 5:
            print(f"   • ... and {len(twitter_result.output['findings']) - 5} more")
    else:
        print(f"❌ Twitter research failed: {twitter_result.reasoning}")

    print()

    # Phase 4: Analysis
    print("=" * 70)
    print("PHASE 4: KNOWLEDGE ANALYSIS")
    print("=" * 70)

    analysis_task = AgentTask(task_id="analyze_001", task_type="analyze_gathered", parameters={})

    print("📊 Analyzing gathered knowledge...")
    analysis_result = agent.execute(analysis_task)

    if analysis_result.success:
        analysis = analysis_result.output
        print(f"✅ {analysis['summary']}")
        print()
        print("📈 STATISTICS:")
        print(f"   - Total Patterns: {analysis['total_patterns']}")
        print(f"   - Total Errors: {analysis['total_errors']}")
        print(f"   - Total Insights: {analysis['total_insights']}")
        print()
        print("🌐 SOURCES:")
        for source, count in analysis["sources"].items():
            print(f"   - {source.capitalize()}: {count} patterns")
        print()
        print("🔝 TOP NODES:")
        for i, (node, count) in enumerate(analysis["top_nodes"][:5], 1):
            print(f"   {i}. {node}: {count} uses")
        print()
        print("📊 COMPLEXITY:")
        for complexity, count in analysis["complexity_distribution"].items():
            print(f"   - {complexity.capitalize()}: {count} patterns")
    else:
        print(f"❌ Analysis failed: {analysis_result.reasoning}")

    print()

    # Generate knowledge base summary
    print("=" * 70)
    print("KNOWLEDGE BASE SUMMARY")
    print("=" * 70)
    print()
    print(kb.export_summary())

    # Save summary to file
    summary_path = os.path.join(kb.base_dir, "summary.md")
    with open(summary_path, "w") as f:
        f.write(kb.export_summary())
    print(f"📄 Summary saved to: {summary_path}")

    print()
    print("=" * 70)
    print("✅ WEB RESEARCH COMPLETE")
    print("=" * 70)
    print()
    print(f"Agent Performance: {agent.get_performance()}")
    print()
    print("Next step: Use this knowledge to improve workflow generation in Cycle-02")


if __name__ == "__main__":
    main()
