# Family Secret Santa — Magic Hat

A small Python program that randomly decides who gifts whom for the family Secret
Santa, respects every restriction (never yourself, never your partner, never someone
you have already gifted), and emails each participant **only their own secret
assignment**. The organizer can play along without ever knowing who is gifting them.

Everything lives in one folder. Nothing to install except Python.

## The files

| File | What it is |
| --- | --- |
| `Magic Hat.py` | The program. No need to edit it. |
| `Gifternames.json` | This year's roster plus every restriction. **Edited by hand once a year.** |
| `Gifteremails.json` | Where each gifter's email gets sent. |
| `secret.py` | The Gmail account + app password used to send. **Contains a secret — never share it, never put it in a public repo.** |
| `Magic Hat Log File.log` | Running log (created automatically; safe to ignore or delete). |
| `<YEAR> Output.txt` | The full assignment, written the moment the emails go out (e.g. `2026 Output.txt`). **Do not read it before the exchange** — it contains who is gifting you. Archive it after the exchange. |

## How it works

1. `Gifternames.json` is a list of gifters. Each gifter is an object whose **values**
   are the names they may **not** gift. The keys are just labels for your own
   reference — the program reads the values and ignores the keys. Convention:
   `"Partner"` for the spouse, and the year (e.g. `"2025"`) for each past pairing.

   ```json
   [
     {"Name": "Alpha", "Partner": "Beta", "2024": "Gamma", "2025": "Delta"},
     {"Name": "Beta",  "Partner": "Alpha", "2025": "Epsilon"}
   ]
   ```

   A gifter's excluded set is therefore every value in their object: themselves
   (the `"Name"` value — that is how self-gifting is ruled out), their partner, and
   everyone they have gifted in past years.

2. `Gifteremails.json` maps each gifter to an address:

   ```json
   [
     {"Name": "Alpha", "Email": "alpha@example.com"},
     {"Name": "Beta",  "Email": "beta@example.com"}
   ]
   ```

3. When `Magic Hat.py` starts, it builds **one** valid random assignment for the
   whole roster (most-restricted gifter first). If the restrictions make the game
   impossible, it stops immediately with a big error and waits for Enter — that is
   the "can we play this year?" check.

4. The menu:
   - **1** — view the current gifters (names only, never assignments).
   - **2** — email this year's list: each gifter gets an email telling them who they
     are gifting, and the full mapping is written to `<YEAR> Output.txt` in this folder.
   - **3** — exit.

5. Every launch builds a **fresh random list**. Emails are sent only on the launch
   where you pick **2**. Once you have sent, **do not run option 2 again** — a
   re-run would email a second, different list. The log records a "Sent to …" line
   per person if you ever need to check what went out.

## First-time setup

1. Install Python 3 (any recent version).
2. Create `Gifternames.json` and `Gifteremails.json` in the shapes shown above.
3. Create a Gmail **app password**: Google Account → Security → 2-Step Verification
   → App passwords. (This is not your regular password.)
4. Create `secret.py` with exactly these two lines:

   ```python
   sent_from = "you@gmail.com"
   API_key = "abcd efgh ijkl mnop"
   ```

5. Run the program: double-click `Magic Hat.py`, or from a terminal in this folder:
   `python Magic Hat.py`.

## Annual maintenance (the calendar)

1. **After the exchange (January) — update the history.** Open last year's
   `<YEAR> Output.txt` and, pairing by pairing, add each gifter's recipient to their
   object in `Gifternames.json` under a new key named for that year:

   ```json
   {"Name": "Alpha", "Partner": "Beta", "2025": "Gamma", "2026": "Delta"}
   ```

   This is the step that prevents anyone from gifting the same person twice. (Nice
   to do by hand — the secrets get revealed one by one.) Then move
   `<YEAR> Output.txt` into an `archive` folder.

2. **Around Nov 1 — ask the group.** Email everyone the current roster, ask for
   opt-outs or additions, and allow at least a week for responses:

   > Hello once again, and happy Friday!
   >
   > Hard to believe the first week of November is almost over already, but that
   > means it is time once again to figure out who will comprise our `<YEAR>`
   > Secret Santa players. Please let me know if you'd like to opt-out or see
   > anyone missing from the list below! Here is what I have from last year:
   >
   > `<list of names>`
   >
   > As a reminder the gift limit is $75, and gifts must be in your recipient's
   > hands no later than Christmas Day (December 25, `<YEAR>`)
   >
   > Love,
   > -Alex

3. **Apply the final roster.** In both JSON files: add new participants (a new
   gifter object plus a new email entry) and remove anyone who opted out. A brand-new
   joiner only needs `{"Name": "..."}` (plus `"Partner"` if applicable) — they have
   no history yet. A returning former participant starts fresh the same way; re-add
   old pairings only if you want to keep excluding them.

4. **Sanity check.** Launch `Magic Hat.py`. If it prints
   `CRITICAL ERROR: NO VALID GIFT LIST POSSIBLE - CHECK RESTRICTIONS`, the
   restrictions are too tight (small roster + lots of partners is the usual cause)
   — loosen something and start again. If it reaches the menu, the game is playable.
   The startup log line per gifter (…N possible recipients) shows anyone whose pool
   is dangerously small.

5. **By Nov 15 — send it.** Pick **2** in the menu. Done for the year.

## Troubleshooting

- **`NO VALID GIFT LIST POSSIBLE`** — restrictions contradict each other. See the
  startup pool sizes in the log and loosen the tightest gifter's list.
- **`FAILED TO LOGIN TO GMAIL`** — check `secret.py`. App passwords are 16
  characters with spaces; create a fresh one in Gmail if it was revoked.
- **`FAILED TO SEND …` (mid-loop)** — the program stops, but the partial
  `<YEAR> Output.txt` already contains everyone's assignment, including the person
  whose email failed. The clean fix: email the missing person(s) **manually** from
  that file, keeping the original list intact. Do not re-run option 2 (it would
  email a brand-new list to everyone).
- **Error flashes and the window closes** — it should no longer: every error path
  now waits at "Press Enter to exit…" before closing.
- **Double-click does nothing** — make sure `.py` files are associated with Python,
  or run `python Magic Hat.py` from a terminal in this folder.

## Privacy

Only `Magic Hat.py` and this README are safe to share publicly. `Gifternames.json`,
`Gifteremails.json`, `secret.py`, the log, and every `Output.txt` contain personal
data — keep them on the family NAS and off any public repository.
