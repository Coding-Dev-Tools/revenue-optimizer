"""
Synthetic data generator for Revenue Optimization Engine.
Generates realistic channel performance data with embedded optimization opportunities.
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta

random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def generate_affiliate_data(days=90):
    """Generate affiliate channel performance data with optimization signals."""
    base_date = datetime.now() - timedelta(days=days)
    rows = []
    base_clicks = 2000
    base_conv = 0.032
    base_epc = 0.45

    affiliates = [
        {"id": "aff_001", "name": "TechReviewPro", "niche": "electronics"},
        {"id": "aff_002", "name": "GadgetGuru", "niche": "electronics"},
        {"id": "aff_003", "name": "HomeEssentials", "niche": "home"},
        {"id": "aff_004", "name": "FitLifeDeals", "niche": "fitness"},
        {"id": "aff_005", "name": "BudgetBuyer", "niche": "general"},
        {"id": "aff_006", "name": "PremiumPickz", "niche": "luxury"},
        {"id": "aff_007", "name": "EcoFriendlyShop", "niche": "sustainability"},
        {"id": "aff_008", "name": "PetParadise", "niche": "pets"},
    ]

    for d in range(days):
        date = base_date + timedelta(days=d)
        for aff in affiliates:
            noise = random.uniform(0.8, 1.2)
            # Some affiliates have clear issues (low EPC, declining conversions)
            if aff["id"] == "aff_005":
                clicks = int(base_clicks * 1.5 * noise)
                conv = base_conv * 0.5 * noise  # low conversion
                epc = base_epc * 0.4 * noise
            elif aff["id"] == "aff_006":
                clicks = int(base_clicks * 0.6 * noise)
                conv = base_conv * 2.0 * noise  # high conversion, low volume
                epc = base_epc * 2.5 * noise
            elif aff["id"] == "aff_002":
                # declining trend
                trend = 1.0 - (d / days) * 0.3
                clicks = int(base_clicks * noise * trend)
                conv = base_conv * noise * trend
                epc = base_epc * noise * trend
            else:
                clicks = int(base_clicks * noise)
                conv = base_conv * noise
                epc = base_epc * noise

            sales = max(1, int(clicks * conv))
            revenue = round(clicks * conv * epc * 20, 2)
            commission = round(revenue * 0.08, 2)

            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "affiliate_id": aff["id"],
                "affiliate_name": aff["name"],
                "niche": aff["niche"],
                "clicks": clicks,
                "conversions": sales,
                "conversion_rate": round(conv, 4),
                "epc": round(epc, 4),
                "revenue": revenue,
                "commission": commission,
            })
    return rows


def generate_content_data(days=90):
    base_date = datetime.now() - timedelta(days=days)
    rows = []
    pages = [
        {"id": "pg_001", "title": "Best Laptops 2026", "type": "review", "age_days": 120},
        {"id": "pg_002", "title": "How to Start a Blog", "type": "howto", "age_days": 200},
        {"id": "pg_003", "title": "Top 10 VPN Services", "type": "review", "age_days": 45},
        {"id": "pg_004", "title": "Budget Meal Planning", "type": "guide", "age_days": 90},
        {"id": "pg_005", "title": "Remote Work Setup Guide", "type": "guide", "age_days": 150},
        {"id": "pg_006", "title": "SEO Basics 2026", "type": "howto", "age_days": 30},
        {"id": "pg_007", "title": "Old Product Roundup", "type": "review", "age_days": 400},
        {"id": "pg_008", "title": "Fitness Tracker Comparison", "type": "review", "age_days": 60},
    ]
    for d in range(days):
        date = base_date + timedelta(days=d)
        for pg in pages:
            noise = random.uniform(0.7, 1.3)
            if pg["age_days"] > 300:
                sessions = int(150 * noise * 0.3)  # stale content
            elif pg["type"] == "review":
                sessions = int(800 * noise)
            else:
                sessions = int(400 * noise)

            bounce = round(random.uniform(0.3, 0.7), 3)
            avg_time = round(random.uniform(1.0, 5.0), 1)
            monetized = random.random() < (0.8 if pg["type"] == "review" else 0.3)
            revenue = round(sessions * random.uniform(0.05, 0.3) if monetized else 0, 2)

            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "page_id": pg["id"],
                "page_title": pg["title"],
                "content_type": pg["type"],
                "sessions": sessions,
                "bounce_rate": bounce,
                "avg_time_min": avg_time,
                "monetized": monetized,
                "revenue": revenue,
            })
    return rows


def generate_seo_data(days=90):
    base_date = datetime.now() - timedelta(days=days)
    rows = []
    keywords = [
        {"kw": "best laptops 2026", "current_rank": 4, "volume": 18000, "cpc": 2.5},
        {"kw": "vpn comparison", "current_rank": 12, "volume": 22000, "cpc": 3.1},
        {"kw": "budget meal prep", "current_rank": 7, "volume": 9500, "cpc": 0.8},
        {"kw": "remote work accessories", "current_rank": 18, "volume": 6000, "cpc": 1.9},
        {"kw": "fitness tracker reviews", "current_rank": 3, "volume": 14000, "cpc": 2.0},
        {"kw": "seo tools 2026", "current_rank": 25, "volume": 8000, "cpc": 4.2},
        {"kw": "standing desk review", "current_rank": 8, "volume": 11000, "cpc": 2.8},
        {"kw": "home office setup", "current_rank": 15, "volume": 7500, "cpc": 1.5},
    ]
    for d in range(days):
        date = base_date + timedelta(days=d)
        for kw in keywords:
            noise = random.uniform(0.9, 1.1)
            rank = max(1, kw["current_rank"] + random.randint(-2, 2))
            ctr = max(0.001, (0.3 / rank) * noise)
            impressions = int(kw["volume"] / 30 * noise)
            clicks = int(impressions * ctr)
            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "keyword": kw["kw"],
                "position": rank,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr, 4),
                "search_volume": kw["volume"],
                "cpc": kw["cpc"],
            })
    return rows


def generate_email_data(days=90):
    base_date = datetime.now() - timedelta(days=days)
    rows = []
    lists = [
        {"id": "list_001", "name": "Weekly Deals", "size": 15000, "freq": "weekly"},
        {"id": "list_002", "name": "Product Launches", "size": 8000, "freq": "biweekly"},
        {"id": "list_003", "name": "Newsletter Digest", "size": 22000, "freq": "weekly"},
        {"id": "list_004", "name": "VIP Buyers", "size": 3000, "freq": "monthly"},
    ]
    for d in range(days):
        date = base_date + timedelta(days=d)
        for lst in lists:
            noise = random.uniform(0.85, 1.15)
            open_rate = round(random.uniform(0.15, 0.35) * noise, 3)
            click_rate = round(open_rate * random.uniform(0.1, 0.4), 4)
            unsub_rate = round(random.uniform(0.001, 0.005) * noise, 4)
            revenue = round(lst["size"] * click_rate * random.uniform(0.5, 2.0), 2)
            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "list_id": lst["id"],
                "list_name": lst["name"],
                "subscribers": lst["size"],
                "open_rate": open_rate,
                "click_rate": click_rate,
                "unsub_rate": unsub_rate,
                "revenue": revenue,
            })
    return rows


def generate_competitor_data(days=90):
    base_date = datetime.now() - timedelta(days=days)
    rows = []
    competitors = [
        {"id": "comp_001", "name": "RivalReviews", "domain": "rivalreviews.com"},
        {"id": "comp_002", "name": "TopPickDaily", "domain": "toppickdaily.com"},
        {"id": "comp_003", "name": "DealHunterPro", "domain": "dealhunterpro.com"},
    ]
    for d in range(days):
        date = base_date + timedelta(days=d)
        for comp in competitors:
            noise = random.uniform(0.9, 1.1)
            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "competitor_id": comp["id"],
                "competitor_name": comp["name"],
                "domain": comp["domain"],
                "est_traffic": int(random.uniform(50000, 200000) * noise),
                "domain_authority": round(random.uniform(40, 70) * noise, 1),
                "backlinks": int(random.uniform(5000, 30000) * noise),
                "content_pieces": int(random.uniform(200, 800) * noise),
                "avg_position": round(random.uniform(5, 20) * noise, 1),
            })
    return rows


def generate_social_data(days=90):
    base_date = datetime.now() - timedelta(days=days)
    rows = []
    platforms = [
        {"id": "soc_twitter", "name": "Twitter/X", "followers": 25000},
        {"id": "soc_instagram", "name": "Instagram", "followers": 18000},
        {"id": "soc_youtube", "name": "YouTube", "followers": 12000},
        {"id": "soc_pinterest", "name": "Pinterest", "followers": 8000},
    ]
    for d in range(days):
        date = base_date + timedelta(days=d)
        for plat in platforms:
            noise = random.uniform(0.8, 1.2)
            posts = random.randint(1, 5)
            impressions = int(plat["followers"] * random.uniform(0.05, 0.3) * noise * posts)
            engagements = int(impressions * random.uniform(0.01, 0.08))
            clicks = int(engagements * random.uniform(0.05, 0.2))
            revenue = round(clicks * random.uniform(0.1, 0.5), 2)
            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "platform_id": plat["id"],
                "platform_name": plat["name"],
                "followers": plat["followers"],
                "posts": posts,
                "impressions": impressions,
                "engagements": engagements,
                "clicks": clicks,
                "revenue": revenue,
            })
    return rows


def save_csv(data, filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    if not data:
        return path
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return path


def save_json(data, filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path


def generate_all(days=90):
    """Generate all synthetic datasets and save to CSV."""
    generators = {
        "affiliate_performance.csv": generate_affiliate_data,
        "content_performance.csv": generate_content_data,
        "seo_performance.csv": generate_seo_data,
        "email_performance.csv": generate_email_data,
        "competitor_metrics.csv": generate_competitor_data,
        "social_performance.csv": generate_social_data,
    }
    paths = {}
    for filename, gen_func in generators.items():
        data = gen_func(days)
        path = save_csv(data, filename)
        paths[filename] = path
    return paths


if __name__ == "__main__":
    generate_all()
