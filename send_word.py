#!/usr/bin/env python3
"""
Sends one GRE vocab word to a Telegram chat and advances a saved cursor.
Runs statelessly on GitHub Actions; state.json is committed back after each send.

Env vars (set as GitHub Secrets, or export locally):
  TELEGRAM_BOT_TOKEN   required  - from @BotFather
  TELEGRAM_CHAT_ID     required  - your numeric chat id
  ACTIVE_HOURS_START   optional  - IST hour to start sending (default 8)
  ACTIVE_HOURS_END     optional  - IST hour to stop sending (default 22)
  FORCE_SEND           optional  - "1" to ignore the waking-hours gate (for testing)
"""
import json, os, sys, html, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS_PATH = os.path.join(HERE, "words.json")
STATE_PATH = os.path.join(HERE, "state.json")

IST = timezone(timedelta(hours=5, minutes=30))
STARS = {5: "⭐⭐⭐⭐⭐", 4: "⭐⭐⭐⭐", 3: "⭐⭐⭐", 2: "⭐⭐", 1: "⭐"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def within_active_hours():
    if os.environ.get("FORCE_SEND") == "1":
        return True
    start = int(os.environ.get("ACTIVE_HOURS_START", "8"))
    end = int(os.environ.get("ACTIVE_HOURS_END", "22"))
    hour = datetime.now(IST).hour
    return start <= hour <= end


def build_message(entry, position, total, cycle):
    w = html.escape(entry["w"])
    d = html.escape(entry["d"])
    e = html.escape(entry["e"])
    t = html.escape(entry["t"])
    stars = STARS.get(entry["p"], "")
    cycle_tag = f" · pass {cycle}" if cycle > 1 else ""
    return (
        f"📖 <b>Word {position} of {total}</b>{cycle_tag}\n\n"
        f"<b>{w}</b>  {stars}\n"
        f"{d}\n\n"
        f"<i>e.g.</i> {e}\n\n"
        f"<i>Theme:</i> {t}"
    )


def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode())
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API error: {payload}")
    return payload


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID; nothing sent.")
        sys.exit(0)

    if not within_active_hours():
        print("Outside active hours (IST); skipping this run.")
        sys.exit(0)

    words = load(WORDS_PATH)
    total = len(words)
    state = load(STATE_PATH)
    cursor = state.get("cursor", 0)
    cycle = state.get("cycle", 1)

    if cursor >= total:            # completed a full pass, start the next one
        cursor = 0
        cycle += 1

    entry = words[cursor]
    text = build_message(entry, cursor + 1, total, cycle)
    send_telegram(token, chat_id, text)
    print(f"Sent '{entry['w']}' ({cursor + 1}/{total}, pass {cycle}).")

    state["cursor"] = cursor + 1
    state["cycle"] = cycle
    state["sent_total"] = state.get("sent_total", 0) + 1
    state["last_sent_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_state(state)


if __name__ == "__main__":
    main()
