"""00_fetch_inputs.py -- Goold et al. 2016 (doi:10.1098/rsos.160268)

Paper full text: open access at PMC5098969 / royalsocietypublishing.org.
Data: deposited at Dryad doi:10.5061/dryad.81k11. Dryad's file-download API now
requires an authenticated bearer token, so this script uses the complete Zenodo
mirror of the same deposit (record 4967251) -- identical six files, verified by name
and size. SUBSTITUTION IS DELIBERATE AND IS DECLARED IN THE REVIEW.
Writes into ./data/.
"""
import json, os, urllib.request

RECORD = "4967251"

def main(outdir="data"):
    os.makedirs(outdir, exist_ok=True)
    with urllib.request.urlopen(
            "https://zenodo.org/api/records/%s" % RECORD, timeout=120) as r:
        rec = json.loads(r.read())
    for f in rec["files"]:
        with urllib.request.urlopen(f["links"]["self"], timeout=600) as r:
            open(os.path.join(outdir, f["key"]), "wb").write(r.read())
        print(f["key"], f["size"])

if __name__ == "__main__":
    main()
