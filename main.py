#!/usr/bin/env python3
"""
Revenue Optimization Engine - CLI Entry Point

Usage:
    python main.py scan                          Scan all channels
    python main.py scan --channel affiliate      Scan specific channel
    python main.py plan                          Generate monthly plan
    python main.py report --format all           Generate all reports
    python main.py simulate                      Simulate revenue impact
    python main.py generate-data                 Generate synthetic demo data

Options:
    --output/-o DIR     Output directory (default: ./output)
    --format FMT        console, json, csv, all (default: console)
    --top N             Number of top opportunities to show
    --data-dir DIR      Data directory (default: ./data)
"""

import argparse
import os
import sys

# Ensure project dir is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_models import ChannelType
from optimizer import RevenueOptimizer
from reporter import Reporter

CHANNEL_LOOKUP = {
    "affiliate": ChannelType.AFFILIATE,
    "content": ChannelType.CONTENT,
    "seo": ChannelType.SEO,
    "email": ChannelType.EMAIL,
    "social": ChannelType.SOCIAL,
    "competitor": ChannelType.COMPETITOR,
}


def cmd_scan(args):
    """Scan channels for optimization opportunities."""
    optimizer = RevenueOptimizer(args.data_dir)

    channels = None
    if args.channel:
        ch = CHANNEL_LOOKUP.get(args.channel.lower())
        if ch is None:
            print(f"Unknown channel: {args.channel}")
            print(f"Available: {', '.join(CHANNEL_LOOKUP.keys())}")
            sys.exit(1)
        channels = [ch]

    print("Scanning channels for optimization opportunities...")
    opps = optimizer.scan(channels)
    print(f"\nFound {len(opps)} total opportunities.")

    reporter = Reporter(optimizer)
    reporter.console_report(top_n=args.top or 15)


def cmd_plan(args):
    """Generate monthly optimization plan."""
    optimizer = RevenueOptimizer(args.data_dir)
    optimizer.scan()

    reporter = Reporter(optimizer)
    reporter.monthly_action_plan()


def cmd_report(args):
    """Generate reports in specified format(s)."""
    optimizer = RevenueOptimizer(args.data_dir)
    optimizer.scan()

    reporter = Reporter(optimizer)
    fmt = args.format or "console"
    output_dir = args.output or "./output"

    if fmt in ("console", "all"):
        reporter.console_report(top_n=args.top or 15)
        reporter.executive_summary()

    if fmt in ("json", "all"):
        path = os.path.join(output_dir, "optimization_report.json")
        reporter.export_json(path)

    if fmt in ("csv", "all"):
        path = os.path.join(output_dir, "optimization_report.csv")
        reporter.export_csv(path)

    if fmt == "all":
        print(f"\nAll reports generated in: {os.path.abspath(output_dir)}")


def cmd_simulate(args):
    """Simulate revenue impact of optimizations."""
    optimizer = RevenueOptimizer(args.data_dir)
    optimizer.scan()

    reporter = Reporter(optimizer)
    reporter.simulate_report(top_n=args.top)


def cmd_generate_data(args):
    """Generate synthetic demo data."""
    from data_generator import generate_all
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate_all()


def main():
    parser = argparse.ArgumentParser(
        description="Revenue Optimization Engine - Identify and optimize revenue across channels"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan channels for optimization opportunities")
    p_scan.add_argument("--channel", "-c", help="Specific channel to scan")
    p_scan.add_argument("--top", "-n", type=int, default=15, help="Number of top opportunities")
    p_scan.add_argument("--data-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))

    # plan
    p_plan = subparsers.add_parser("plan", help="Generate monthly optimization plan")
    p_plan.add_argument("--data-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))

    # report
    p_report = subparsers.add_parser("report", help="Generate optimization reports")
    p_report.add_argument("--format", "-f", choices=["console", "json", "csv", "all"], default="console")
    p_report.add_argument("--output", "-o", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
    p_report.add_argument("--top", "-n", type=int, default=15, help="Number of top opportunities")
    p_report.add_argument("--data-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))

    # simulate
    p_sim = subparsers.add_parser("simulate", help="Simulate revenue impact of optimizations")
    p_sim.add_argument("--top", "-n", type=int, help="Simulate top N opportunities")
    p_sim.add_argument("--data-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))

    # generate-data
    subparsers.add_parser("generate-data", help="Generate synthetic demo data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "scan": cmd_scan,
        "plan": cmd_plan,
        "report": cmd_report,
        "simulate": cmd_simulate,
        "generate-data": cmd_generate_data,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
