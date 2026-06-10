"""
data_models.py - Shared data models for Revenue Optimization Engine.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ChannelType(Enum):
    AFFILIATE = "affiliate"
    CONTENT = "content"
    SEO = "seo"
    EMAIL = "email"
    SOCIAL = "social"
    DIRECT = "direct"
    COMPETITOR = "competitor"


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Effort(Enum):
    TRIVIAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class Impact(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4
    TRANSFORMATIONAL = 5


@dataclass
class OptimizationOpportunity:
    """A single optimization opportunity identified by channel analysis."""
    id: str
    channel: ChannelType
    title: str
    description: str
    current_value: float
    projected_value: float
    revenue_gain_monthly: float
    effort: Effort
    impact: Impact
    roi_score: float = 0.0
    priority: Priority = Priority.MEDIUM
    action_steps: List[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    @property
    def revenue_gain_annual(self):
        return self.revenue_gain_monthly * 12

    def compute_roi_score(self):
        """ROI = (projected_gain * impact) / (effort * cost_factor)"""
        effort_val = self.effort.value
        impact_val = self.impact.value
        gain = self.revenue_gain_monthly
        self.roi_score = round((gain * impact_val) / (effort_val * 100 + 1), 2)
        return self.roi_score

    def determine_priority(self):
        if self.roi_score >= 50:
            self.priority = Priority.CRITICAL
        elif self.roi_score >= 20:
            self.priority = Priority.HIGH
        elif self.roi_score >= 5:
            self.priority = Priority.MEDIUM
        else:
            self.priority = Priority.LOW
        return self.priority


@dataclass
class ActionPlan:
    """A weekly action plan for optimization."""
    week: int
    opportunities: List[OptimizationOpportunity] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    projected_revenue_gain: float = 0.0


@dataclass
class ChannelSummary:
    """Summary stats for a channel."""
    channel: ChannelType
    total_revenue: float
    avg_daily_revenue: float
    trend_pct: float
    opportunity_count: int
    total_potential_gain: float
    top_opportunity: Optional[OptimizationOpportunity] = None


@dataclass
class SimulationResult:
    """Result of simulating optimization impacts."""
    baseline_monthly: float
    optimized_monthly: float
    gain_monthly: float
    gain_annual: float
    gain_pct: float
    opportunities_applied: int
    timeline_months: int
    monthly_projections: List[float] = field(default_factory=list)
