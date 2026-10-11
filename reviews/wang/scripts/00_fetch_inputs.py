"""00_fetch_inputs.py -- Wang & Horowitz 2026 (doi:10.1038/s41598-026-41426-1)

Paper full text: open access at PMC13046943.

Data: Dryad doi:10.5061/dryad.bzkh189pt (Part_1.xlsx, Part_2.xlsx, README.md,
statistical_analyses.R; ~130 KB).

MANUAL STEP REQUIRED. Dryad's file-download API returns
    401 {"error":"Unauthorized, must have current bearer token"}
for anonymous clients, and this project does not work around that. The dataset is
openly downloadable from the web interface:

    https://datadryad.org/dataset/doi:10.5061/dryad.bzkh189pt  ->  Download dataset

Unzip the result into ./data/ so that ./data/Part_1.xlsx exists, then run 01_analysis.py.
This script only verifies that the expected files are present.
"""
import os, sys

EXPECTED = ["Part_1.xlsx", "Part_2.xlsx", "README.md", "statistical_analyses.R"]

def main(outdir="data"):
    missing = [f for f in EXPECTED if not os.path.exists(os.path.join(outdir, f))]
    if missing:
        sys.exit("Missing from %s/: %s\nSee the manual download step in this file's "
                 "docstring." % (outdir, ", ".join(missing)))
    print("All %d expected files present in %s/." % (len(EXPECTED), outdir))

if __name__ == "__main__":
    main()
