---
name: statistical-review
description: "Evaluate the statistical claims in a paper, figure, thesis or analysis, and decide whether each one survives its own data. Load when reviewing or refereeing statistical evidence, when asked whether a test was the right test, when checking a p-value, confidence interval, FDR correction or error bar, when judging paired vs unpaired, one- vs two-tailed, equal- vs unequal-variance, parametric vs nonparametric vs permutation, when assessing replication, pseudoreplication, n and the experimental unit, when screening for p-hacking, multiple-testing abuse or selective reporting, and when re-analysing raw data to confirm a published number. Ships stat_two_group, stat_qq_panel, stat_permutation_p, stat_multiplicity, stat_min_attainable_p and stat_pcurve."
---

# Statistical review

A statistical claim is a **chain**:

> population -> sample -> experimental unit -> design -> model -> statistic ->
> reference distribution -> p / interval -> the sentence in the abstract

The claim is only as strong as its weakest link, and **the broken link is
almost always upstream of the test**. Reviewing the test alone is the most
common way to miss the real problem. Walk the chain in order; stop at the
first link that fails and say so, because everything downstream inherits it.

Two standing principles:

- **The scientific question determines the summary statistic, which
  determines the test.** Not the other way round. A population where 9 of 10
  subjects improve by +1 and one worsens by -20 has a *positive* direction of
  change and a *negative* mean change. Both are correct answers to different
  questions. Decide which question was asked before judging which number is
  right.
- **Everything is a random variable.** The sample is random, so every summary
  computed from it has a sampling distribution. A confidence statement is a
  statement about that distribution — either shown (interval, bootstrap
  distribution, error bar) or tested (p-value). A number reported without
  either is not yet a claim.

---

## 0. Build the claim register first

Do not review prose linearly. Extract every statistical claim into a table —
one row per claim — and review rows, not paragraphs. A claim is any sentence
asserting a difference, association, trend, enrichment or absence thereof.

| Field | What to record |
|---|---|
| id | C1, C2, ... |
| claim | The sentence as written, verbatim |
| location | Figure/table/line |
| direction | What is asserted to be bigger/related/absent |
| n reported | As stated by the authors |
| experimental unit | What *you* judge the independent unit to be |
| design | one-sample / two-sample independent / paired / >2 groups / regression |
| test used | As stated; "not stated" is a finding |
| statistic + p | As reported |
| effect size + interval | As reported; "absent" is a finding |
| multiplicity | How many tests sit behind this claim |
| data available | Which file supports re-analysis |

Claims with no test, no n, or no named method are **Not assessable** — that is
a verdict, not a gap in the review.

---

## 1. Population and sampling

The first question is never "which test". It is **what population is this a
statement about, and is the sample representative of it?** This assumption
carries everything downstream and no amount of computation repairs it.

Check:

1. **Is the target population stated?** "All vivarium-grown mice of this
   genetic background" is a population. "Mice" is not.
2. **Could the sample have been drawn from somewhere narrower?** One cage, one
   clinic, one season, one sequencing run, volunteers who answered a survey.
   State the narrower population the data actually supports and whether the
   claim was written for the wider one.
3. **Confounding.** Known confounders can be designed or modelled away;
   unknown ones cannot. Ask whether treatment is entangled with batch, date,
   operator, plate position, litter, housing or scanner. **Randomisation and
   blinding are the only general protection** — if neither is reported, the
   confounding caveat applies to every claim in the paper and belongs in the
   summary, not in a footnote on one figure.
4. **Survey and observational data**: recruitment channel *is* the sampling
   frame. Self-selected respondents support claims about respondents.

A Q-Q plot, a bootstrap or a permutation test cannot detect any failure in
this section. Say so explicitly when the design is observational.

---

## 2. Replication and the experimental unit

**Why repeat experiments**: averages of independent observations concentrate
(central limit theorem), so the uncertainty in a mean shrinks as
`SE = SD / sqrt(n)`. This only works if the *n* observations are independent
replicates of the thing the claim is about.

| Term | Measures | Shrinks with n? |
|---|---|---|
| SD | spread of individual observations | no |
| SE / SEM | uncertainty of the estimated summary | yes, as 1/sqrt(n) |

Rules:

- **R2.1 — Identify the independent unit, then recount n.** If the claim is
  about mice, n is mice; cells, images, reads, wells, time points or technical
  replicates from the same animal are **pseudoreplication**. Inflated n is the
  single most consequential error in figure statistics and it always moves the
  p-value in the author's favour. Report both the stated n and the defensible n.
- **R2.2 — Technical replicates measure the assay, biological replicates
  measure the biology.** Averaging technical replicates to one value per unit
  is correct; treating them as independent is not.
- **R2.3 — Error bars must be identified.** SD, SEM and CI are three different
  claims. An unlabelled error bar is a reporting defect; an SEM bar presented
  as if it showed data spread is a misleading one.
- **R2.4 — Show the distribution of the summary statistic you are making a
  claim about.** If the claim is about a mean, the reader needs the sampling
  distribution of the mean (interval, bootstrap, SEM), not only a boxplot of
  raw values — and vice versa.
- **R2.5 — Replicated at all?** A single experiment with internal replicates
  is one experiment. Independent repetition on a separate cohort/day/batch is
  the only thing that addresses batch-level confounding.
- **R2.6 — n per group must be reported per group**, not pooled, and must
  match the number of points plotted.

---

## 3. Design determines the test

Three orthogonal choices. Get them from the **design**, never from the data.

### 3a. One-sample / two-sample / paired

| Design | Correct family | Classic error |
|---|---|---|
| One group vs a fixed reference value | one-sample | treating the reference as a sampled group |
| Two independent groups | two-sample | — |
| Same unit measured twice; matched littermates; before/after | **paired** | analysing as independent, which discards the pairing and usually loses power |
| Independent groups analysed as paired | — | invalid: pairs are manufactured by sort order |

**R3.1** A paired design analysed unpaired is a real error even when it is
conservative; a non-paired design analysed as paired is a fatal one.

### 3b. One- or two-tailed

**R3.2** A one-tailed test is legitimate only if the direction was committed to
**before** seeing the data, and a result in the opposite direction is then
reported as a null. A one-tailed test that appears only after a two-tailed
p of 0.08 doubles the false-positive rate. Flag any one-tailed test without
pre-specification; a one-tailed p near 0.05 silently corresponds to a
two-tailed p near 0.1.

### 3c. Equal or unequal variance

**R3.3** Default to **Welch's unequal-variance t-test** for independent groups.
The pooled t-test buys a stronger assumption (common sigma) for almost no
power when it holds, and is anti-conservative when variances and group sizes
differ in opposite directions. Report the variance ratio.

**R3.4** Do not use a preliminary variance test (Levene, F) to *choose*
between pooled and Welch. Conditioning the test on the data distorts the
error rate — it is a researcher degree of freedom with a respectable name.

**R3.5** When group variances genuinely differ, "the groups differ" may be a
claim about *spread*, not location. Check whether the stated conclusion
matches the quantity the test addressed.

---

## 4. Distributional assumptions and Q-Q plots

**R4.1 — Inspect the right quantity.**

| Design | What must be approximately normal | Plot |
|---|---|---|
| Independent groups | each group's own values | one Q-Q panel per group |
| Paired | the **within-pair differences** | one Q-Q panel of the differences |
| Regression / ANOVA | the residuals | Q-Q of residuals |

Pooling groups with different means produces a mixture that looks non-normal
even when every group is perfectly normal. Inspecting the pooled vector is a
standard mistake.

**R4.2 — Read shape, not pass/fail.** A Q-Q plot distinguishes approximately
normal (points on the line), right-skew (upward curve) and heavy tails
(S-shape, both ends off the line). Even genuinely normal samples do not sit
exactly on the line at n = 60.

**R4.3 — Do not use a normality test as an automatic test-selector.** At small
n it has no power to reject anything; at large n it rejects trivial departures
that the t-test tolerates. Mechanical "Shapiro then choose" pipelines are a
forking path. Judge from the Q-Q plot plus the sample size plus what the
statistic needs.

**R4.4 — "n >= 30 so it's fine" is a heuristic, not a theorem.** The
large-sample argument needs finite variance and *iid* sampling, and there is
no universal cutoff; skewness and outliers both raise the required n. Three
versus four observations never qualifies.

**R4.5 — A straight Q-Q plot establishes nothing about independence,
randomisation or confounding.** Those come from the design (section 1), and no
diagnostic plot substitutes.

Use `stat_qq_panel(groups, paired=...)`.

---

## 5. The three ways to make a probabilistic statement

### 5a. Parametric

A parametric model specifies a distribution family with finitely many
parameters: `measurement = group mean + random variation`, with the null
constraining the means (H0: muA = muB). Parametric does **not** mean Gaussian.

The t-statistic is the effect divided by its own uncertainty:
`t = (difference in means) / SE`. Three ways to make t large: bigger
difference, less variation, more observations. The t reference distribution
has heavier tails than the normal because the variance is itself estimated;
it approaches normal as n grows.

**Assumptions**: independent observations; the stated family within group;
common variance *only* for the pooled version.

### 5b. Nonparametric

Convert the data into something whose null distribution is known by
combinatorics — usually signs or ranks. "Nonparametric" means no
finite-dimensional family. It does **not** mean assumption-free.

| Test | Null it actually tests | Assumption people forget |
|---|---|---|
| Sign test (paired) | P(D > 0) = P(D < 0), i.e. median paired difference 0 | independent pairs; zeros dropped reduce effective n |
| Wilcoxon signed-rank (paired) | — | **differences symmetric about zero.** A zero median is sufficient for the sign test but *not* for signed-rank: if all large magnitudes carry one sign, the sign-flip null is unjustified even with median zero |
| Mann-Whitney / rank-sum | the two distributions are **identical** | it is **not** a test of equal medians, and the common distribution needs no particular shape |

**R5.1 — Mann-Whitney significance does not license a median claim.** Two
groups can have identical medians and still be strongly ordered. Translating
U into a median shift requires the extra assumption of a pure location shift
with shared shape. Report `U / (n1*n2)` as the probability of superiority
instead — it is what the test estimates.

**R5.2 — Never compare raw rank sums across unequal group sizes.** Their null
expectations differ (`E[R_g] = n_g (N+1) / 2`). Use U, which is calibrated for
the sizes.

**R5.3 — Cross-group comparisons are dependent.** The n1*n2 comparisons reuse
observations; they are not independent Bernoulli trials and must not be fed to
a binomial test.

**R5.4 — Ranks discard magnitude.** Changing the largest observation from 100
to 10,000 leaves the ranks, the rank sum and the exact p-value untouched while
the mean difference moves by two orders of magnitude. That is robustness to
outlier *influence*, and simultaneously a refusal to report effect size in
original units. A rank test must be accompanied by an effect estimate.

**R5.5 — Nonparametric is not free.** Under normality the rank-sum test needs
about 105 observations per group for what the t-test does with 100 (asymptotic
relative efficiency 3/pi = 0.955); under heavy tails it needs about 67. Choose
on the expected shape, not on fashion — and not after seeing the p-values.

### 5c. Permutation and bootstrap

**Permutation** builds the null by redoing a computational experiment that
embodies the null story.

- **R5.6 — The only assumption is exchangeability under the null**, and it is
  stronger than it sounds: the *entire distribution* must be identical between
  the groups being shuffled, not just the mean.
- **R5.7 — How you permute defines the null you tested.** For repeated
  measures on the same patients, shuffling labels across patients tests a
  different (and usually wrong) hypothesis than flipping before/after within
  patient. For structured data, permuting within stratum (cell type, batch,
  region) tests "is there structure beyond the stratum", whereas permuting
  globally tests "is there any structure at all". Always state in words the
  null the shuffling scheme encodes and check it matches the claim.
- **R5.8 — Any statistic is allowed, so the statistic must be pre-specified.**
  Two groups can have *identical* means (Welch p = 1.00) while a permutation
  test on "count below 3.5" gives p = 0.015. That freedom is the method's
  strength and its largest researcher degree of freedom. A statistic chosen
  after inspection is p-hacking with extra steps.
- **R5.9 — p-value resolution is bought with computation**:
  `p = (k + 1) / (N + 1)` where k is the number of permutations at least as
  extreme and N the number performed. p < 1e-6 requires ~1e6 permutations; a
  reported p of 0.0001 from 1,000 permutations is impossible. For many tests,
  use an adaptive/sequential scheme rather than a flat N.
- **R5.10 — Permutation handles multiplicity natively.** Compare each case's
  statistic to the distribution of the *maximum* statistic over all cases in
  each permutation; this controls the family-wise rate without assuming
  independence between tests.

**Bootstrap** estimates the sampling distribution of a summary by resampling
the sample with replacement.

- **R5.11 — The key assumption is representativeness of the sample**; the
  bootstrap cannot repair a biased sample, it faithfully reproduces its bias.
- **R5.12 — Tail estimates need iterations.** A 95% interval from 200
  resamples is noise at the ends; use >= 10,000 for intervals.
- **R5.13 — Bootstrap estimates can be biased** (medians, variances, ratios,
  extremes especially). Use BCa or an explicit bias correction, and never
  bootstrap an extreme order statistic such as the maximum.
- **R5.14 — Small samples limit both methods.** With n1 = n2 = 3 the smallest
  attainable exact two-sided permutation p is 0.10; with 4 vs 4 it is 0.029.
  A sign test on 5 nonzero pairs cannot go below 0.0625. **If the minimum
  attainable p exceeds alpha, the design could not have produced a significant
  result and the claim is Not assessable** — no amount of computation helps.
  Check with `stat_min_attainable_p`.

---

## 6. What the number is allowed to mean

- **R6.1 — p is not an effect size and not a probability that the hypothesis
  is true.** Every claim needs an estimate with an interval in interpretable
  units. A p-value alone is an incomplete claim.
- **R6.2 — "No significant difference" is not evidence of no difference.** An
  exact two-sided p of 1.00 does not establish equivalence. Absence claims
  require an equivalence test against a pre-stated margin, or a power/precision
  statement; otherwise the correct wording is "no evidence of a difference"
  and the interval must be shown.
- **R6.3 — Significant and meaningless coexist.** At large n, trivial
  differences clear alpha. Ask whether the effect size is biologically or
  clinically relevant, separately from the p-value.
- **R6.4 — Check that reported numbers are mutually consistent**: p against the
  statistic and df; CI against the SE; n against the plotted points; percentages
  against their denominators. Recompute whatever the text gives you enough to
  recompute.
- **R6.5 — Discretised language is a finding.** "Trending toward
  significance", "marginally significant", "approached significance" are
  p > 0.05 with a thumb on the scale.

---

## 7. Multiplicity and researcher degrees of freedom

Running one test 100 times at alpha = 0.05 yields ~5 significant results from
pure noise. Running *different analyses* until one works does the same thing
invisibly.

| Correction | Controls | Behaviour |
|---|---|---|
| Bonferroni | family-wise error: P(>= 1 false positive) <= alpha | very conservative; not data-dependent |
| Benjamini-Hochberg FDR | expected proportion of false positives *among declared discoveries* | adaptive threshold that depends on how many hits there are; the right default for screens |

- **R7.1 — Count the tests that were actually run, not the ones reported.**
  Genes x contrasts x time points x subgroups. Correction applied only to the
  reported subset is not a correction.
- **R7.2 — Match the correction to the claim.** "This gene is differentially
  expressed" is an FWER claim; "these 300 genes are enriched for X" is an FDR
  claim. Reporting one gene plucked from an FDR list at its q-value overstates
  it.
- **R7.3 — FDR assumes a sensible p-value distribution.** BH needs independence
  or positive dependence; with arbitrary dependence use BY or permutation
  max-statistics. Discrete tests (small-n sign tests, Fisher exact on sparse
  tables) give lumpy p-value distributions that make BH conservative and
  unstable.
- **R7.4 — Subgroup findings are exploratory** unless pre-specified, and must
  be counted into the multiplicity.

### P-hacking screen

Evidence of p-hacking is statistical, not moral: look for the fingerprint, then
report it as a risk, not an accusation.

Flags, in rough order of severity:

1. p-values clustered just below 0.05 across the paper (run `stat_pcurve`; a
   real effect yields right-skew with mass near 0, p-hacking piles up just
   under alpha).
2. Sample size not pre-specified; n differs between panels for the same cohort;
   signs of optional stopping ("we added animals until").
3. Outcome switching: the abstract's primary outcome is not the registered /
   methods-stated one.
4. Exclusions applied after analysis, or outlier rules stated without a
   threshold fixed in advance.
5. Test changed, covariates added or transformation applied with no
   justification, especially when the change crosses 0.05.
6. One-tailed tests appearing only where two-tailed would fail (R3.2).
7. Permutation statistic or permutation scheme chosen after inspection (R5.8).
8. Selective reporting: arms, time points, probes or genes mentioned in methods
   but absent from results.
9. Correction applied inconsistently across claims.

Exploratory analysis is legitimate and necessary. The line is **disclosure**:
exploratory results labelled as exploratory, with a confirmatory test on fresh
data or an honest multiplicity count, are fine. The same results presented as
confirmatory are not.

---

## 8. Calibration — what is NOT a violation

Over-flagging destroys a review's credibility. These are acceptable:

- Unequal group sizes, by themselves.
- Non-normal *raw* measurements when the claim concerns means, n is adequate
  and Welch was used.
- A nonparametric test when the parametric one would also have worked —
  slightly conservative, not wrong.
- No multiplicity correction across genuinely independent, pre-specified
  primary hypotheses — state it, do not fail it.
- Descriptive or exploratory reporting with no p-values at all, when framed as
  such. Absence of a test is not an error when no claim of difference is made.
- A null result reported as "no evidence of a difference" with an interval.
- Parametric tests on modest n with symmetric, well-behaved Q-Q plots.
- Bootstrap CIs on a well-behaved mean without BCa.

---

## 9. Re-analysis protocol (when raw data is available)

1. **Reproduce the reported number first.** Match n per group before anything
   else; an n mismatch means you are not looking at the same analysis, and
   nothing after it is interpretable.
2. **Recompute as reported** — same test, same tails, same variance
   assumption. Record the delta from the published value.
3. **Recompute as it should have been** per sections 2-5. Record that delta too.
4. **Show the test-choice sensitivity**: run the candidate tests side by side
   (`stat_two_group`) so the reader sees how much the conclusion depends on the
   choice. A claim that survives every reasonable test is robust; one that
   lives only under the pooled one-tailed t-test is not.
5. **Report an effect size with an interval** in original units, whatever the
   test.
6. **Re-do multiplicity across the full set of tests you can reconstruct**
   (`stat_multiplicity`) and report how many claims survive BH and Bonferroni.
7. **Never present a re-analysis without stating what you could not check** —
   unavailable raw data, aggregated tables, missing per-group n, unknown
   exclusion rules.

---

## 10. Verdicts

One verdict per claim, plus a severity.

| Verdict | Meaning |
|---|---|
| **Supported** | Method appropriate; number reproduces; conclusion matches the quantity tested |
| **Supported, overstated** | The analysis holds but the sentence claims more than it (causality, equivalence, generality, a median claim from U) |
| **Mis-specified** | Wrong test, wrong unit, wrong tails, wrong assumption; conclusion may or may not survive correction — say which, and recompute if data allow |
| **Not assessable** | Design or reporting cannot resolve it: method unstated, n unrecoverable, or minimum attainable p above alpha |
| **Contradicted** | Correct re-analysis reverses or removes the claim |

| Severity | Meaning |
|---|---|
| A | The claim does not survive |
| B | The claim survives; its reported strength does not |
| C | Reporting/transparency defect; conclusion unaffected |

Write each finding as: **what was done -> what it assumes -> why that fails
here -> what should be done -> what changes.** A finding without the last
clause is an opinion.

---

## 11. Report format

Deliver a report artifact, not chat prose. Load **`figure-contract`** before
building any figure in it, and `figure-style` for final rendering.

Required sections:

1. **Verdict table** — one row per claim: id, claim (short), design, test used,
   test indicated, reported p, recomputed p, effect size + CI, verdict,
   severity. This is the deliverable; everything else supports it.
2. **Summary paragraph** — the two or three findings that change how the paper
   should be read.
3. **Per-claim findings**, in severity order, each in the five-part form above.
4. **Figures** (only where they carry the argument):
   - Q-Q panels for the assumptions actually relied on (`stat_qq_panel`).
   - Test-choice sensitivity: reported vs recomputed p across candidate tests.
   - Effect sizes with intervals, in original units.
   - Multiplicity: raw vs BH vs Bonferroni discovery counts.
   - p-curve across the paper's tests when a p-hacking risk is raised.
5. **Limitations of the review** — what the available data could not resolve.

Figure discipline (from `figure-contract`): plot individual observations at
the level of the experimental unit, label what error bars are, keep a common
scale when panels are compared, and never let a styling pass delete
observations or uncertainty.

---

## Helpers

Loaded into the kernel with this skill.

```python
stat_two_group(a, b, paired=False, n_perm=10000)
# DataFrame: every candidate test side by side with the assumption each buys.
# .attrs["effects"] -> mean difference, 95% CI, Hedges' g or Cohen's dz,
# probability of superiority, variance ratio, n.

stat_qq_panel(groups, paired=False)          # dict {label: values}; paired=True
                                             # plots the within-pair differences
stat_permutation_p(a, b, statistic=None, paired=False, n_perm=10000)
                                             # -> p, k, resolution 1/(N+1)
stat_multiplicity(pvals, alpha=0.05, labels=None)   # BH q + Bonferroni + counts
stat_min_attainable_p(n1, n2=None, kind="sign")     # "sign"|"signrank"|
                                             # "ranksum"|"permutation"
stat_pcurve(pvals, alpha=0.05)               # (fig, binned counts)
```

---

## Self-review checklist

The chain, as questions. Every claim, every time.

1. What population, and is the sample representative of it? Randomised?
   Blinded? Confounded?
2. What is the independent experimental unit, and does the reported n count it?
3. Independent or paired? One- or two-tailed, and was the direction
   pre-committed? Equal variance assumed, and why?
4. Which quantity has to be normal, and does its Q-Q plot support it?
5. Which null does this test actually test — and for a permutation test, what
   does the shuffling scheme say in words?
6. Is there an effect size with an interval in original units?
7. How many tests sit behind this claim, and what correction matches the claim?
8. Could this design have produced a significant result at all?
9. Does the sentence in the abstract claim more than the quantity tested?
