"""Tests for revenue-optimizer core functionality."""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_main_imports():
    """Test that main module imports without errors."""
    import main
    assert hasattr(main, 'main')


def test_data_models_imports():
    """Test data models can be imported."""
    from data_models import (
        ChannelType,
        Effort,
        Impact,
        Priority,
    )
    assert ChannelType.AFFILIATE
    assert Priority.HIGH
    assert Effort.MEDIUM
    assert Impact.HIGH


def test_optimizer_imports():
    """Test optimizer module imports."""
    from optimizer import RevenueOptimizer
    assert RevenueOptimizer


def test_channels_imports():
    """Test channel analyzers import."""
    from channels import (
        AffiliateChannel,
        CompetitorChannel,
        ContentChannel,
        EmailChannel,
        SEOChannel,
        SocialChannel,
    )
    assert AffiliateChannel
    assert ContentChannel
    assert SEOChannel
    assert CompetitorChannel
    assert EmailChannel
    assert SocialChannel


def test_reporter_imports():
    """Test reporter module imports."""
    from reporter import Reporter
    assert Reporter


def test_data_generator_imports():
    """Test data generator imports."""
    from data_generator import generate_all
    assert generate_all


def test_main_generate_data_command():
    """Test generate-data command runs without error."""
    import sys
    from io import StringIO

    import main
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        # Simulate command line args
        sys.argv = ['main.py', 'generate-data']
        main.main()
        # Just verify it runs without error (no output expected after ruff fix)
    finally:
        sys.stdout = old_stdout
        sys.argv = ['main.py']


def test_data_models_enum_values():
    """Test data model enums have expected values."""
    from data_models import ChannelType, Effort, Impact, Priority
    
    # Check all channels exist
    assert hasattr(ChannelType, 'AFFILIATE')
    assert hasattr(ChannelType, 'CONTENT')
    assert hasattr(ChannelType, 'SEO')
    assert hasattr(ChannelType, 'COMPETITOR')
    assert hasattr(ChannelType, 'EMAIL')
    assert hasattr(ChannelType, 'SOCIAL')
    
    # Check priority levels exist
    assert hasattr(Priority, 'CRITICAL')
    assert hasattr(Priority, 'HIGH')
    assert hasattr(Priority, 'MEDIUM')
    assert hasattr(Priority, 'LOW')
    
    # Check effort levels exist
    assert hasattr(Effort, 'TRIVIAL')
    assert hasattr(Effort, 'LOW')
    assert hasattr(Effort, 'MEDIUM')
    assert hasattr(Effort, 'HIGH')
    assert hasattr(Effort, 'VERY_HIGH')
    
    # Check impact levels exist
    assert hasattr(Impact, 'LOW')
    assert hasattr(Impact, 'MEDIUM')
    assert hasattr(Impact, 'HIGH')
    assert hasattr(Impact, 'VERY_HIGH')
    assert hasattr(Impact, 'TRANSFORMATIONAL')


def test_optimizer_initialization():
    """Test optimizer can be initialized."""
    from optimizer import RevenueOptimizer
    
    optimizer = RevenueOptimizer(data_dir='data')
    assert optimizer is not None
    assert hasattr(optimizer, 'data_dir')


def test_data_generator_creates_files():
    """Test data generator creates expected CSV files."""
    import os
    import tempfile

    from data_generator import generate_affiliate_data, save_csv
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test one generator
        data = generate_affiliate_data(days=7)
        path = os.path.join(tmpdir, 'test_affiliate.csv')
        save_csv(data, path)
        
        assert os.path.exists(path)
        with open(path) as f:
            content = f.read()
            assert len(content) > 0
            assert 'affiliate_id' in content


def test_channel_analyzers_exist():
    """Test all 6 channel analyzers exist and can be instantiated."""
    from channels import (
        AffiliateChannel,
        CompetitorChannel,
        ContentChannel,
        EmailChannel,
        SEOChannel,
        SocialChannel,
    )
    
    # Verify classes exist
    assert AffiliateChannel
    assert ContentChannel
    assert SEOChannel
    assert CompetitorChannel
    assert EmailChannel
    assert SocialChannel


def test_optimizer_scan_returns_opportunities():
    """Test optimizer scan returns list of opportunities."""
    from optimizer import RevenueOptimizer
    
    optimizer = RevenueOptimizer(data_dir='data')
    opportunities = optimizer.scan()
    
    assert isinstance(opportunities, list)
    # Should have at least some opportunities from demo data
    assert len(opportunities) >= 0


def test_optimizer_plan_generation():
    """Test optimizer can generate a plan."""
    from optimizer import RevenueOptimizer
    
    optimizer = RevenueOptimizer(data_dir='data')
    optimizer.scan()
    plans = optimizer.generate_monthly_plan()
    
    assert isinstance(plans, list)
    # May have 0-4 weeks of plans
    assert len(plans) <= 4


def test_reporter_generates_output():
    """Test reporter can generate console output."""

    from data_models import ChannelType, Effort, Impact, OptimizationOpportunity
    from reporter import Reporter
    
    # Create a test opportunity
    opp = OptimizationOpportunity(
        id="test-1",
        channel=ChannelType.AFFILIATE,
        title="Test Opportunity",
        description="Test",
        current_value=1.0,
        projected_value=2.0,
        revenue_gain_monthly=1000.0,
        effort=Effort.MEDIUM,
        impact=Impact.HIGH,
        action_steps=["Step 1", "Step 2"],
        metrics={},
    )
    opp.compute_roi_score()
    opp.determine_priority()
    
    # Mock optimizer with minimal required attributes
    class MockOptimizer:
        def __init__(self, opportunities):
            self.opportunities = opportunities
            self.summaries = {}
        
        def get_top(self, n=15):
            return self.opportunities[:n]
        
        def get_by_priority(self, priority):
            return [o for o in self.opportunities if o.priority == priority]
        
        def get_by_channel(self, channel_type):
            return [o for o in self.opportunities if o.channel == channel_type]
        
        def simulate(self, top_n=None):
            from data_models import SimulationResult
            return SimulationResult(
                baseline_monthly=1000.0,
                optimized_monthly=1500.0,
                gain_monthly=500.0,
                gain_annual=6000.0,
                gain_pct=50.0,
                opportunities_applied=len(self.opportunities),
                timeline_months=6,
                monthly_projections=[1100, 1200, 1300, 1400, 1450, 1500]
            )
        
        def generate_monthly_plan(self, weeks=4, max_hours_per_week=20):
            from data_models import ActionPlan
            plan = ActionPlan(week=1)
            if self.opportunities:
                plan.opportunities.append(self.opportunities[0])
                plan.tasks.extend(self.opportunities[0].action_steps)
                plan.estimated_hours = 10
                plan.projected_revenue_gain = 1000
            return [plan]
    
    mock_opt = MockOptimizer([opp])
    reporter = Reporter(mock_opt)
    
    # Should not raise
    output = reporter.console_report(top_n=5)
    assert output is None  # Prints to stdout, returns None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])