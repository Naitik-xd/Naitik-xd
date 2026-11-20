import json
import os
import re
from collections import defaultdict
from datetime import datetime
import requests

USERNAME = "Naitik-xd"
OUT_PATH = "data/contributions.json"


def fetch_contributions(username: str) -> dict:
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    html = resp.text

    # Parse date and level from contribution cells
    day_pattern = re.compile(
        r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"'
    )
    # Parse tooltips like "5 contributions on October 12th."
    tooltip_pattern = re.compile(
        r'id="contribution-day-component-\d+-\d+"[^>]*>([^<]+)</tool-tip>'
    )
    cell_id_pattern = re.compile(
        r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-\d+-\d+)"[^>]*data-level="(\d)"'
    )

    # Map cell id -> count from tooltips
    tooltip_map = {}
    for m in re.finditer(r'for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]+)<', html):
        cid, text = m.group(1), m.group(2).strip()
        num = re.search(r"(\d+)\s+contribution", text)
        tooltip_map[cid] = int(num.group(1)) if num else 0

    days = []
    for m in cell_id_pattern.finditer(html):
        date_str, cid, level = m.group(1), m.group(2), int(m.group(3))
        count = tooltip_map.get(cid, level * 2 if level > 0 else 0)
        days.append({"date": date_str, "count": count, "level": level})

    # Fallback if GitHub changes attribute order
    if not days:
        for m in day_pattern.finditer(html):
            date_str, level = m.group(1), int(m.group(2))
            days.append({"date": date_str, "count": level * 2, "level": level})

    days.sort(key=lambda d: d["date"])

    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)

    # Monthly totals (last 12 months)
    monthly = defaultdict(int)
    for d in days:
        ym = d["date"][:7]
        monthly[ym] += d["count"]
    sorted_months = sorted(monthly.items())[-12:]
    months_list = [
        {"month": datetime.strptime(ym, "%Y-%m").strftime("%b"), "ym": ym, "count": cnt}
        for ym, cnt in sorted_months
    ]

    # Longest & current streak
    longest_streak = 0
    temp_streak = 0
    for d in days:
        if d["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        elif current_streak > 0:
            break

    # Busiest day
    busiest = max(days, key=lambda d: d["count"]) if days else {"date": "—", "count": 0}
    busiest_label = (
        datetime.strptime(busiest["date"], "%Y-%m-%d").strftime("%b %d")
        if busiest["date"] != "—"
        else "—"
    )

    return {
        "username": username,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "total": total,
        "active_days": active_days,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "busiest_day": busiest_label,
        "busiest_count": busiest["count"],
        "months": months_list,
        "days": days[-364:],
    }


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    data = fetch_contributions(USERNAME)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {data['total']} contributions to {OUT_PATH}")
