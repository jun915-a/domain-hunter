import requests
import os
import json

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")


def send_discord(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("[WARN] DISCORD_WEBHOOK_URL が未設定です")
        return
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})


def build_message(domains: list) -> str:
    if not domains:
        return "本日の候補ドメインはありませんでした。"

    lines = [f"**【期限切れドメイン候補】{len(domains)}件**\n"]
    for d in domains[:10]:
        lines.append(f"・`{d['domain']}` DA:{d['da']} / 被リンク:{d['backlinks']}")
    if len(domains) > 10:
        lines.append(f"...他{len(domains) - 10}件はresults.jsonを確認")
    return "\n".join(lines)


if __name__ == "__main__":
    with open("results.json") as f:
        domains = json.load(f)
    msg = build_message(domains)
    send_discord(msg)
    print(msg)
