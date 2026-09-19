#!/usr/bin/env python3
"""Fetch the curated free reference set from Wikimedia Commons.

Standard library only. Licence metadata is checked live at download time.
"""
from pathlib import Path
import argparse, csv, hashlib, html, json, re, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.json"
META = ROOT / "sources" / "commons_download_metadata.jsonl"
REPORT = ROOT / "sources" / "download_report.csv"
API = "https://commons.wikimedia.org/w/api.php"
UA = "E-Kirche-reconstruction/1.0 (https://github.com/KreutzM/E-Kirche; research)"

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
    return bool(re.fullmatch(
        r"(?:cc[ -]by(?:[ -]sa)?(?: \d\.\d)?|cc0(?: 1\.0)?|public domain|pdm|gfdl(?: \d\.\d)?)",
        (name or "").strip().lower()))

def destination(rec):
    if rec["group"] == "modern":
        base = ROOT / "references" / "images" / "modern"
    elif rec["group"] == "historic_pd":
        base = ROOT / "references" / "images" / "historic"
    else:
        base = ROOT / "references" / "plans" / "downloaded"
    return base / f'{rec["id"]}_{Path(rec["title"]).name}'

def download(url, dest):
    if dest.exists():
        raise FileExistsError(f"Refusing to overwrite reference: {dest}")
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
    ap.add_argument("--delay", type=float, default=2.0, help="Seconds between assets (default: 2)")
    args = ap.parse_args()
    if args.max_width <= 0 or args.delay < 0:
        ap.error("max-width must be positive and delay non-negative")

    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.priority:
        rows = [r for r in rows if int(r["priority"]) <= args.priority]

    META.parent.mkdir(parents=True, exist_ok=True)
    previous = {}
    if META.exists():
        for line in META.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            previous[record["dataset_id"]] = record
    report = []
    ok = 0
    for i, rec in enumerate(rows, 1):
        print(f'[{i}/{len(rows)}] {rec["id"]} {rec["title"]}')
        try:
            dest = destination(rec)
            if dest.exists():
                old = previous.get(rec["id"], {})
                digest = hashlib.sha256(dest.read_bytes()).hexdigest()
                if old.get("download_sha256") != digest:
                    raise RuntimeError("Existing reference lacks matching provenance/hash; inspect manually")
                if old.get("requested_width") != (None if args.originals else args.max_width):
                    raise RuntimeError("Existing reference uses a different resolution; preserve it and resolve manually")
                report.append([rec["id"], "cached", old["license_short_name"], str(dest.relative_to(ROOT)), ""])
                ok += 1
                continue
            meta = info(rec["title"], None if args.originals else args.max_width)
            if not allowed(meta["license_short_name"]):
                raise RuntimeError(f'licence not accepted: {meta["license_short_name"]!r}')
            url = meta["original_url"] if args.originals else (meta["thumb_url"] or meta["original_url"])
            download(url, dest)
            meta.update({"dataset_id":rec["id"],"title":rec["title"],"commons_page":rec["commons_page"],
                         "downloaded_to":str(dest.relative_to(ROOT)),
                         "download_url":url,
                         "retrieved_at":datetime.now(timezone.utc).isoformat(),
                         "requested_width":None if args.originals else args.max_width,
                         "download_sha256":hashlib.sha256(dest.read_bytes()).hexdigest()})
            with META.open("a", encoding="utf-8") as f:
                f.write(json.dumps(meta, ensure_ascii=False)+"\n")
            report.append([rec["id"], "downloaded", meta["license_short_name"], str(dest.relative_to(ROOT)), ""])
            ok += 1
        except Exception as exc:
            report.append([rec["id"], "ERROR", "", "", str(exc)])
            print("  ERROR:", exc)
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                print("Rate limited; stopping. Respect Retry-After:", exc.headers.get("Retry-After", "not supplied"))
                print("Re-run later; verified cached references will be preserved.")
                report.extend([r["id"], "DEFERRED", "", "", "Rate limited earlier in run"] for r in rows[i:])
                break
        time.sleep(args.delay)
    new_report = not REPORT.exists() or REPORT.stat().st_size == 0
    with REPORT.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        if new_report:
            writer.writerow(["id", "status", "license", "file", "error"])
        writer.writerows(report)
    print(f"Available {ok}/{len(rows)} assets.")
    return 0 if ok == len(rows) else 1

if __name__ == "__main__":
    raise SystemExit(main())
