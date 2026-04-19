import requests
import os
import json

LINE_TOKEN = os.environ.get("LINE_NOTIFY_TOKEN", "")


def send_line(message: str):
    if not LINE_TOKEN:
        print("[WARN] LINE_NOTIFY_TOKEN が未設定です")
        return
    requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {LINE_TOKEN}"},
        data={"message": message},
    )


def build_message(domains: list) -> str:
    if not domains:
        return "\n本日の候補ドメインはありませんでした。"

    lines = [f"\n【期限切れドメイン候補】{len(domains)}件\n"]
    for d in domains[:10]:
        lines.append(
            f"・{d['domain']}\n  DA:{d['da']} / 被リンク:{d['backlinks']}"
        )
    if len(domains) > 10:
        lines.append(f"...他{len(domains) - 10}件はresults.jsonを確認")
    return "\n".join(lines)


if __name__ == "__main__":
    with open("results.json") as f:
        domains = json.load(f)
    msg = build_message(domains)
    send_line(msg)
    print(msg)
