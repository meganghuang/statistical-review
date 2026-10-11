"""00_fetch_inputs.py -- Alavi Naini et al. 2026 (doi:10.17912/micropub.biology.001911)

Paper full text: open access at PMC13310411 (the DOI is not registered in CrossRef;
fetch via NCBI E-utilities efetch on db=pmc, id=13310411).

Data: Dryad doi:10.5061/dryad.s4mw6m9jg (Bobcat_Data.csv, Domestic_Cat_Data.csv,
"Dhat R Script MicroPub.R", "Watsons U2 and Polar Plot.m", two overlap figures).

MANUAL STEP REQUIRED. Dryad's file-download API requires a bearer token for anonymous
clients and this project does not work around that. Download from the web interface:

    https://datadryad.org/dataset/doi:10.5061/dryad.s4mw6m9jg  ->  Download dataset

Unzip into ./data/ (discard the __MACOSX/ directory), then run 01_analysis.py.
This script fetches the paper text and verifies the data files are present.
"""
import os, sys, urllib.request

EXPECTED = ["Bobcat_Data.csv", "Domestic_Cat_Data.csv"]
EFETCH = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
          "?db=pmc&id=13310411&retmode=xml")

def main(outdir="data", paperdir="paper"):
    os.makedirs(paperdir, exist_ok=True)
    with urllib.request.urlopen(EFETCH, timeout=120) as r:
        open(os.path.join(paperdir, "alavinaini_pmc.xml"), "wb").write(r.read())
    print("paper XML fetched")
    missing = [f for f in EXPECTED if not os.path.exists(os.path.join(outdir, f))]
    if missing:
        sys.exit("Missing from %s/: %s\nSee the manual download step in this file's "
                 "docstring." % (outdir, ", ".join(missing)))
    print("All expected data files present in %s/." % outdir)

if __name__ == "__main__":
    main()
