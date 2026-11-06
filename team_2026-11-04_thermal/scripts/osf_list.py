"""List an OSF storage folder (all pages) via the public API; write TSV with name, size, md5, sha256, download url.
usage: python -I osf_list.py <node> <folder_id> <out.tsv>"""
import json, sys, urllib.request
node, folder, out = sys.argv[1:4]
url = f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/{folder}/?page[size]=100"
rows = []
while url:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mtp-datascout"}), timeout=60) as r:
        d = json.load(r)
    for it in d["data"]:
        a = it["attributes"]
        h = (a.get("extra") or {}).get("hashes") or {}
        rows.append((a["name"], a["kind"], a.get("size") or 0, h.get("md5", ""), h.get("sha256", ""), it["links"].get("download", ""), it["id"]))
    url = d["links"].get("next")
with open(out, "w") as f:
    f.write("name\tkind\tsize\tmd5\tsha256\tdownload\tid\n")
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
print(len(rows), "items;", sum(int(r[2]) for r in rows), "bytes")
