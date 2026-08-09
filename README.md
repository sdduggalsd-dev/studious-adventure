# GRE word-of-the-hour (Telegram)

Sends you one GRE word from your 1,112-word list every waking hour, via a Telegram bot,
run for free on GitHub Actions. Words are ordered by GRE value — all the ⭐⭐⭐⭐⭐ Essential
words come first, then ⭐⭐⭐⭐, and so on — so the first few weeks cover the highest-payoff
vocabulary. It walks the whole list, then loops for a second pass.

No servers, no billing, no message templates.

---

## One-time setup (about 10 minutes)

### 1. Create the bot and get its token
1. In Telegram, message **@BotFather**.
2. Send `/newbot`, pick a name and a username ending in `bot`.
3. BotFather replies with a **token** like `123456789:AAE...`. Keep it.

### 2. Get your chat id
1. Send any message (e.g. "hi") to your new bot so it's allowed to message you back.
2. Open this URL in a browser, pasting your token in:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat":{"id":<number>` — that number is your **chat id**.
   (Alternative: message **@userinfobot**, which just replies with your id.)

### 3. Put it in a GitHub repo
1. Create a new GitHub repo (public is fine and keeps free minutes unlimited).
2. Upload these files, keeping the folder layout — the workflow **must** stay at
   `.github/workflows/vocab.yml`.
3. In the repo: **Settings → Secrets and variables → Actions → New repository secret**.
   Add two secrets:
   - `TELEGRAM_BOT_TOKEN` = the token from step 1
   - `TELEGRAM_CHAT_ID` = the id from step 2

### 4. Test it
- Go to the **Actions** tab → **GRE word of the hour** → **Run workflow**.
- To bypass the waking-hours check during testing, either run it during 08:00–22:00 IST,
  or add a temporary repo secret `FORCE_SEND` = `1` (delete it afterwards).
- You should get a word in Telegram within a few seconds.

That's it. From then on it fires by itself, roughly on the hour.

---

## Tuning

- **Waking hours** (default 08:00–22:00 IST → ~15 words/day): edit `ACTIVE_HOURS_START` /
  `ACTIVE_HOURS_END` in `.github/workflows/vocab.yml`, or set them as repo secrets.
- **Frequency**: change the `cron:` line. `0 */2 * * *` = every 2 hours; `0 9,13,18 * * *`
  = three fixed times (all in **UTC** — IST is UTC+5:30, so 09:00 UTC = 14:30 IST).
- **Start somewhere specific**: edit `cursor` in `state.json` (0 = first word).
- **Message wording**: edit `build_message()` in `send_word.py`.

## How progress is saved

GitHub Actions has no memory between runs, so after each send the workflow commits the new
`cursor` in `state.json` back to the repo. A useful side effect: those commits keep the repo
"active", which stops GitHub from auto-disabling scheduled workflows on idle repos.

## Good to know

- Scheduled Actions run on **UTC** and can be **delayed 5–30+ minutes** at busy times, and a
  run can occasionally be skipped under heavy load. Fine for a habit nudge; don't rely on the
  exact minute.
- Runs outside your waking-hours window exit immediately without sending or committing.
- Nothing here costs money on a normal free account.

## Files

    words.json                     1,112 words: word, definition, example, theme, priority
    send_word.py                   picks the next word, sends it, advances the cursor
    state.json                     saved progress (cursor / pass number / totals)
    .github/workflows/vocab.yml    the hourly schedule
