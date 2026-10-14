# Free Cairo Restaurant Lead Finder

No Apps Script, paid API key, Apollo plan, or email subscription required.

## Install from your phone

1. Sign in to GitHub and create a **public repository** named `cairo-restaurant-leads`.
2. Upload these files preserving the folder structure:
   - `lead_finder.py`
   - `.github/workflows/daily.yml`
3. Open the repository's **Actions** tab and enable workflows if GitHub asks.
4. Choose **Refresh Cairo restaurant leads** → **Run workflow**.
5. When it finishes, open the run → download the `cairo-restaurant-leads` artifact. It contains `restaurant_leads.csv`, which opens in Google Sheets or Excel.
6. GitHub Actions will run it daily at 06:15 UTC (08:15 Cairo time during UTC+2; 09:15 during UTC+3).

## What it does
- Queries free OpenStreetMap public data around El Salam/El Nahda, Nasr City, and Heliopolis.
- Includes available public phone/email/website tags and map links.
- Generates English and Egyptian Arabic pitches.
- Tries multiple public Overpass servers if one is unavailable.

## Important limitations
- OpenStreetMap coverage is incomplete. Missing website tag does **not** prove a restaurant has no website.
- This version prepares leads and messages; it does not send emails or WhatsApp messages.
- Public repository means the script is visible to everyone, but the generated leads artifact contains public business listing data. Do not add personal secrets.
