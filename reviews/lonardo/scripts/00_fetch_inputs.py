"""00_fetch_inputs.py -- Lonardo et al. 2026 (doi:10.1016/j.cognition.2026.106586)

Paper full text: PAYWALLED (Elsevier), no PMC copy. The review therefore covers the
publisher abstract plus the authors' deposited data and code. This script fetches the
deposit only; the abstract is reproduced in paper/ in the review bundle.

Data + code: Zenodo 10.5281/zenodo.20066888 (analysis-ready; v1 is a 2.8 GB raw
eye-tracking archive and is NOT what the authors' .Rmd files read).
Writes into ./data/.
"""
import io, json, os, urllib.request, zipfile

RECORD = "20066888"

def main(outdir="data"):
    os.makedirs(outdir, exist_ok=True)
    with urllib.request.urlopen(
            "https://zenodo.org/api/records/%s" % RECORD, timeout=120) as r:
        rec = json.loads(r.read())
    for f in rec["files"]:
        with urllib.request.urlopen(f["links"]["self"], timeout=600) as r:
            blob = r.read()
        if f["key"].endswith(".zip"):
            zipfile.ZipFile(io.BytesIO(blob)).extractall(outdir)
        else:
            open(os.path.join(outdir, f["key"]), "wb").write(blob)
        print(f["key"], f["size"])

if __name__ == "__main__":
    main()
