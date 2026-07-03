"""
Output generation for Revenue Optimization Engine.
Console reports, JSON export, CSV export, executive summary, monthly action plan.
"""

import csv
import json
import os
from datetime import datetime


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
            return

        max_roi = max(o.roi_score for o in opps)

        # Channel summaries
        for _ch, s in sorted(self.opt.summaries.items(), key=lambda x: -x[1].total_potential_gain):
            s.top_opportunity.title[:35] if s.top_opportunity else "N/A"

        # Opportunity table

        for _i, opp in enumerate(opps, 1):
            f"{_priority_icon(opp.priority.value)} {opp.priority.value}"
            _bar(opp.roi_score, max_roi, 15)

        # Revenue impact chart
        sum(o.revenue_gain_monthly for o in opps)
        by_channel = {}
        for o in opps:
            by_channel.setdefault(o.channel.value, 0)
            by_channel[o.channel.value] += o.revenue_gain_monthly
        for _ch, gain in sorted(by_channel.items(), key=lambda x: -x[1]):
            _bar(gain, max(by_channel.values()), 35)

    def executive_summary(self):
        """High-level revenue impact projection."""
        sim = self.opt.simulate()

        for _i, proj in enumerate(sim.monthly_projections):
            _bar(proj, sim.optimized_monthly, 30)

        # Top 5 action items
        top5 = self.opt.get_top(5)
        for _i, _o in enumerate(top5, 1):
            pass

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

    def monthly_action_plan(self):
        """Print week-by-week optimization tasks."""
        plans = self.opt.generate_monthly_plan()

        total_hours = 0
        total_gain = 0

        for plan in plans:

            if not plan.opportunities:
                continue

            for _i, opp in enumerate(plan.opportunities, 1):
                for _step in opp.action_steps[:3]:
                    pass
                if len(opp.action_steps) > 3:
                    pass

            total_hours += plan.estimated_hours
            total_gain += plan.projected_revenue_gain

    def simulate_report(self, top_n=None):
        """Print simulation results."""
        sim = self.opt.simulate(top_n)

        max_proj = max(sim.monthly_projections) if sim.monthly_projections else 1
        for _i, proj in enumerate(sim.monthly_projections):
            _bar(proj, max_proj, 35)
            proj - sim.baseline_monthly

        # Cumulative gain
        sum(p - sim.baseline_monthly for p in sim.monthly_projections)
