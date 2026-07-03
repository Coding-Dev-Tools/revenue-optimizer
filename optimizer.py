"""
Core optimization engine for Revenue Optimization Engine.
Scans channels, scores opportunities, generates action plans.
"""

import os

from channels import (
    AffiliateChannel,
    CompetitorChannel,
    ContentChannel,
    EmailChannel,
    SEOChannel,
    SocialChannel,
)
from data_models import ActionPlan, ChannelSummary, ChannelType, Effort, SimulationResult

CHANNEL_MAP = {
    ChannelType.AFFILIATE: ("affiliate_performance.csv", AffiliateChannel),
    ChannelType.CONTENT: ("content_performance.csv", ContentChannel),
    ChannelType.SEO: ("seo_performance.csv", SEOChannel),
    ChannelType.COMPETITOR: ("competitor_metrics.csv", CompetitorChannel),
    ChannelType.EMAIL: ("email_performance.csv", EmailChannel),
    ChannelType.SOCIAL: ("social_performance.csv", SocialChannel),
}


class RevenueOptimizer:
    """Core optimization engine."""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.opportunities = []
        self.summaries = {}

    def scan(self, channels=None):
        """Scan specified channels (or all) for optimization opportunities."""
        if channels is None:
            channels = list(CHANNEL_MAP.keys())

        self.opportunities = []
        self.summaries = {}

        for ch_type in channels:
            if ch_type not in CHANNEL_MAP:
                print(f"Warning: Unknown channel type {ch_type}")
                continue

            filename, cls = CHANNEL_MAP[ch_type]
            path = os.path.join(self.data_dir, filename)
            if not os.path.exists(path):
                print(f"Warning: Data file not found: {path}")
                continue

            try:
                channel = cls(path)
                opps = channel.analyze()
                self.opportunities.extend(opps)
                self.summaries[ch_type] = self._build_summary(ch_type, channel, opps)
            except Exception as e:
                print(f"Warning: Error analyzing {ch_type.value}: {e}")

        # Sort by ROI score
        self.opportunities.sort(key=lambda o: o.roi_score, reverse=True)
        return self.opportunities

    def _build_summary(self, ch_type, channel, opps):
        """Build channel summary from analyzer data."""
        total_rev = 0
        days = set()

        if hasattr(channel, 'affiliates'):
            for a in channel.affiliates.values():
                total_rev += a['revenue']
                days.update(a['days'])
        elif hasattr(channel, 'pages'):
            for p in channel.pages.values():
                total_rev += p['revenue']
                days.update(p['days'])
        elif hasattr(channel, 'keywords'):
            for k in channel.keywords.values():
                total_rev += k['clicks'] * k['cpc'] * 0.05
                days.add('seo')
        elif hasattr(channel, 'lists'):
            for lst in channel.lists.values():
                total_rev += lst['revenue']
                days.update(lst['days'])
        elif hasattr(channel, 'platforms'):
            for p in channel.platforms.values():
                total_rev += p['revenue']
                days.update(p['days'])
        elif hasattr(channel, 'competitors'):
            for c in channel.competitors.values():
                days.update(c['days'])

        n_days = max(len(days), 1)
        total_gain = sum(o.revenue_gain_monthly for o in opps)
        top = opps[0] if opps else None

        return ChannelSummary(
            channel=ch_type,
            total_revenue=round(total_rev, 2),
            avg_daily_revenue=round(total_rev / n_days, 2),
            trend_pct=0.0,
            opportunity_count=len(opps),
            total_potential_gain=round(total_gain, 2),
            top_opportunity=top
        )

    def get_top(self, n=10):
        """Get top N opportunities by ROI score."""
        return self.opportunities[:n]

    def get_by_priority(self, priority):
        """Filter opportunities by priority level."""
        return [o for o in self.opportunities if o.priority == priority]

    def get_by_channel(self, channel_type):
        """Filter opportunities by channel."""
        return [o for o in self.opportunities if o.channel == channel_type]

    def generate_monthly_plan(self, weeks=4, max_hours_per_week=20):
        """Generate a week-by-week optimization plan."""
        remaining = list(self.opportunities)  # already sorted by ROI
        plans = []

        for week in range(1, weeks + 1):
            plan = ActionPlan(week=week)
            week_hours = 0.0

            while remaining:
                opp = remaining[0]
                effort_hours = {
                    Effort.TRIVIAL: 2, Effort.LOW: 5, Effort.MEDIUM: 10,
                    Effort.HIGH: 20, Effort.VERY_HIGH: 35
                }.get(opp.effort, 10)

                if week_hours + effort_hours > max_hours_per_week:
                    if week_hours == 0:
                        # Even the first item exceeds budget, include it anyway
                        remaining.pop(0)
                        plan.opportunities.append(opp)
                        plan.tasks.extend(opp.action_steps)
                        plan.estimated_hours += effort_hours
                        plan.projected_revenue_gain += opp.revenue_gain_monthly
                        break
                    break

                remaining.pop(0)
                plan.opportunities.append(opp)
                plan.tasks.extend(opp.action_steps)
                plan.estimated_hours += effort_hours
                plan.projected_revenue_gain += opp.revenue_gain_monthly
                week_hours += effort_hours

            plan.projected_revenue_gain = round(plan.projected_revenue_gain, 2)
            plans.append(plan)

        return plans

    def simulate(self, top_n=None):
        """Simulate revenue impact of implementing top N optimizations."""
        if top_n is None:
            top_n = len(self.opportunities)

        selected = self.opportunities[:top_n]

        # Estimate baseline from summaries
        baseline_monthly = sum(s.avg_daily_revenue * 30 for s in self.summaries.values())
        total_gain = sum(o.revenue_gain_monthly for o in selected)

        # Simulate ramp-up over 6 months
        monthly_projections = []
        for month in range(1, 7):
            # Assume gradual adoption: 30%, 50%, 70%, 85%, 95%, 100%
            ramp = [0.3, 0.5, 0.7, 0.85, 0.95, 1.0][min(month - 1, 5)]
            monthly_projections.append(round(baseline_monthly + total_gain * ramp, 2))

        optimized_monthly = baseline_monthly + total_gain

        return SimulationResult(
            baseline_monthly=round(baseline_monthly, 2),
            optimized_monthly=round(optimized_monthly, 2),
            gain_monthly=round(total_gain, 2),
            gain_annual=round(total_gain * 12, 2),
            gain_pct=round((total_gain / max(baseline_monthly, 1)) * 100, 1),
            opportunities_applied=len(selected),
            timeline_months=6,
            monthly_projections=monthly_projections
        )
