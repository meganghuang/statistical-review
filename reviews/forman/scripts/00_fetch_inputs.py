"""00_fetch_inputs.py -- Forman et al. 2023 (doi:10.1038/s41598-023-47409-w)

Paper full text: open access at PMC10721921 / nature.com.
Data: the paper states all data are in its Supplementary Information. The per-cat
dataset is MOESM3 (1154 rows x 75 cols). Fetched from the publisher's ESM host.
Writes into ./data/.
"""
import os, urllib.request

BASE = ("https://static-content.springer.com/esm/"
        "art%3A10.1038%2Fs41598-023-47409-w/MediaObjects/")
FILES = ["41598_2023_47409_MOESM%d_ESM.%s" % (i, e) for i, e in
         [(1, "docx"), (2, "docx"), (3, "csv"), (4, "pdf"), (5, "docx"),
          (6, "xlsx"), (7, "docx")]]

def main(outdir="data"):
    os.makedirs(outdir, exist_ok=True)
    for f in FILES:
        dest = os.path.join(outdir, f)
        with urllib.request.urlopen(BASE + f, timeout=120) as r:
            open(dest, "wb").write(r.read())
        print(f, os.path.getsize(dest))

if __name__ == "__main__":
    main()
