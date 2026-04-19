import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def fetch_expired_domains(min_da=20, min_backlinks=10, pages=3):
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

                if da >= min_da and bl >= min_backlinks:
                    candidates.append({
                        "domain": domain,
                        "da": da,
                        "backlinks": bl,
                    })
            except Exception:
                continue

        time.sleep(2)

    return candidates


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
    candidates = fetch_expired_domains(min_da=20, min_backlinks=10)
    print(f"候補: {len(candidates)}件 → Waybackチェック中...")
    filtered = filter_with_wayback(candidates)
    print(f"通過: {len(filtered)}件")

    with open("results.json", "w") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    return filtered


if __name__ == "__main__":
    run()
