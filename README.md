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

## Using it

The skill is a Claude Science skill; drop `skill/statistical-review/` into a skills directory
and load it with `skill({"skill": "statistical-review"})`. `kernel.py` loads automatically and
defines the helpers above. The agent profile in `agent/` is reproducible from its JSON via
`host.agents.create(...)`.
