from scraper import run
from notifier import build_message, send_discord

domains = run()
msg = build_message(domains)
send_discord(msg)
