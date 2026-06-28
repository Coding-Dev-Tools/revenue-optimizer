"""
Channel-specific analyzers for Revenue Optimization Engine.
Each channel returns a list of OptimizationOpportunity objects.
"""

import csv
from collections import defaultdict
from data_models import (
    ChannelType, Effort, Impact, OptimizationOpportunity
)


def _load_csv(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def _safe_float(v, default=0.0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


class AffiliateChannel:
    """Analyze affiliate performance: EPC, conversion rates, top/bottom performers."""

    def __init__(self, data_path):
        self.data = _load_csv(data_path)
        self._aggregate()

    def _aggregate(self):
        self.affiliates = defaultdict(lambda: {
            'clicks': 0, 'conversions': 0, 'revenue': 0,
            'commission': 0, 'days': set(), 'epc_sum': 0.0, 'conv_sum': 0.0
        })
        for row in self.data:
            a = self.affiliates[row['affiliate_id']]
            a['name'] = row['affiliate_name']
            a['niche'] = row['niche']
            a['clicks'] += int(row['clicks'])
            a['conversions'] += int(row['conversions'])
            a['revenue'] += _safe_float(row['revenue'])
            a['commission'] += _safe_float(row['commission'])
            a['epc_sum'] += _safe_float(row['epc'])
            a['conv_sum'] += _safe_float(row['conversion_rate'])
            a['days'].add(row['date'])
        for a in self.affiliates.values():
            n = max(len(a['days']), 1)
            a['avg_epc'] = a['epc_sum'] / n
            a['avg_conv'] = a['conv_sum'] / n
            a['ctr'] = a['conversions'] / max(a['clicks'], 1)

    def analyze(self):
        opps = []
        avg_rev = sum(a['revenue'] for a in self.affiliates.values()) / max(len(self.affiliates), 1)

        for aid, a in self.affiliates.items():
            # Low EPC opportunity
            if a['avg_epc'] < 0.3 and a['clicks'] > 5000:
                gain = (0.3 - a['avg_epc']) * a['clicks'] * 30 / max(len(a['days']), 1)
                opps.append(OptimizationOpportunity(
                    id=f"aff_epc_{aid}", channel=ChannelType.AFFILIATE,
                    title=f"Improve EPC for {a['name']}",
                    description=f"{a['name']} has EPC ${a['avg_epc']:.2f} vs portfolio avg. "
                                f"Recommend better creatives, landing pages, or product selection.",
                    current_value=a['avg_epc'], projected_value=0.35,
                    revenue_gain_monthly=round(gain, 2),
                    effort=Effort.MEDIUM, impact=Impact.HIGH,
                    action_steps=[
                        "Audit current landing pages for conversion leaks",
                        "A/B test new creatives and CTAs",
                        "Review product selection and pricing",
                        "Negotiate higher commission rates if volume justified",
                        "Implement retargeting for dropped visitors"
                    ],
                    metrics={'clicks': a['clicks'], 'current_epc': round(a['avg_epc'], 4)}
                ))

            # Low conversion rate opportunity
            if a['avg_conv'] < 0.02 and a['clicks'] > 3000:
                gain = a['clicks'] * (0.03 - a['avg_conv']) * a['avg_epc'] * 20 * 30 / max(len(a['days']), 1)
                opps.append(OptimizationOpportunity(
                    id=f"aff_conv_{aid}", channel=ChannelType.AFFILIATE,
                    title=f"Boost conversion rate for {a['name']}",
                    description=f"{a['name']} converts at {a['avg_conv']*100:.1f}%. "
                                f"Optimize funnel to reach 3% target.",
                    current_value=a['avg_conv'], projected_value=0.03,
                    revenue_gain_monthly=round(max(gain, 50), 2),
                    effort=Effort.HIGH, impact=Impact.HIGH,
                    action_steps=[
                        "Analyze drop-off points in affiliate funnel",
                        "Improve pre-sell content quality",
                        "Test different offer presentations",
                        "Add social proof and urgency elements",
                        "Optimize mobile experience"
                    ],
                    metrics={'conversion_rate': round(a['avg_conv'], 4)}
                ))

            # Under-monetized high-traffic affiliate
            if a['revenue'] < avg_rev * 0.5 and a['clicks'] > avg_rev:
                gain = avg_rev * 0.5 - a['revenue']
                opps.append(OptimizationOpportunity(
                    id=f"aff_under_{aid}", channel=ChannelType.AFFILIATE,
                    title=f"Monetize high-traffic affiliate {a['name']}",
                    description=f"{a['name']} drives significant traffic but underperforms on revenue.",
                    current_value=a['revenue'], projected_value=avg_rev,
                    revenue_gain_monthly=round(max(gain / 3, 100), 2),
                    effort=Effort.MEDIUM, impact=Impact.VERY_HIGH,
                    action_steps=[
                        "Analyze traffic quality and intent",
                        "Test premium product placements",
                        "Create dedicated landing pages",
                        "Implement dynamic offers based on traffic segment"
                    ],
                    metrics={'revenue': round(a['revenue'], 2), 'avg_revenue': round(avg_rev, 2)}
                ))

        for opp in opps:
            opp.compute_roi_score()
            opp.determine_priority()
        return opps


class ContentChannel:
    """Analyze content for traffic, engagement, monetization potential."""

    def __init__(self, data_path):
        self.data = _load_csv(data_path)
        self._aggregate()

    def _aggregate(self):
        self.pages = defaultdict(lambda: {
            'sessions': 0, 'bounce_sum': 0.0, 'time_sum': 0.0,
            'revenue': 0.0, 'days': set(), 'monetized_count': 0, 'content_type': ''
        })
        for row in self.data:
            p = self.pages[row['page_id']]
            p['title'] = row['page_title']
            p['content_type'] = row['content_type']
            p['sessions'] += int(row['sessions'])
            p['bounce_sum'] += _safe_float(row['bounce_rate'])
            p['time_sum'] += _safe_float(row['avg_time_min'])
            p['revenue'] += _safe_float(row['revenue'])
            if row.get('monetized', '').lower() == 'true':
                p['monetized_count'] += 1
            p['days'].add(row['date'])
        for p in self.pages.values():
            n = max(len(p['days']), 1)
            p['avg_bounce'] = p['bounce_sum'] / n
            p['avg_time'] = p['time_sum'] / n
            p['monetized_pct'] = p['monetized_count'] / max(len(p['days']), 1)

    def analyze(self):
        opps = []
        avg_sessions = sum(p['sessions'] for p in self.pages.values()) / max(len(self.pages), 1)
        avg_rev = sum(p['revenue'] for p in self.pages.values()) / max(len(self.pages), 1)

        for pid, p in self.pages.items():
            # High-traffic, unmonetized content
            if p['sessions'] > avg_sessions and p['revenue'] < avg_rev * 0.3:
                gain = avg_rev * 0.6
                opps.append(OptimizationOpportunity(
                    id=f"cnt_mon_{pid}", channel=ChannelType.CONTENT,
                    title=f"Monetize high-traffic page: {p['title']}",
                    description=f"Page gets {p['sessions']:,} sessions but generates only ${p['revenue']:.0f}. "
                                f"Add affiliate links, ads, or product recommendations.",
                    current_value=p['revenue'], projected_value=gain,
                    revenue_gain_monthly=round(gain / 3, 2),
                    effort=Effort.LOW, impact=Impact.HIGH,
                    action_steps=[
                        "Add relevant affiliate product links",
                        "Insert contextual ad placements",
                        "Create comparison tables with affiliate links",
                        "Add email capture for lead nurturing",
                        "Test in-content vs sidebar placements"
                    ],
                    metrics={'sessions': p['sessions'], 'current_rps': round(p['revenue']/max(p['sessions'],1), 4)}
                ))

            # High bounce rate page with good traffic
            if p['avg_bounce'] > 0.6 and p['sessions'] > avg_sessions * 0.5:
                gain = p['revenue'] * 0.3
                opps.append(OptimizationOpportunity(
                    id=f"cnt_bounce_{pid}", channel=ChannelType.CONTENT,
                    title=f"Reduce bounce rate: {p['title']}",
                    description=f"Bounce rate {p['avg_bounce']*100:.0f}% is high. "
                                f"Improve engagement to capture more revenue.",
                    current_value=p['avg_bounce'], projected_value=0.4,
                    revenue_gain_monthly=round(max(gain, 20), 2),
                    effort=Effort.MEDIUM, impact=Impact.MEDIUM,
                    action_steps=[
                        "Improve above-the-fold content and hook",
                        "Add internal links and related content widgets",
                        "Improve page load speed",
                        "Add engaging media (video, infographics)",
                        "Test different content layouts"
                    ],
                    metrics={'bounce_rate': round(p['avg_bounce'], 3)}
                ))

            # Stale content that needs refresh
            if p['content_type'] == 'review' and p['revenue'] > 0 and p['sessions'] < avg_sessions * 0.3:
                gain = avg_rev * 0.4 - p['revenue']
                opps.append(OptimizationOpportunity(
                    id=f"cnt_refresh_{pid}", channel=ChannelType.CONTENT,
                    title=f"Refresh stale content: {p['title']}",
                    description="Review content has declining traffic. Update with current info and new products.",
                    current_value=p['revenue'], projected_value=avg_rev * 0.4,
                    revenue_gain_monthly=round(max(gain, 30), 2),
                    effort=Effort.LOW, impact=Impact.MEDIUM,
                    action_steps=[
                        "Update product recommendations with current picks",
                        "Refresh pricing and availability info",
                        "Add new comparison criteria",
                        "Update publication date and meta info",
                        "Promote via social and email channels"
                    ],
                    metrics={'sessions': p['sessions']}
                ))

        for opp in opps:
            opp.compute_roi_score()
            opp.determine_priority()
        return opps


class SEOChannel:
    """Analyze keyword gaps, content gaps, ranking opportunities."""

    def __init__(self, data_path):
        self.data = _load_csv(data_path)
        self._aggregate()

    def _aggregate(self):
        self.keywords = defaultdict(lambda: {
            'positions': [], 'impressions': 0, 'clicks': 0,
            'volume': 0, 'cpc': 0.0
        })
        for row in self.data:
            k = self.keywords[row['keyword']]
            k['positions'].append(int(row['position']))
            k['impressions'] += int(row['impressions'])
            k['clicks'] += int(row['clicks'])
            k['volume'] = int(row['search_volume'])
            k['cpc'] = _safe_float(row['cpc'])
        for k in self.keywords.values():
            k['avg_position'] = sum(k['positions']) / max(len(k['positions']), 1)
            k['ctr'] = k['clicks'] / max(k['impressions'], 1)

    def analyze(self):
        opps = []
        for kw, k in self.keywords.items():
            # Keywords on page 2 (positions 11-20) - easy to push to page 1
            if 11 <= k['avg_position'] <= 20:
                est_traffic_gain = k['volume'] * 0.15 * 30 / 30  # ~15% CTR on page 1
                gain = est_traffic_gain * k['cpc'] * 0.05
                opps.append(OptimizationOpportunity(
                    id=f"seo_page2_{kw.replace(' ', '_')}", channel=ChannelType.SEO,
                    title=f"Push '{kw}' from page 2 to page 1",
                    description=f"Currently averaging position {k['avg_position']:.0f}. "
                                f"Volume: {k['volume']:,}/mo. High opportunity to reach page 1.",
                    current_value=k['avg_position'], projected_value=8.0,
                    revenue_gain_monthly=round(max(gain, 50), 2),
                    effort=Effort.MEDIUM, impact=Impact.HIGH,
                    action_steps=[
                        "Audit and improve content depth and quality",
                        "Build 5-10 relevant backlinks",
                        "Optimize title tag and meta description",
                        "Add structured data markup",
                        "Improve internal linking to this page",
                        "Ensure mobile optimization and Core Web Vitals"
                    ],
                    metrics={'position': round(k['avg_position'], 1), 'volume': k['volume'], 'cpc': k['cpc']}
                ))

            # High impressions, low CTR - title/description optimization
            if k['impressions'] > 5000 and k['ctr'] < 0.02:
                gain = k['impressions'] * (0.04 - k['ctr']) * k['cpc'] * 0.05 * 30 / 30
                opps.append(OptimizationOpportunity(
                    id=f"seo_ctr_{kw.replace(' ', '_')}", channel=ChannelType.SEO,
                    title=f"Improve CTR for '{kw}'",
                    description=f"High impressions ({k['impressions']:,}) but low CTR ({k['ctr']*100:.1f}%). "
                                f"Optimize titles and meta descriptions.",
                    current_value=k['ctr'], projected_value=0.04,
                    revenue_gain_monthly=round(max(gain, 30), 2),
                    effort=Effort.LOW, impact=Impact.MEDIUM,
                    action_steps=[
                        "Rewrite title tag with power words and numbers",
                        "Write compelling meta description with CTA",
                        "Add schema markup for rich snippets",
                        "Test different title variations over 4 weeks"
                    ],
                    metrics={'impressions': k['impressions'], 'ctr': round(k['ctr'], 4)}
                ))

            # High CPC keywords worth investing in
            if k['cpc'] > 3.0 and k['avg_position'] > 5:
                est_traffic = k['volume'] * 0.1 * 30 / 30
                gain = est_traffic * k['cpc'] * 0.03
                opps.append(OptimizationOpportunity(
                    id=f"seo_highcpc_{kw.replace(' ', '_')}", channel=ChannelType.SEO,
                    title=f"Target high-CPC keyword '{kw}'",
                    description=f"CPC ${k['cpc']:.2f}, position {k['avg_position']:.0f}. "
                                f"Ranking improvements yield high revenue per visitor.",
                    current_value=k['avg_position'], projected_value=3.0,
                    revenue_gain_monthly=round(max(gain, 100), 2),
                    effort=Effort.HIGH, impact=Impact.VERY_HIGH,
                    action_steps=[
                        "Create comprehensive pillar content",
                        "Build topic cluster with supporting articles",
                        "Secure 15+ quality backlinks",
                        "Optimize for featured snippet",
                        "Monitor and iterate monthly"
                    ],
                    metrics={'cpc': k['cpc'], 'position': round(k['avg_position'], 1)}
                ))

        for opp in opps:
            opp.compute_roi_score()
            opp.determine_priority()
        return opps


class CompetitorChannel:
    """Analyze pricing gaps, feature gaps, market positioning."""

    def __init__(self, data_path):
        self.data = _load_csv(data_path)
        self._aggregate()

    def _aggregate(self):
        self.competitors = defaultdict(lambda: {
            'traffic_sum': 0, 'da_sum': 0, 'backlinks_sum': 0,
            'content_sum': 0, 'position_sum': 0, 'days': set()
        })
        for row in self.data:
            c = self.competitors[row['competitor_id']]
            c['name'] = row['competitor_name']
            c['domain'] = row['domain']
            c['traffic_sum'] += int(row['est_traffic'])
            c['da_sum'] += _safe_float(row['domain_authority'])
            c['backlinks_sum'] += int(row['backlinks'])
            c['content_sum'] += int(row['content_pieces'])
            c['position_sum'] += _safe_float(row['avg_position'])
            c['days'].add(row['date'])
        for c in self.competitors.values():
            n = max(len(c['days']), 1)
            c['avg_traffic'] = c['traffic_sum'] / n
            c['avg_da'] = c['da_sum'] / n
            c['avg_backlinks'] = c['backlinks_sum'] / n
            c['avg_content'] = c['content_sum'] / n
            c['avg_position'] = c['position_sum'] / n

    def analyze(self):
        opps = []
        for cid, c in self.competitors.items():
            # Backlink gap
            if c['avg_backlinks'] > 10000:
                opps.append(OptimizationOpportunity(
                    id=f"comp_bl_{cid}", channel=ChannelType.COMPETITOR,
                    title=f"Close backlink gap with {c['name']}",
                    description=f"{c['name']} has {c['avg_backlinks']:,.0f} backlinks. "
                                f"Targeted link building can capture their ranking share.",
                    current_value=0, projected_value=c['avg_backlinks'] * 0.3,
                    revenue_gain_monthly=round(c['avg_traffic'] * 0.001, 2),
                    effort=Effort.HIGH, impact=Impact.HIGH,
                    action_steps=[
                        f"Analyze {c['name']}'s top backlink sources",
                        "Create link-worthy content assets",
                        "Guest post on competitor's referring domains",
                        "Build resource page links",
                        "Monitor new competitor backlinks monthly"
                    ],
                    metrics={'competitor_backlinks': c['avg_backlinks']}
                ))

            # Content gap
            if c['avg_content'] > 500:
                opps.append(OptimizationOpportunity(
                    id=f"comp_content_{cid}", channel=ChannelType.COMPETITOR,
                    title=f"Close content gap with {c['name']}",
                    description=f"{c['name']} has {c['avg_content']:.0f} content pieces. "
                                f"Identify topics they cover that you don't.",
                    current_value=0, projected_value=c['avg_content'] * 0.2,
                    revenue_gain_monthly=round(c['avg_traffic'] * 0.0005, 2),
                    effort=Effort.VERY_HIGH, impact=Impact.MEDIUM,
                    action_steps=[
                        "Run content gap analysis using keyword tools",
                        "Prioritize topics by traffic potential and relevance",
                        "Create content calendar for missing topics",
                        "Produce 4-6 gap-filling articles per month",
                        "Track ranking improvements quarterly"
                    ],
                    metrics={'competitor_content': c['avg_content']}
                ))

            # Traffic opportunity from competitor weakness
            if c['avg_position'] > 12:
                opps.append(OptimizationOpportunity(
                    id=f"comp_weak_{cid}", channel=ChannelType.COMPETITOR,
                    title=f"Exploit {c['name']}'s weak rankings",
                    description=f"{c['name']} averages position {c['avg_position']:.0f}. "
                                f"Target their weak keywords to capture market share.",
                    current_value=0, projected_value=c['avg_traffic'] * 0.1,
                    revenue_gain_monthly=round(c['avg_traffic'] * 0.002, 2),
                    effort=Effort.MEDIUM, impact=Impact.HIGH,
                    action_steps=[
                        "Identify keywords where competitor ranks poorly",
                        "Create superior content for those keywords",
                        "Build links to outperform competitor pages",
                        "Monitor SERP movements weekly"
                    ],
                    metrics={'competitor_avg_position': round(c['avg_position'], 1)}
                ))

        for opp in opps:
            opp.compute_roi_score()
            opp.determine_priority()
        return opps


class EmailChannel:
    """Analyze list health, open rates, revenue per subscriber."""

    def __init__(self, data_path):
        self.data = _load_csv(data_path)
        self._aggregate()

    def _aggregate(self):
        self.lists = defaultdict(lambda: {
            'subscribers': 0, 'open_sum': 0.0, 'click_sum': 0.0,
            'unsub_sum': 0.0, 'revenue': 0.0, 'days': set()
        })
        for row in self.data:
            l = self.lists[row['list_id']]
            l['name'] = row['list_name']
            l['subscribers'] = int(row['subscribers'])
            l['open_sum'] += _safe_float(row['open_rate'])
            l['click_sum'] += _safe_float(row['click_rate'])
            l['unsub_sum'] += _safe_float(row['unsub_rate'])
            l['revenue'] += _safe_float(row['revenue'])
            l['days'].add(row['date'])
        for l in self.lists.values():
            n = max(len(l['days']), 1)
            l['avg_open'] = l['open_sum'] / n
            l['avg_click'] = l['click_sum'] / n
            l['avg_unsub'] = l['unsub_sum'] / n
            l['rps'] = l['revenue'] / max(l['subscribers'] * n, 1)

    def analyze(self):
        opps = []
        for lid, l in self.lists.items():
            # Low open rate
            if l['avg_open'] < 0.20:
                gain = l['subscribers'] * (0.25 - l['avg_open']) * l['avg_click'] * 1.5 * 30
                opps.append(OptimizationOpportunity(
                    id=f"email_open_{lid}", channel=ChannelType.EMAIL,
                    title=f"Improve open rate: {l['name']}",
                    description=f"Open rate {l['avg_open']*100:.1f}% is below 20% benchmark. "
                                f"Better subject lines and send times can boost engagement.",
                    current_value=l['avg_open'], projected_value=0.25,
                    revenue_gain_monthly=round(max(gain, 50), 2),
                    effort=Effort.LOW, impact=Impact.HIGH,
                    action_steps=[
                        "A/B test subject lines (personalization, urgency, curiosity)",
                        "Segment list by engagement level",
                        "Optimize send times based on open data",
                        "Clean inactive subscribers (>90 days no opens)",
                        "Test preview text optimization"
                    ],
                    metrics={'subscribers': l['subscribers'], 'open_rate': round(l['avg_open'], 3)}
                ))

            # High open rate but low click rate - content optimization
            if l['avg_open'] > 0.25 and l['avg_click'] < 0.03:
                gain = l['subscribers'] * l['avg_open'] * (0.05 - l['avg_click']) * 2.0 * 30
                opps.append(OptimizationOpportunity(
                    id=f"email_click_{lid}", channel=ChannelType.EMAIL,
                    title=f"Boost click rate: {l['name']}",
                    description=f"Good opens ({l['avg_open']*100:.1f}%) but low clicks ({l['avg_click']*100:.1f}%). "
                                f"Email content and CTAs need improvement.",
                    current_value=l['avg_click'], projected_value=0.05,
                    revenue_gain_monthly=round(max(gain, 40), 2),
                    effort=Effort.MEDIUM, impact=Impact.HIGH,
                    action_steps=[
                        "Redesign email template with clear CTA buttons",
                        "Add product images and compelling descriptions",
                        "Use personalization in content blocks",
                        "Test single-CTA vs multi-CTA emails",
                        "Implement dynamic content based on user behavior"
                    ],
                    metrics={'open_rate': round(l['avg_open'], 3), 'click_rate': round(l['avg_click'], 4)}
                ))

            # High unsubscribe rate
            if l['avg_unsub'] > 0.003:
                opps.append(OptimizationOpportunity(
                    id=f"email_unsub_{lid}", channel=ChannelType.EMAIL,
                    title=f"Reduce unsubscribe rate: {l['name']}",
                    description=f"Unsubscribe rate {l['avg_unsub']*100:.2f}% is high. "
                                f"List churn reduces long-term revenue potential.",
                    current_value=l['avg_unsub'], projected_value=0.002,
                    revenue_gain_monthly=round(l['subscribers'] * l['avg_unsub'] * 0.5 * 30, 2),
                    effort=Effort.LOW, impact=Impact.MEDIUM,
                    action_steps=[
                        "Implement frequency preference center",
                        "Add 'pause' option instead of unsubscribe",
                        "Improve content relevance and segmentation",
                        "Survey unsubscribers for feedback",
                        "Review and reduce email frequency if needed"
                    ],
                    metrics={'unsub_rate': round(l['avg_unsub'], 4)}
                ))

            # Low revenue per subscriber
            if l['rps'] < 0.01 and l['subscribers'] > 5000:
                target_rps = 0.03
                gain = (target_rps - l['rps']) * l['subscribers'] * 30
                opps.append(OptimizationOpportunity(
                    id=f"email_rps_{lid}", channel=ChannelType.EMAIL,
                    title=f"Increase revenue per subscriber: {l['name']}",
                    description=f"RPS ${l['rps']:.4f} is low for {l['subscribers']:,} subscribers. "
                                f"Better monetization can unlock significant revenue.",
                    current_value=l['rps'], projected_value=target_rps,
                    revenue_gain_monthly=round(max(gain, 100), 2),
                    effort=Effort.MEDIUM, impact=Impact.VERY_HIGH,
                    action_steps=[
                        "Segment subscribers by purchase history",
                        "Create targeted product recommendation emails",
                        "Implement automated post-purchase sequences",
                        "Add upsell/cross-sell to transactional emails",
                        "Test dedicated promotional sends vs mixed content"
                    ],
                    metrics={'rps': round(l['rps'], 4), 'subscribers': l['subscribers']}
                ))

        for opp in opps:
            opp.compute_roi_score()
            opp.determine_priority()
        return opps


class SocialChannel:
    """Analyze social media performance for optimization opportunities."""

    def __init__(self, data_path):
        self.data = _load_csv(data_path)
        self._aggregate()

    def _aggregate(self):
        self.platforms = defaultdict(lambda: {
            'followers': 0, 'impressions': 0, 'engagements': 0,
            'clicks': 0, 'revenue': 0.0, 'posts': 0, 'days': set()
        })
        for row in self.data:
            p = self.platforms[row['platform_id']]
            p['name'] = row['platform_name']
            p['followers'] = int(row['followers'])
            p['impressions'] += int(row['impressions'])
            p['engagements'] += int(row['engagements'])
            p['clicks'] += int(row['clicks'])
            p['revenue'] += _safe_float(row['revenue'])
            p['posts'] += int(row['posts'])
            p['days'].add(row['date'])
        for p in self.platforms.values():
            n = max(len(p['days']), 1)
            p['eng_rate'] = p['engagements'] / max(p['impressions'], 1)
            p['click_rate'] = p['clicks'] / max(p['engagements'], 1)
            p['rps'] = p['revenue'] / max(p['clicks'], 1)

    def analyze(self):
        opps = []
        for pid, p in self.platforms.items():
            # Low engagement rate
            if p['eng_rate'] < 0.03:
                gain = p['impressions'] * (0.05 - p['eng_rate']) * p['click_rate'] * p['rps'] / max(len(p['days']), 1) * 30
                opps.append(OptimizationOpportunity(
                    id=f"soc_eng_{pid}", channel=ChannelType.SOCIAL,
                    title=f"Boost engagement: {p['name']}",
                    description=f"Engagement rate {p['eng_rate']*100:.1f}% is low. "
                                f"Better content strategy can drive more traffic and revenue.",
                    current_value=p['eng_rate'], projected_value=0.05,
                    revenue_gain_monthly=round(max(gain, 30), 2),
                    effort=Effort.MEDIUM, impact=Impact.MEDIUM,
                    action_steps=[
                        "Analyze top-performing post types and topics",
                        "Increase video and interactive content",
                        "Post at optimal times for audience",
                        "Engage actively with comments and shares",
                        "Use trending hashtags and formats"
                    ],
                    metrics={'eng_rate': round(p['eng_rate'], 4), 'impressions': p['impressions']}
                ))

            # Low click-through from engagement
            if p['eng_rate'] > 0.03 and p['click_rate'] < 0.08:
                gain = p['engagements'] * (0.12 - p['click_rate']) * p['rps'] / max(len(p['days']), 1) * 30
                opps.append(OptimizationOpportunity(
                    id=f"soc_click_{pid}", channel=ChannelType.SOCIAL,
                    title=f"Improve click-through: {p['name']}",
                    description=f"Good engagement ({p['eng_rate']*100:.1f}%) but low clicks ({p['click_rate']*100:.1f}%). "
                                f"CTAs and link placement need optimization.",
                    current_value=p['click_rate'], projected_value=0.12,
                    revenue_gain_monthly=round(max(gain, 20), 2),
                    effort=Effort.LOW, impact=Impact.MEDIUM,
                    action_steps=[
                        "Add clear CTAs to every post",
                        "Use link-in-bio tools effectively",
                        "Create curiosity-driven content teasers",
                        "Test different link formats (direct vs landing page)",
                        "Pin top-converting posts"
                    ],
                    metrics={'click_rate': round(p['click_rate'], 4)}
                ))

        for opp in opps:
            opp.compute_roi_score()
            opp.determine_priority()
        return opps
