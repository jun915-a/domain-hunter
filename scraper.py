import csv
import json
from datetime import datetime
import time

TRADEMARK_BLACKLIST = {
    "apple", "google", "amazon", "microsoft", "facebook", "twitter", "meta",
    "tesla", "toyota", "honda", "bmw", "sony", "samsung", "lg", "panasonic",
    "nike", "adidas", "puma", "gucci", "louis", "prada", "rolex", "cartier",
    "coca", "pepsi", "starbucks", "mcdonalds", "kfc", "uber", "airbnb",
    "netflix", "spotify", "disney", "warner", "paramount", "nba", "nfl",
    "bank", "chase", "wells", "citibank", "goldman", "softbank", "rakuten",
    "yahoo", "line", "dena", "gree", "zynga"
}


def check_trademark_risk(domain: str) -> bool:
    domain_lower = domain.lower().replace("www.", "").split(".")[0]
    for term in TRADEMARK_BLACKLIST:
        if term in domain_lower or domain_lower in term:
            return True
    return False


def load_domains_from_csv(filename="domains.csv"):
    """domains.csvから候補ドメインを読み込む"""
    try:
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            domains = []
            for row in reader:
                domain = row.get("domain", "").strip()
                if domain:
                    domains.append({
                        "domain": domain,
                        "da": int(row.get("da", 0) or 0),
                        "backlinks": int(row.get("backlinks", 0) or 0),
                    })
            return domains
    except FileNotFoundError:
        print(f"[ERROR] {filename} が見つかりません")
        return []


def filter_domains(domains):
    """商標チェック + 基本フィルタリング"""
    filtered = []
    for item in domains:
        domain = item.get("domain")
        if check_trademark_risk(domain):
            print(f"  [NG] {domain} (商標リスク)")
            continue
        filtered.append(item)
    return filtered


def check_wayback(domain):
    """Wayback Machineで過去のサイト履歴確認"""
    import requests
    url = f"https://archive.org/wayback/available?url={domain}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        snapshot = data.get("archived_snapshots", {}).get("closest", {})
        return snapshot.get("available", False)
    except Exception:
        return False


def filter_with_wayback(candidates):
    """Waybackチェック"""
    results = []
    for item in candidates:
        has_history = check_wayback(item["domain"])
        if has_history:
            item["wayback"] = True
            results.append(item)
            print(f"  [OK] {item['domain']} (DA:{item['da']} BL:{item['backlinks']})")
        else:
            print(f"  [スキップ] {item['domain']} (Wayback履歴なし)")
        time.sleep(0.5)
    return results


def run():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] スキャン開始")

    # CSVから読み込み
    domains = load_domains_from_csv("domains.csv")
    print(f"読み込み: {len(domains)}件")

    if len(domains) == 0:
        print("\n[INFO] domains.csvにドメインを入力してください")
        print("  フォーマット: domain,da,backlinks")
        print("  例:")
        print("    example.com,25,10")
        print("    test.com,30,15")
        return []

    # 商標チェック
    print("\n商標チェック中...")
    filtered = filter_domains(domains)
    print(f"通過: {len(filtered)}件")

    if len(filtered) == 0:
        return []

    # Waybackチェック
    print("\nWayback履歴確認中...")
    results = filter_with_wayback(filtered)
    print(f"最終: {len(results)}件")

    # 結果保存
    with open("results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


if __name__ == "__main__":
    run()
