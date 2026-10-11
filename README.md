# statistical-review

A rule set for evaluating statistical claims, the reviewer agent that applies it, and five
worked reviews of published papers against their own deposited data.

Built as coursework for *Lecture 3: Using the language of probability to make confidence
statements*. The rules are the lecture's, organised into something an agent can execute.

## The idea

A statistical claim is a **chain**:

> population -> sample -> experimental unit -> design -> model -> statistic ->
> reference distribution -> p / interval -> the sentence in the abstract

A claim is only as strong as its weakest link, and **the broken link is almost always
upstream of the test**. The review walks the chain in order and stops at the first failure,
because everything downstream inherits it. Reviewing "was the t-test right" first is the
standard way to miss that *n* counted cells instead of animals.

## Layout

| Path | What it is |
|---|---|
| `skill/statistical-review/SKILL.md` | The rule set: 11 sections, numbered rules, verdict rubric, self-review checklist |
| `skill/statistical-review/kernel.py` | Helper functions auto-loaded with the skill |
| `skill/paper-batch-review/` | The orchestration pattern that produced this repo: bundle, dispatch, collect, export scripts, publish |
| `agent/STAT_REVIEWER.md` | The reviewer agent profile and its input/output contract |
| `reviews/<paper>/` | One worked review per test case: report, machine-readable verdict table, figures |
| `DATA_SOURCES.md` | Exact provenance of every paper and dataset, including what could not be obtained |

## The rule set

| Section | Covers |
|---|---|
| 0 | Claim register — review rows, not paragraphs |
| 1 | Population, representativeness, confounding |
| 2 | Replication, experimental unit, pseudoreplication, SD vs SEM |
| 3 | Design -> test: one/two/paired, one/two-tailed, equal/unequal variance |
| 4 | Q-Q plots and what must be normal for which design |
| 5 | Parametric / nonparametric / permutation / bootstrap and their assumptions |
| 6 | What a p-value is allowed to mean |
| 7 | Multiplicity, Bonferroni vs FDR, and a nine-flag p-hacking screen |
| 8 | **Calibration: what is NOT a violation** |
| 9 | Re-analysis protocol when raw data are available |
| 10-11 | Verdict/severity rubric and report format |

Section 8 exists on purpose. A reviewer that flags everything is useless, so the skill lists
the things that look like violations and are not: unequal group sizes, non-normal raw values
when the claim is about means and Welch was used, no correction across pre-specified
independent primaries, descriptive reporting with no p-values at all.

### Verdicts

`Supported` · `Supported, overstated` · `Mis-specified` · `Not assessable` · `Contradicted`

with severity **A** (the claim does not survive), **B** (the claim survives, its reported
strength does not), **C** (reporting defect, conclusion unaffected).

Every finding is written as *what was done -> what it assumes -> why that fails here ->
what should be done -> what changes*. A finding without the last clause is an opinion.

## Helpers

```python
stat_two_group(a, b, paired=False)   # every candidate test side by side, with the
                                     # assumption each one buys, plus effect size and CI
stat_qq_panel(groups, paired=False)  # per-group panels, or the paired differences
stat_permutation_p(a, b, ...)        # p = (k+1)/(N+1), with its resolution stated
stat_multiplicity(pvals)             # BH q-values and Bonferroni side by side
stat_min_attainable_p(n1, n2, kind)  # the smallest p the design could ever produce
stat_pcurve(pvals)                   # right-skew vs a pile-up under alpha
```

`stat_min_attainable_p` implements the stop rule: if the smallest p a design can produce
exceeds alpha, the claim is **Not assessable** however the data fall. It reproduces the
lecture's worked numbers exactly — 0.0625 for five nonzero pairs, 0.03125 for six, 0.100 for
an exact 3-vs-3 permutation, 0.0286 for 4-vs-4.

## Test cases

Five papers on cats and dogs, each with a public data deposit.

| Key | Paper | Data |
|---|---|---|
| `wang` | Wang & Horowitz 2026, *Sci Rep* — dogs distinguish conspecific emotional chemosignals | Dryad `10.5061/dryad.bzkh189pt` |
| `goold` | Goold et al. 2016, *R Soc Open Sci* — network analysis of behavioural phenotypes in police dogs | Dryad `10.5061/dryad.81k11` |
| `forman` | Forman et al. 2023, *Sci Rep* — survey of cat fetching behaviour | Publisher supplementary |
| `lonardo` | Lonardo et al. 2026, *Cognition* — pupil size and the social conventions behind human gestures | Zenodo `10.5281/zenodo.20066888` |
| `alavinaini` | Alavi Naini et al. 2026, *microPublication Biology* — diel activity of bobcats and domestic cats | Dryad `10.5061/dryad.s4mw6m9jg` |

See `DATA_SOURCES.md` for exactly what was retrieved for each, and what was not.

## Results

106 claims adjudicated across the five papers. Counts are computed from the committed
`claims_*.csv` files, not transcribed from the reports.

| Paper | Claims | Supported | Overstated | Mis-specified | Not assessable | Contradicted | A | B | C |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| [forman](reviews/forman/review_forman.md) | 35 | 26 | 6 | 2 | 1 | 0 | 1 | 5 | 10 |
| [wang](reviews/wang/review_wang.md) | 26 | 7 | 8 | 1 | 0 | 10 | 11 | 7 | 7 |
| [goold](reviews/goold/review_goold.md) | 21 | 6 | 6 | 6 | 1 | 2 | 6 | 4 | 5 |
| [lonardo](reviews/lonardo/review_lonardo.md) | 12 | 6 | 3 | 0 | 2 | 1 | 1 | 3 | 5 |
| [alavinaini](reviews/alavinaini/review_alavinaini.md) | 12 | 2 | 5 | 1 | 3 | 1 | 1 | 6 | 3 |
| **total** | **106** | **47** | **28** | **10** | **7** | **14** | **20** | **25** | **30** |

Severity: **A** the claim does not survive · **B** the claim survives, its reported
strength does not · **C** reporting defect, conclusion unaffected.

### What the chain caught

The rule set is ordered so that upstream links are checked first, and that is where the
consequential findings landed. Not one severity-A finding in this set came from choosing
the wrong test formula.

**The experimental unit, three times.** In `wang`, Part 2 was analysed on 12 time-bin
averages rather than 24 dogs; re-run at the dog level, **5 of the 6 significant results
disappear**. In `forman`, 1,154 cats were treated as independent when 924 owners reported
them, and the male-biased sex ratio stops clearing alpha once the design effect exceeds
1.44 — inside the 1.40–1.79 band that clustering implies. In `alavinaini`, camera-trap
detections are not independent animals; the paper's only significant test loses
significance under a 30-minute independence filter with a site-stratified null.

**The comparison that was never made.** `goold` contrasts the patrol and detection
networks but never tests the difference. Running the between-network permutation test the
paper lacks gives **p = 0.666**. Its figure 3 intervals turn out to be Monte-Carlo error
scaling as 1.60/sqrt(n_boot) — a property of the bootstrap iteration count, not of the data.

**Exclusion-dependent effects.** In `lonardo`, the headline pupil-dilation effect is
confined to the 28-of-39-dog completeness subset.

**Effect sizes.** `forman` reports no effect size or interval for any of its 21
significant results, though the authors' own script ran two tests with `conf.int=TRUE`.
Recomputed, those 14 rank comparisons span probability of superiority 0.284 to 0.653 —
all printed in the paper as "p < 0.001" or similar.

### Calibration

47 of 106 claims are Supported outright and 30 of the defects are severity C — reporting
gaps that leave the conclusion standing. `forman` in particular is largely sound: every
one of its 29 reported statistics reproduced from the deposited data, and 19 of its 35
claims carry no defect at all. A rule set that failed everything would be useless, which
is what section 8 of the skill exists to prevent.

The 7 Not-assessable verdicts are honest stops, not evasions: a design whose minimum
attainable p exceeds alpha, a model that would not converge, a bootstrap whose inputs were
never deposited. Each is named in its report's limitations section.

## Using it

The skill is a Claude Science skill; drop `skill/statistical-review/` into a skills directory
and load it with `skill({"skill": "statistical-review"})`. `kernel.py` loads automatically and
defines the helpers above. The agent profile in `agent/` is reproducible from its JSON via
`host.agents.create(...)`.
