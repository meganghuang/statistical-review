# Reproducing these reviews

Everything here was produced by the `STAT_REVIEWER` agent applying the
`statistical-review` skill to five published papers and their deposited data.

## What the scripts are, and what they are not

`reviews/<paper>/scripts/01_analysis.py` (and `02_analysis.R` where the reviewer used R)
are the **verbatim code cells the reviewer actually executed**, concatenated in execution
order with `# ---- cell N ----` separators. Cells that errored are omitted; everything
else is unedited.

They are deliberately *not* a tidied-up pipeline. A rewritten, prettier version would be
code that never produced the published numbers, and the point of the exercise is that you
can check the numbers. Expect exploration, false starts that were later superseded, and
occasional redundancy — that is what the analysis looked like.

Two consequences for running them:

- **Run each file top-to-bottom in ONE process.** The originals ran in a persistent
  kernel, so later cells depend on names bound by earlier ones.
- **Paths are relative to a working directory containing `data/` and `paper/`**, laid out
  as `00_fetch_inputs.py` leaves them.

## Run order

```bash
cd reviews/<paper>
python scripts/00_fetch_inputs.py     # fetch the deposit into ./data
python scripts/01_analysis.py         # the review analysis
Rscript scripts/02_analysis.R         # only where present
```

## Data access

Three deposits are fetched automatically. Two are not, and cannot be:

| Paper | Source | Automatic? |
|---|---|---|
| `forman` | Publisher supplementary (Springer ESM) | yes |
| `lonardo` | Zenodo `10.5281/zenodo.20066888` | yes |
| `goold` | Zenodo `4967251`, the complete mirror of Dryad `10.5061/dryad.81k11` | yes |
| `wang` | Dryad `10.5061/dryad.bzkh189pt` | **no — manual** |
| `alavinaini` | Dryad `10.5061/dryad.s4mw6m9jg` | **no — manual** |

Dryad's file-download API now answers anonymous clients with
`401 {"error":"Unauthorized, must have current bearer token"}`. The datasets are openly
downloadable from the Dryad web interface, so the two `00_fetch_inputs.py` scripts print
the URL, verify the expected files once you have unzipped them into `./data/`, and exit
non-zero until then. Nothing here attempts to bypass that authentication.

The `goold` substitution — Zenodo mirror in place of the Dryad original — is deliberate,
was made for the same reason, and is declared in that paper's review as well as here. The
mirror carries the identical six files.

## Environments

| Environment | Contents |
|---|---|
| `python` | numpy, pandas, scipy, matplotlib, seaborn (+ `openpyxl` for `.xlsx`, `pyarrow` for `.parquet`) |
| `r` | tidyverse, plus per-paper packages the authors' own code requires (`mgcv`, `glmmTMB`, `lme4`, `overlap`, `circular`) |

Each script's header comment records the conda environment it ran in.

## Known non-reproducible step

The Lonardo review's claim C3 depends on the authors' pupil-size GAMM
(`mgcv::bam`, 4,592 rows, 112 trial-level and 28 dog-level factor smooths). It **did not
converge** — 95 minutes on the authors' exact ML call and 29 minutes on an fREML variant,
across two R environments. The claim is recorded `Not assessable` and no substitute model
was fitted in its place. Re-running that cell will reproduce the non-convergence, not a
result.
