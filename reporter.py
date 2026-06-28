"""
Output generation for Revenue Optimization Engine.
Console reports, JSON export, CSV export, executive summary, monthly action plan.
"""

import csv
import json
import os
from datetime import datetime
from data_models import Priority


def _bar(value, max_val, width=30):
    """ASCII bar chart element."""
    if max_val <= 0:
        return ""
    filled = int((value / max_val) * width)
    return "█" * filled + "░" * (width - filled)


def _priority_icon(p):
    return {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(p, "⚪")


class Reporter:
    """Generate reports from optimization results."""

    def __init__(self, optimizer):
        self.opt = optimizer

    def console_report(self, top_n=15):
        """Print prioritized opportunity table with ASCII charts."""
        opps = self.opt.get_top(top_n)
        if not opps:
            print("No opportunities found.")
            return

        max_roi = max(o.roi_score for o in opps)
        max_gain = max(o.revenue_gain_monthly for o in opps)

        print()
        print("=" * 100)
        print("  REVENUE OPTIMIZATION ENGINE - OPPORTUNITY REPORT")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 100)
        print()

        # Channel summaries
        print("  CHANNEL SUMMARIES")
        print("  " + "-" * 96)
        print(f"  {'Channel':<14} {'Daily Rev':>10} {'Opportunities':>14} {'Potential Gain':>16} {'Top Opportunity'}")
        print("  " + "-" * 96)
        for ch, s in sorted(self.opt.summaries.items(), key=lambda x: -x[1].total_potential_gain):
            top_title = s.top_opportunity.title[:35] if s.top_opportunity else "N/A"
            print(f"  {ch.value:<14} ${s.avg_daily_revenue:>9,.0f} {s.opportunity_count:>14} ${s.total_potential_gain:>14,.0f}  {top_title}")
        print()

        # Opportunity table
        print("  TOP OPPORTUNITIES (Ranked by ROI Score)")
        print("  " + "-" * 96)
        print(f"  {'#':>3} {'Priority':<10} {'Channel':<12} {'Opportunity':<32} {'Gain/mo':>10} {'ROI Score':>10}")
        print("  " + "-" * 96)

        for i, opp in enumerate(opps, 1):
            pri = f"{_priority_icon(opp.priority.value)} {opp.priority.value}"
            bar = _bar(opp.roi_score, max_roi, 15)
            print(f"  {i:>3} {pri:<10} {opp.channel.value:<12} {opp.title[:30]:<32} ${opp.revenue_gain_monthly:>9,.0f} {bar} {opp.roi_score:>6.1f}")

        print("  " + "-" * 96)

        # Revenue impact chart
        total_gain = sum(o.revenue_gain_monthly for o in opps)
        print()
        print("  REVENUE IMPACT BY CHANNEL")
        print("  " + "-" * 60)
        by_channel = {}
        for o in opps:
            by_channel.setdefault(o.channel.value, 0)
            by_channel[o.channel.value] += o.revenue_gain_monthly
        for ch, gain in sorted(by_channel.items(), key=lambda x: -x[1]):
            bar = _bar(gain, max(by_channel.values()), 35)
            print(f"  {ch:<14} {bar} ${gain:>8,.0f}/mo")

        print()
        print(f"  TOTAL POTENTIAL: ${total_gain:,.0f}/month  |  ${total_gain*12:,.0f}/year")
        print("=" * 100)

    def executive_summary(self):
        """High-level revenue impact projection."""
        sim = self.opt.simulate()
        opps = self.opt.opportunities

        print()
        print("=" * 80)
        print("  EXECUTIVE SUMMARY - REVENUE OPTIMIZATION")
        print("=" * 80)
        print()
        print(f"  Current Monthly Revenue (est):    ${sim.baseline_monthly:>12,.2f}")
        print(f"  Optimized Monthly Revenue (est):  ${sim.optimized_monthly:>12,.2f}")
        print(f"  Monthly Revenue Gain:             ${sim.gain_monthly:>12,.2f}")
        print(f"  Annual Revenue Gain:              ${sim.gain_annual:>12,.2f}")
        print(f"  Revenue Increase:                 {sim.gain_pct:>11.1f}%")
        print()
        print(f"  Total Opportunities Found:        {len(opps):>12}")
        print(f"  Critical Priority:                {len(self.opt.get_by_priority(Priority.CRITICAL)):>12}")
        print(f"  High Priority:                    {len(self.opt.get_by_priority(Priority.HIGH)):>12}")
        print()
        print("  6-MONTH PROJECTION (with ramp-up):")
        print("  " + "-" * 50)
        for i, proj in enumerate(sim.monthly_projections):
            bar = _bar(proj, sim.optimized_monthly, 30)
            print(f"  Month {i+1}:  {bar} ${proj:>10,.0f}")
        print("  " + "-" * 50)
        print()

        # Top 5 action items
        top5 = self.opt.get_top(5)
        print("  TOP 5 QUICK WINS:")
        for i, o in enumerate(top5, 1):
            print(f"  {i}. [{o.channel.value.upper()}] {o.title}")
            print(f"     -> {o.description[:70]}...")
            print(f"     Est. gain: ${o.revenue_gain_monthly:,.0f}/mo  |  ROI Score: {o.roi_score:.1f}")
        print()
        print("=" * 80)

    def export_json(self, output_path):
        """Export full opportunity data with action plans."""
        plans = self.opt.generate_monthly_plan()
        data = {
            "generated": datetime.now().isoformat(),
            "summary": {
                "total_opportunities": len(self.opt.opportunities),
                "total_monthly_gain": sum(o.revenue_gain_monthly for o in self.opt.opportunities),
                "total_annual_gain": sum(o.revenue_gain_annual for o in self.opt.opportunities),
                "channels": {}
            },
            "opportunities": [],
            "monthly_plan": []
        }

        for ch, s in self.opt.summaries.items():
            data["summary"]["channels"][ch.value] = {
                "avg_daily_revenue": s.avg_daily_revenue,
                "opportunity_count": s.opportunity_count,
                "total_potential_gain": s.total_potential_gain
            }

        for opp in self.opt.opportunities:
            data["opportunities"].append({
                "id": opp.id,
                "channel": opp.channel.value,
                "title": opp.title,
                "description": opp.description,
                "current_value": opp.current_value,
                "projected_value": opp.projected_value,
                "revenue_gain_monthly": opp.revenue_gain_monthly,
                "revenue_gain_annual": opp.revenue_gain_annual,
                "effort": opp.effort.name,
                "impact": opp.impact.name,
                "roi_score": opp.roi_score,
                "priority": opp.priority.value,
                "action_steps": opp.action_steps,
                "metrics": opp.metrics
            })

        for plan in plans:
            data["monthly_plan"].append({
                "week": plan.week,
                "task_count": len(plan.tasks),
                "estimated_hours": plan.estimated_hours,
                "projected_revenue_gain": plan.projected_revenue_gain,
                "opportunities": [o.title for o in plan.opportunities],
                "tasks": plan.tasks
            })

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"JSON report exported: {output_path}")

    def export_csv(self, output_path):
        """Export opportunities as CSV spreadsheet."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fields = [
            "id", "channel", "title", "description", "current_value",
            "projected_value", "revenue_gain_monthly", "revenue_gain_annual",
            "effort", "impact", "roi_score", "priority"
        ]
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for opp in self.opt.opportunities:
                writer.writerow({
                    "id": opp.id,
                    "channel": opp.channel.value,
                    "title": opp.title,
                    "description": opp.description,
                    "current_value": opp.current_value,
                    "projected_value": opp.projected_value,
                    "revenue_gain_monthly": opp.revenue_gain_monthly,
                    "revenue_gain_annual": opp.revenue_gain_annual,
                    "effort": opp.effort.name,
                    "impact": opp.impact.name,
                    "roi_score": opp.roi_score,
                    "priority": opp.priority.value,
                })
        print(f"CSV report exported: {output_path}")

    def monthly_action_plan(self):
        """Print week-by-week optimization tasks."""
        plans = self.opt.generate_monthly_plan()

        print()
        print("=" * 80)
        print("  MONTHLY OPTIMIZATION ACTION PLAN")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 80)

        total_hours = 0
        total_gain = 0

        for plan in plans:
            print()
            print(f"  WEEK {plan.week}")
            print(f"  Est. Hours: {plan.estimated_hours:.0f}  |  Projected Gain: ${plan.projected_revenue_gain:,.0f}/mo")
            print("  " + "-" * 70)

            if not plan.opportunities:
                print("  (No opportunities assigned - capacity filled or all completed)")
                continue

            for i, opp in enumerate(plan.opportunities, 1):
                print(f"  {i}. [{opp.channel.value.upper()}] {opp.title}")
                print(f"     Priority: {opp.priority.value}  |  ROI: {opp.roi_score:.1f}  |  Gain: ${opp.revenue_gain_monthly:,.0f}/mo")
                for step in opp.action_steps[:3]:
                    print(f"     - {step}")
                if len(opp.action_steps) > 3:
                    print(f"     ... and {len(opp.action_steps) - 3} more steps")
                print()

            total_hours += plan.estimated_hours
            total_gain += plan.projected_revenue_gain

        print("  " + "=" * 70)
        print(f"  TOTAL: {total_hours:.0f} hours  |  ${total_gain:,.0f}/mo potential gain")
        print("=" * 80)

    def simulate_report(self, top_n=None):
        """Print simulation results."""
        sim = self.opt.simulate(top_n)

        print()
        print("=" * 80)
        print("  REVENUE IMPACT SIMULATION")
        print("=" * 80)
        print()
        print(f"  Opportunities Applied:     {sim.opportunities_applied}")
        print(f"  Baseline Monthly Revenue:  ${sim.baseline_monthly:>12,.2f}")
        print(f"  Projected Monthly Revenue: ${sim.optimized_monthly:>12,.2f}")
        print(f"  Monthly Gain:              ${sim.gain_monthly:>12,.2f}")
        print(f"  Annual Gain:               ${sim.gain_annual:>12,.2f}")
        print(f"  Revenue Increase:          {sim.gain_pct:>11.1f}%")
        print()
        print("  MONTHLY RAMP-UP PROJECTION:")
        print("  " + "-" * 60)

        max_proj = max(sim.monthly_projections) if sim.monthly_projections else 1
        for i, proj in enumerate(sim.monthly_projections):
            bar = _bar(proj, max_proj, 35)
            delta = proj - sim.baseline_monthly
            print(f"  Month {i+1}:  {bar}  ${proj:>10,.0f}  (+${delta:>8,.0f})")

        print("  " + "-" * 60)
        print(f"  {'':14} {'':35}  Baseline: ${sim.baseline_monthly:>10,.0f}")
        print()

        # Cumulative gain
        cumulative = sum(p - sim.baseline_monthly for p in sim.monthly_projections)
        print(f"  Cumulative 6-Month Gain:   ${cumulative:>12,.2f}")
        print("  Break-even Assumption:     Immediate (optimization effort only)")
        print("=" * 80)
