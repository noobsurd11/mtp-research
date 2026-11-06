"""Download selected files from an OSF listing TSV (from osf_list.py) into dest_dir; verify size, md5, sha256
against the OSF-published values; append results to dest_dir/../<set>_verify.tsv.
usage: python -I osf_fetch.py <listing.tsv> <dest_dir> <verify_out.tsv> [names_file]
names_file: one file name per line; if omitted, all files in the listing are fetched.
Never executes downloaded content."""
import csv, hashlib, os, sys, time, urllib.request
lst, dest, vout = sys.argv[1:4]
names = None
if len(sys.argv) > 4:
    names = [l.rstrip("\n") for l in open(sys.argv[4]) if l.strip()]
rows = {r["name"]: r for r in csv.DictReader(open(lst), delimiter="\t") if r["kind"] == "file"}
todo = names if names is not None else sorted(rows)
missing = [n for n in todo if n not in rows]
if missing:
    sys.exit(f"names not in listing: {missing[:5]}")
os.makedirs(dest, exist_ok=True)
new = not os.path.exists(vout)
vf = open(vout, "a")
if new:
    vf.write("name\tbytes_listed\tbytes_got\tmd5_pub\tmd5_got\tsha256_pub\tsha256_got\tstatus\n")
bad = 0
for n in todo:
    r = rows[n]
    p = os.path.join(dest, n)
    if os.path.exists(p):
        sys.exit(f"refuse to overwrite {p}")
    for attempt in range(3):
        try:
            req = urllib.request.Request(r["download"], headers={"User-Agent": "mtp-datascout"})
            with urllib.request.urlopen(req, timeout=120) as resp, open(p + ".part", "wb") as f:
                while True:
                    b = resp.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            break
        except Exception as e:
            print("retry", n, e, file=sys.stderr); time.sleep(5)
    else:
        sys.exit(f"failed {n}")
    os.rename(p + ".part", p)
    md5, sha = hashlib.md5(), hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            md5.update(b); sha.update(b)
    got = os.path.getsize(p)
    ok_size = str(got) == r["size"]
    ok_md5 = (r["md5"] == "" or r["md5"] == md5.hexdigest())
    ok_sha = (r["sha256"] == "" or r["sha256"] == sha.hexdigest())
    status = "OK" if (ok_size and ok_md5 and ok_sha) else "MISMATCH"
    if not (r["md5"] or r["sha256"]):
        status += "_nohash"
    bad += status.startswith("MISMATCH")
    vf.write("\t".join([n, r["size"], str(got), r["md5"], md5.hexdigest(), r["sha256"], sha.hexdigest(), status]) + "\n")
    vf.flush()
print(len(todo), "files fetched;", bad, "mismatches")
