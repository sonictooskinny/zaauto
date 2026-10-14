import csv, json, urllib.parse, urllib.request, time
from datetime import datetime, timezone

AREAS = [
    ("El Salam / El Nahda", 30.169, 31.447),
    ("Nasr City", 30.061, 31.337),
    ("Heliopolis", 30.087, 31.323),
]
RADIUS = 6000
SERVERS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
OUT = "restaurant_leads.csv"

def fetch(query):
    last = None
    for server in SERVERS:
        try:
            data = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(data=data, headers={"User-Agent": "FreeCairoRestaurantLeadFinder/1.0"})
            with urllib.request.urlopen(req, timeout=70) as resp:
                parsed = json.loads(resp.read().decode("utf-8"))
            return parsed.get("elements", [])
        except Exception as e:
            last = f"{server}: {e}"
            time.sleep(2)
    raise RuntimeError("All public map servers failed. " + str(last))

def val(tags, *keys):
    for k in keys:
        if tags.get(k): return str(tags[k])
    return ""

def main():
    seen, rows = set(), []
    for area, lat, lon in AREAS:
        query = (
            '[out:json][timeout:60];('
            'nwr["amenity"~"^(restaurant|cafe|fast_food|food_court|ice_cream)$"]'
            f'(around:{RADIUS},{lat},{lon}););out center tags;'
        )
        for el in fetch(query):
            t = el.get("tags", {})
            name = val(t, "name", "name:en", "name:ar")
            if not name: continue
            center = el.get("center", {})
            xlat = el.get("lat", center.get("lat"))
            xlon = el.get("lon", center.get("lon"))
            address = ", ".join(x for x in [
                " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x),
                val(t, "addr:suburb", "addr:neighbourhood", "addr:district") or area,
                val(t, "addr:city") or "Cairo"
            ] if x)
            key = (name + "|" + address).lower()
            if key in seen: continue
            seen.add(key)
            phone = val(t, "phone", "contact:phone", "contact:mobile")
            email = val(t, "email", "contact:email")
            website = val(t, "website", "contact:website")
            maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(name + " " + address + " Cairo Egypt")
            osm = f"https://www.openstreetmap.org/?mlat={xlat}&mlon={xlon}#map=18/{xlat}/{xlon}" if xlat is not None and xlon is not None else "https://www.openstreetmap.org/"
            digits = "".join(c for c in phone if c.isdigit())
            if digits.startswith("0"): digits = "20" + digits[1:]
            elif len(digits) == 10 and not digits.startswith("20"): digits = "20" + digits
            wa = "https://wa.me/" + digits if len(digits) >= 10 else ""
            english = f"Hi {name}! I'm a web designer based in Cairo. I help restaurants create a clean, mobile-friendly website with their menu, location, contact details, and WhatsApp ordering. Would you be open to seeing a sample design?"
            arabic = f"أهلاً {name}، أنا مصمم مواقع من القاهرة. بساعد المطاعم تعمل موقع بسيط وسريع للموبايل فيه المنيو والموقع وبيانات التواصل والطلب عن طريق واتساب. تحبوا أوريكم نموذج تصميم مناسب لمطعمكم؟"
            rows.append({
                "Lead Status":"New", "Business":name, "Type":val(t,"amenity") or "food business",
                "Search Area":area, "Phone":phone, "Email":email, "Website":website,
                "Website Signal":"Website listed — verify it works" if website else "No website tagged — verify manually",
                "Address":address, "Google Maps":maps, "WhatsApp Link":wa,
                "English Pitch":english, "Egyptian Arabic Pitch":arabic, "OSM Source":osm,
                "Last Refreshed":datetime.now(timezone.utc).isoformat(),
                "Notes":"Missing website tag is not proof that no website exists; verify before outreach."
            })
    fields = ["Lead Status","Business","Type","Search Area","Phone","Email","Website","Website Signal","Address","Google Maps","WhatsApp Link","English Pitch","Egyptian Arabic Pitch","OSM Source","Last Refreshed","Notes"]
    rows.sort(key=lambda r: (bool(r["Website"]), r["Business"].lower()))
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {OUT} with {len(rows)} leads.")

if __name__ == "__main__":
    main()
