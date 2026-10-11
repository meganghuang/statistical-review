---
name: paper-batch-review
description: "Run one reviewer agent per paper across a batch of papers that each have their own deposited data, then publish the results as a reproducible repository. Load when applying a review or audit agent to several papers at once, when assembling paper-plus-data bundles for sub-agents, when retrieving full text and data deposits from PMC, Dryad, Zenodo or publisher supplementary, when exporting an agent's executed cells as numbered reproducibility scripts, when pushing reports and figures to GitHub with artifact markers rewritten to repo paths, or when building a cross-paper verdict summary from per-paper claim tables. Ships pbr_bundle, pbr_rewrite_markers, pbr_verdict_summary and pbr_github_put."
---

# Batch paper review

One sub-agent per paper, each handed a self-contained bundle, each returning a report plus
a machine-readable claim table. The orchestrator never reads the papers — it resolves
inputs, dispatches, audits declared deviations, and publishes.

The pattern generalises beyond statistical review: substitute any per-paper reviewer
(methods audit, reagent validation, reproducibility check). What is specific here is the
plumbing, which is where the time goes.

## Why one agent per paper

PDFs and data exploration dominate context. Five papers in one context produces a shallow
pass on all five; five contexts produce five deep passes. The seam is natural — papers are
independent — and each child returns a small structured result, so the orchestrator stays
clean enough to do the cross-paper synthesis at the end.

Do **not** split a single paper across agents. Claim registration, re-analysis and the
verdict table are one chain of reasoning.

## Workflow

### 1. Resolve inputs before dispatching anything

Resolve every paper and dataset yourself first. A child that spends twenty minutes
discovering its data is behind a paywall is twenty minutes wasted, and it will reach for
a substitute you did not sanction.

| Source | Route | Notes |
|---|---|---|
| Open-access paper | `fetch_article_fulltext(doi)` | returns PMC text or a publisher PDF |
| DOI not in CrossRef | NCBI E-utilities `efetch` on `db=pmc` | microPublication and similar; find the PMCID by search first |
| Springer/Nature supplementary | `static-content.springer.com/esm/art%3A<encoded DOI>/MediaObjects/<file>` | the real route; PMC `/bin/` links hit a JS download interstitial |
| Zenodo | `https://zenodo.org/api/records/<id>` then `files[].links.self` | open, no auth |
| Dryad | **metadata open, files require a bearer token** | see below |
| Elsevier and other paywalls | abstract only | declare it; do not pretend otherwise |

**Dryad.** The v2 API serves metadata and file listings anonymously but answers
`/download` with `401 {"error":"Unauthorized, must have current bearer token"}`. Do not
work around it. Two legitimate routes: check whether the deposit is mirrored on Zenodo
(many Dryad datasets are — search the exact title), or ask the user to download it from
`https://datadryad.org/dataset/doi:<DOI>` in a browser and attach the zip. A mirror is a
**substitution** and must be declared in the output, not silently used.

Record provenance per paper as you go. It becomes the `DATA_SOURCES` / `REPRODUCING`
section and it is the first thing a reader checks.

### 2. Bundle paper + data into one artifact per paper

Sub-agents run in their own working directories, so relative paths and your absolute paths
do not reach them. One zip per paper, with a fixed internal layout:

```
paper/   the text and/or PDF
data/    the authors' deposited data and their own analysis code
```

Ship the authors' analysis code when it exists. A reviewer that can read what the authors
actually ran judges the specification rather than guessing it from the prose.

```python
pbr_bundle("forman", ["papers/forman.pdf"], "data/forman")   # -> bundles/forman_bundle.zip
```

`save_artifacts` each zip, then put the literal `{{artifact:VERSION_ID}}` marker in the
child's `task`. That marker resolves to a readable path inside the child.

### 3. Dispatch, with the crash-safe clause

```python
host.delegate([{ "name": "Forman",
                 "task": TASK_TEMPLATE.format(marker=..., key=...),
                 "context_summary": ...,
                 "output_schema": CLAIMS_SCHEMA,
                 "profile": "YOUR_REVIEWER" } for ...], wait=False)
```

Four things the `task` must carry, learned the hard way:

1. **Which skill to load first**, by name. The rule set is not in the child's head.
2. **Exact output filenames** — `review_<key>.md`, `claims_<key>.csv`,
   `fig_<key>_<topic>.png`. Children invent names otherwise and the publish step becomes
   manual.
3. **A crash-safe clause.** *"Save the report artifact as soon as a first complete draft
   exists, then revise and re-save. Never hold it to the end."* The runtime kills idle
   kernels; a child that writes its report last loses everything. A child that saved
   incrementally can be resumed.
4. **A paper-specific focus paragraph.** You resolved the data, so you know where the
   design is load-bearing — the clustering, the repeated measures, the untested contrast.
   Name it. Generic tasks produce generic reviews.

Set `output_schema` so results come back structured with a `deviations` list. Prose
children bury their caveats.

### 4. Collect, and read the deviations before the findings

`host.collect([frame_id, ...], timeout=...)` in a backgrounded cell; loop short slices.

**Every declared deviation travels with the numbers it qualifies.** A child that
substituted a mirror, subsampled instead of bootstrapping, or failed to fit a model has
produced provisional numbers, and they stay provisional in your summary, your README and
your message to the user. A result whose `deviations` is `["none"]` is the only one you
report unqualified.

If a child dies mid-flight, `host.send_message(frame_id, ...)` **resumes it with full
context even from `status: "failed"`** — point it at its own saved artifacts and tell it
to finish rather than redo. This recovers most of a lost run.

Finding a child's artifacts: `host.artifacts(frame_id=<child id>)` returns **empty**. Use
`host.artifacts(filename="<key>")` and resolve with `host.artifact_path(version_id)`.

### 5. Export the executed cells as numbered scripts

Reproducibility means the code that actually ran, not a tidied retelling. Pull it from the
child's execution log (`repl` tool only — `host.query` is not in the analysis kernels):

```python
rows = host.query("""SELECT cell_index, language, conda_env, exit_status, source
                     FROM execution_log WHERE frame_id=? ORDER BY cell_index""", [fid])["rows"]
```

Keep `exit_status == 'ok'`, concatenate per language in execution order with
`# ---- cell N ----` separators, and write `01_analysis.py` / `02_analysis.R` under
`reviews/<key>/scripts/`. Add a `00_fetch_inputs.py` that reproduces retrieval **from the
public source**, not from your bundle — a reader starts where you started.

State in the header what these are: verbatim cells, error cells omitted, run top-to-bottom
in one process because the originals shared a persistent kernel. Do not rewrite them into
a clean pipeline — that would be code that never produced the results.

For a deposit that cannot be fetched programmatically, `00_fetch_inputs.py` prints the URL,
verifies the expected filenames once unzipped, and exits non-zero until then.

### 6. Publish

GitHub Contents API, one PUT per file, `sha` from a prior GET when updating.

**Rewrite `{{artifact:VERSION_ID}}` markers before pushing.** They are platform-internal
and render as broken text anywhere else. Map version_id to the repo-relative filename,
substitute, and assert zero markers remain:

```python
md2, unresolved = pbr_rewrite_markers(md, {version_id: filename, ...})
assert not unresolved, unresolved
```

Credentials: a read-scoped GitHub token authenticates and lists repositories happily, then
403s every write with `Resource not accessible by personal access token` — the response
header `x-accepted-github-permissions` names what is missing. A fine-grained token created
for "Public repositories" is read-only whatever its Contents setting says. Note also that
the analysis kernels' credential list can lag the control plane after a credential is
added; if a declared credential is "not found" in a `python` cell but appears in
`host.credentials.list()`, run that step from the `repl` tool instead.

### 7. Cross-paper summary, computed not transcribed

Build the summary table from the committed `claims_*.csv` files, never from the children's
prose:

```python
pbr_verdict_summary({"forman": "reviews/forman/claims_forman.csv", ...})
```

Report the calibration alongside the failures — how many claims were Supported outright,
how many defects were cosmetic. A batch review that reports only problems reads as a
prosecution and gets discounted accordingly.

## Helpers

```python
pbr_bundle(key, paper_files, data_dir, outdir="bundles")   # -> zip path, paper/ + data/
pbr_rewrite_markers(md_text, vmap)                         # -> (text, unresolved_ids)
pbr_verdict_summary(csv_paths, verdict_col="verdict")      # -> per-paper counts + totals
pbr_github_put(repo, relpath, data, message, token)        # create-or-update one file
```

## Checklist

1. Every paper and dataset resolved, with provenance recorded, before any dispatch.
2. Every substitution (mirror, abstract-only, analysis-ready in place of raw) declared.
3. One bundle artifact per paper; marker in the task, not a path.
4. Task names the skill, the exact filenames, the crash-safe clause, the specific focus.
5. Deviations read before findings; provisional numbers stay labelled provisional.
6. Scripts exported from the execution log, with a public-source fetch step.
7. Markers rewritten; zero remaining, asserted.
8. Summary computed from the committed tables.
