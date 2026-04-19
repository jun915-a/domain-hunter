import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

TRADEMARK_BLACKLIST = {
    "apple", "google", "amazon", "microsoft", "facebook", "twitter", "meta",
    "tesla", "toyota", "honda", "bmw", "sony", "samsung", "lg", "panasonic",
    "nike", "adidas", "puma", "gucci", "louis", "prada", "rolex", "cartier",
    "coca", "pepsi", "starbucks", "mcdonalds", "kfc", "uber", "airbnb",
    "netflix", "spotify", "disney", "warner", "paramount", "nba", "nfl",
    "bank", "chase", "wells", "citibank", "goldman", "jp morgan",
    "softbank", "rakuten", "yahoo", "line", "dena", "gree", "zynga"
}

def fetch_expired_domains(min_da=30, min_backlinks=20, pages=3):
    candidates = []

    for page in range(1, pages + 1):
        url = f"https://www.expireddomains.net/domain-name-search/?fwhois=22&fsimilar=0&falexa=0&fda={min_da}&fmajestic=0&fpi=0&start={( page - 1) * 25}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            res.raise_for_status()
        except Exception as e:
            print(f"[ERROR] fetch page {page}: {e}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.base1 tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 10:
                continue
            try:
                domain = cols[0].get_text(strip=True)
                da = int(cols[4].get_text(strip=True) or 0)
                bl = int(cols[6].get_text(strip=True).replace(",", "") or 0)

                if da >= min_da and bl >= min_backlinks and not check_trademark_risk(domain):
                    candidates.append({
                        "domain": domain,
                        "da": da,
                        "backlinks": bl,
                    })
            except Exception:
                continue

        time.sleep(2)

    return candidates


def check_trademark_risk(domain: str) -> bool:
    domain_lower = domain.lower().replace("www.", "").split(".")[0]
    for term in TRADEMARK_BLACKLIST:
        if term in domain_lower or domain_lower in term:
            return True
    return False


def check_wayback(domain):
    url = f"https://archive.org/wayback/available?url={domain}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        snapshot = data.get("archived_snapshots", {}).get("closest", {})
        return snapshot.get("available", False)
    except Exception:
        return False


def filter_with_wayback(candidates):
    results = []
    for item in candidates:
        has_history = check_wayback(item["domain"])
        if has_history:
            item["wayback"] = True
            results.append(item)
        time.sleep(1)
    return results


def run():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] スキャン開始")
    print("フィルタ: DA≥30, 被リンク≥20, 商標チェック済み")
    candidates = fetch_expired_domains(min_da=30, min_backlinks=20)
    print(f"候補: {len(candidates)}件 → Waybackチェック中...")
    filtered = filter_with_wayback(candidates)
    print(f"通過: {len(filtered)}件")

    with open("results.json", "w") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    return filtered


if __name__ == "__main__":
    run()
