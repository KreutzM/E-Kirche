#!/usr/bin/env python3
"""Fetch the curated free reference set from Wikimedia Commons.

Standard library only. Licence metadata is checked live at download time.
"""
from pathlib import Path
import argparse, html, json, re, time, urllib.parse, urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.json"
META = ROOT / "sources" / "commons_download_metadata.jsonl"
REPORT = ROOT / "sources" / "download_report.csv"
API = "https://commons.wikimedia.org/w/api.php"
UA = "E-Kirche-reconstruction/1.0 (research)"
ALLOWED = ("cc by", "cc-by", "cc by-sa", "cc-by-sa", "cc0", "public domain", "pdm", "gfdl")

def clean(value):
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()

def info(title, width):
    params = {
        "action":"query","format":"json","formatversion":"2",
        "prop":"imageinfo","titles":"File:"+title,
        "iiprop":"url|size|mime|sha1|extmetadata|commonmetadata",
    }
    if width:
        params["iiurlwidth"] = str(width)
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    page = data["query"]["pages"][0]
    if page.get("missing"):
        raise RuntimeError("Commons file not found")
    ii = page["imageinfo"][0]
    ext = ii.get("extmetadata", {})
    def em(k):
        v = ext.get(k, {})
        return clean(v.get("value","")) if isinstance(v, dict) else ""
    return {
        "original_url": ii.get("url",""),
        "thumb_url": ii.get("thumburl",""),
        "width": ii.get("width"),
        "height": ii.get("height"),
        "mime": ii.get("mime"),
        "sha1": ii.get("sha1"),
        "license_short_name": em("LicenseShortName"),
        "license_url": em("LicenseUrl"),
        "artist": em("Artist"),
        "credit": em("Credit"),
        "source": em("Source"),
        "date_time_original": em("DateTimeOriginal"),
        "commonmetadata": ii.get("commonmetadata", {}),
    }

def allowed(name):
    return any(x in (name or "").lower() for x in ALLOWED)

def destination(rec):
    if rec["group"] == "modern":
        base = ROOT / "references" / "images" / "modern"
    elif rec["group"] == "historic_pd":
        base = ROOT / "references" / "images" / "historic"
    else:
        base = ROOT / "references" / "plans" / "downloaded"
    return base / f'{rec["id"]}_{Path(rec["title"]).name}'

def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=120) as r, tmp.open("wb") as f:
        while True:
            chunk = r.read(1024*1024)
            if not chunk:
                break
            f.write(chunk)
    tmp.replace(dest)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priority", type=int, choices=(1,2,3))
    ap.add_argument("--max-width", type=int, default=2500)
    ap.add_argument("--originals", action="store_true")
    args = ap.parse_args()

    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.priority:
        rows = [r for r in rows if int(r["priority"]) <= args.priority]

    META.write_text("", encoding="utf-8")
    report = ["id,status,license,file,error"]
    ok = 0
    for i, rec in enumerate(rows, 1):
        print(f'[{i}/{len(rows)}] {rec["id"]} {rec["title"]}')
        try:
            meta = info(rec["title"], None if args.originals else args.max_width)
            if not allowed(meta["license_short_name"]):
                raise RuntimeError(f'licence not accepted: {meta["license_short_name"]!r}')
            url = meta["original_url"] if args.originals else (meta["thumb_url"] or meta["original_url"])
            dest = destination(rec)
            download(url, dest)
            meta.update({"dataset_id":rec["id"],"title":rec["title"],"commons_page":rec["commons_page"],
                         "downloaded_to":str(dest.relative_to(ROOT))})
            with META.open("a", encoding="utf-8") as f:
                f.write(json.dumps(meta, ensure_ascii=False)+"\n")
            report.append(f'{rec["id"]},downloaded,"{meta["license_short_name"]}","{dest.relative_to(ROOT)}",')
            ok += 1
        except Exception as exc:
            msg = str(exc).replace('"','""')
            report.append(f'{rec["id"]},ERROR,,,"{msg}"')
            print("  ERROR:", exc)
        time.sleep(0.2)
    REPORT.write_text("\n".join(report)+"\n", encoding="utf-8")
    print(f"Downloaded {ok}/{len(rows)} assets.")

if __name__ == "__main__":
    main()
