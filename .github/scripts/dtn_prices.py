# Weekly: read DTN's latest retail fertilizer price report and save the
# national average prices ($/ton) to dtn-prices.json for the Rock Marker app.
import json, re, html, sys, urllib.request, datetime

BASE = "https://www.dtnpf.com"
UA = {"User-Agent": "Mozilla/5.0 (RockMarker weekly price check)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "ignore")

def find_articles():
    found = []
    for page in ["/agriculture/web/ag/crops", "/agriculture/web/ag/news"]:
        try:
            s = get(BASE + page)
        except Exception:
            continue
        links = re.findall(r'href="(/agriculture/web/ag/crops/article/(\d{4})/(\d{2})/(\d{2})/[^"]*fertilizer[^"]*)"', s)
        for l in links:
            if BASE + l[0] not in [f[1] for f in found]:
                found.append((l[1] + l[2] + l[3], BASE + l[0]))
    found.sort(reverse=True)
    return [f[1] for f in found]

def last_row(block):
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S)
    data = []
    for r in rows:
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(cells) >= 5 and re.match(r"^\$?[\d,]+$", cells[1].replace("$", "")):
            data.append(cells)
    return data[-1] if data else None

def parse(s):
    i = s.find("<table")
    if i < 0:
        return None
    t = s[i:s.find("</table>", i) + 8]
    parts = re.split(r"LIQUID", t, maxsplit=1)
    dry = last_row(parts[0])
    liq = last_row(parts[1]) if len(parts) > 1 else None
    if not dry:
        return None
    n = lambda x: int(x.replace("$", "").replace(",", ""))
    out = {"week": dry[0], "dap": n(dry[1]), "map": n(dry[2]), "potash": n(dry[3]), "urea": n(dry[4])}
    if liq:
        out.update({"p10340": n(liq[1]), "anhydrous": n(liq[2]), "uan28": n(liq[3]), "uan32": n(liq[4])})
    return out

def main():
    p = None
    for url in find_articles()[:6]:
        try:
            p = parse(get(url))
        except Exception:
            p = None
        if p and 200 < p["urea"] < 3000:
            break
        p = None
    if not p:
        print("No DTN price table found; leaving file as is.")
        return 0
    p["source"] = url
    p["checked"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    try:
        old = json.load(open("dtn-prices.json"))
    except Exception:
        old = {}
    same = {k: v for k, v in old.items() if k != "checked"} == {k: v for k, v in p.items() if k != "checked"}
    if same:
        print("No new DTN week:", p["week"])
        return 0
    json.dump(p, open("dtn-prices.json", "w"), indent=1)
    print("Saved", p)
    return 0

if __name__ == "__main__":
    sys.exit(main())
