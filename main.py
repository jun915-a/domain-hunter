from scraper import run
from notifier import build_message, send_line

domains = run()
msg = build_message(domains)
send_line(msg)
