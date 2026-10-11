# Statistical review — Alavi Naini et al. (2026)

**Paper.** Alavi Naini L, Linde N, Malik S, Syed Y, Cheek AO (2026). *Diel Activity Patterns of Bobcats and Domestic Cats in the Houston Metropolitan Area.* microPublication Biology. doi:10.17912/micropub.biology.001911

**Data reviewed.** The authors' complete Dryad deposit (doi:10.5061/dryad.s4mw6m9jg): `Bobcat_Data.csv` (81 records), `Domestic_Cat_Data.csv` (795 records), `Dhat R Script MicroPub.R`, `Watsons U2 and Polar Plot.m`, and the two deposited overlap figures. Every number below was computed in this session from those files.

**Reproducibility, up front.** This deposit is unusually complete and it reproduces. All four analysis groups match the paper exactly (49 / 696 / 32 / 99 detections; 7 bobcat-only, 19 cat-only, 7 shared sites); the hard-coded time vectors in the MATLAB script are identical to the CSV-derived fixed-CST local minutes to within 3×10⁻⁷ min; both Watson's U² statistics reproduce to four decimals; and both overlap coefficients reproduce exactly (Δ̂₁ = 0.8525 and 0.6465 against the published 0.852 and 0.646). Nothing in this review is a claim that the authors' arithmetic is wrong. The findings concern the **experimental unit**, the **absence of intervals on the estimates that carry the argument**, and **one p-value that is misreported**.

---

## 1. Verdict table

| id | Claim (short) | Design | Test used | Test indicated | Reported p | Recomputed p | Effect size + CI | Verdict | Sev |
|---|---|---|---|---|---|---|---|---|---|
| **C5** | Cat and bobcat diel activity differ where they co-occur | 2-sample circular, same 7 sites | Watson's U², asymptotic | Watson's U² on independence-filtered detections, site-stratified null | p < 0.05 | **U²=0.1893, p=0.0476** exact; 30-min filter **p=0.104**; site-stratified permutation **p=0.072**; both **p=0.116** | Δ̂₁=0.647, site-clustered 95% CI 0.494–0.759 | **Contradicted** | **A** |
| C1 | Bobcats primarily nocturnal *wherever* present | 1-sample proportion vs 50%, clustered | none | proportion with site-clustered interval | — | site-level P(≤50%) = 0.342 | 67.3% of detections (naive CI 52.5–80.1); site-level mean 55.8% (CI 30.3–82.7); 69.1% over the 7 sites with n≥5 | Supported, overstated | B |
| C3 | Activity "similar" at single-species sites | 2-sample circular; species confounded with site set | Watson's U² | identifiable contrast + equivalence margin | **p < 0.20** | **U²=0.0753, p=0.447**; filtered p=0.367 | Δ̂₁=0.8525; no equivalence margin | Mis-specified | B |
| C6 | Overlap "much less" where co-occurring (0.647 vs 0.852) | difference of two Δ̂ on disjoint site sets | none | bootstrap CI on the difference, site-level | — | detection-level P(diff≤0)=0.031; site-clustered **P=0.117** | diff = 0.206; detection 95% CI −0.004 to 0.312; site-clustered −0.088 to 0.310 | Supported, overstated | B |
| C7 | Cats shift to daytime where bobcats present (51% vs 85%) | between-site-group, same species | none | Watson's U² or proportion contrast, site-level null | — | detection-level p=2.1×10⁻¹¹; site-level permutation **p=0.059**; %night site-permutation p=0.003; site as unit (n≥5, 17 vs 3) **p=0.088** | 34.0 pct-pt detection-level; 24.5 pct-pt site-level, 95% CI 11.8–36.3 | Supported, overstated | B |
| C8 | Bobcats ≤65% developed land, cats ≥65% | 2-group site-level covariate | none | site-level test, no post hoc cutpoint | — | not recomputable | 65% cutpoint = the shared-site group mean | Not assessable | B |
| C10 | Temporal + spatial partitioning facilitate coexistence | observational, cross-sectional | none | no design here separates interaction from urban gradient | — | — | site type confounded with developed cover (50/82/65%) and distance | Supported, overstated | B |
| C4 | Δ̂ = 0.852 = high overlap at solo sites | point estimate, not a test | Δ̂₁, no interval | Δ̂₁ + bootstrap interval | — | — | 0.8525 reproduced; bootstrap 95% CI 0.726–0.895; site-clustered 0.574–0.856; Δ̂₄=0.842 | Supported, overstated | C |
| C9 | Land cover 50±19 / 82±14 / 65±16% developed | descriptive | none | none required | — | not recomputable (per-site land cover not deposited) | — | Not assessable | C |
| C12 | Bobcat-only sites >13.7 km, cat-only sites <12 km from downtown | descriptive spatial | none | none required | — | not recomputable (lat/long columns hold one fixed reference point for every row) | — | Not assessable | C |
| C2 | Cats primarily nocturnal at cat-only sites | 1-sample proportion vs 50%, clustered | none | proportion with site-clustered interval | — | site-level P(≤50%) < 0.0001 | 85.5% (naive CI 82.6–88.0); site-level 80.3% (CI 69.8–89.3) | **Supported** | none |
| C11 | 33 sites; 81 bobcat / 795 cat detections; 7/19/7 split | tally | — | — | — | reproduces exactly | 49+32=81; 696+99=795 | **Supported** | none |

---

## 2. Summary

Three things change how this paper should be read.

**The one significant test does not survive the experimental unit.** The paper's single inferential result — bobcat and domestic cat activity differ at shared sites, Watson's U² = 0.189, p < 0.05 — reproduces exactly, and the exact asymptotic p is 0.0476. It sits 0.0024 below alpha. A detection is not an independent animal-night: 11.8% of consecutive same-species, same-camera detections are less than 30 minutes apart, and at shared sites 91% of the 99 domestic cat detections come from two of the seven cameras. Applying the standard 30-minute camera-trap independence filter gives p = 0.104; keeping every detection but permuting species labels *within* site, which is the null the claim actually needs, gives p = 0.072; doing both gives p = 0.116. The direction of the difference is unchanged under all three, but the significance is not recoverable under any of them.

**The paper's headline claim is never tested, and the test it does report is a different contrast.** The abstract says domestic cats "shifted to more daytime activity" where bobcats were present. That is a within-species comparison between cat-only sites (85% nocturnal) and shared sites (51%). No test of it appears in the paper. The reported Watson's U² at shared sites compares cats to *bobcats*, not cats to cats. When the shift is tested, the difference is real and large — 24.5 percentage points with the site as the unit, 95% CI 11.8 to 36.3 — but only three shared sites have enough detections to contribute, the site-level permutation p is 0.088, and the two site groups differ in developed land cover (65% vs 82%) and in distance from downtown. The design cannot separate "bobcats are there" from "it is less urban there".

**Both Δ̂ values are reported without the intervals the deposited script already computes.** `Dhat R Script MicroPub.R` calls `bootstrap()` and `bootCI()`; no interval reaches the paper. Recomputing them, the solo and shared intervals overlap: 0.726–0.895 against 0.536–0.797 at the detection level, 0.574–0.856 against 0.494–0.759 with sites resampled as clusters. The difference of 0.206 that carries the temporal-partitioning argument has a site-clustered 95% CI of −0.088 to 0.310. "Overlapped much less" is a statement about two point estimates that are not separable at the unit of replication.

Calibration notes, so this review is not read as flagging everything. The Dhat1-vs-Dhat4 choice is correct: the script selects Dhat1 when the smaller sample is below 50, which is the Ridout & Linkie rule, and the smaller samples here are 49 and 32. Watson's U² is the right test family for two-sample circular data, and the MATLAB implementation of the statistic is correct and origin-invariant despite the inputs being in minutes rather than radians. Using a single reference coordinate for the solar-time conversion is a negligible approximation at this spatial scale. Unequal group sizes, the observational design itself, and the absence of multiplicity correction across two pre-specified primary contrasts are all acceptable. Several of this paper's claims are descriptive and framed as such.

---

## 3. Findings, in severity order

### C5 — Contradicted (A). The significant result does not survive the experimental unit.

**What was done.** Watson's two-sample U² was computed on 32 bobcat and 99 domestic cat detection times (fixed-CST clock minutes) from the seven sites where both species were recorded, and compared to a tabulated critical value: U² = 0.189, p < 0.05.

**What it assumes.** That the 32 and 99 times are independent draws from the two species' underlying activity distributions. Watson's U² has no cluster term; its null distribution is built on exchangeability of independent observations between the two samples.

**Why that fails here.** The detections are clustered twice over. Within a camera, a single animal retriggers: 11.8% of consecutive same-species, same-camera gaps are under 30 minutes and 5.4% are under one minute, including a run of 14 domestic cat detections at roughly 30-second intervals. Across cameras, the sample is dominated by two of seven sites — WCJP contributes 12 bobcat and 59 cat detections, FHNA 10 and 31, so two cameras carry 91% of the cat sample and 69% of the bobcat sample. The remaining five sites contribute one or two detections each. The nominal n of 131 is doing work that roughly seven independent site-level units can support. Independently of clustering, the reported p is 0.0476, which leaves no margin for any correction at all.

**What should be done.** Collapse detections to independent events with the conventional 30-minute threshold, and test against a null that respects site structure — permute species labels within each shared site, which encodes "within a site, the two species' detection times are exchangeable".

![Watson's U² p-value for the shared-site species comparison under four analyses: as reported (0.048), after a 30-minute independence filter (0.104), with species labels permuted within site (0.072), and both (0.116). Only the as-reported analysis falls below alpha = 0.05.](fig_alavinaini_unit_sensitivity.png)

**What changes.** U² falls from 0.1893 to 0.1500 under the 30-minute filter (n = 28 vs 91), p = 0.104. On unfiltered data with the within-site permutation null, p = 0.072 (5,000 permutations). With both, p = 0.116. The claim of a significant difference is not supported under any of these; the point estimate Δ̂₁ = 0.647 and the direction of the difference are unaffected. The honest sentence is that the two species' activity distributions at shared sites differ by Δ̂₁ = 0.647 (site-clustered 95% CI 0.494–0.759) with no significant difference detectable at the level of the site.

### C1 — Supported, overstated (B). "Wherever they were present" is a per-site claim and does not hold per site.

**What was done.** 67% of bobcat detections at bobcat-only sites and 66% at shared sites occurred at night (I reproduce 67.3% and 65.6% exactly using true sunrise/sunset at the Houston reference coordinate), supporting "bobcats exhibited primarily nocturnal activity wherever they were present."

**What it assumes.** That a detection-weighted percentage describes the typical site, and that 67% is distinguishable from the 50% expected under activity uniform in solar time.

**Why that fails here.** The seven bobcat-only sites contribute 14, 12, 10, 7, 3, 2 and 1 detections, so three cameras supply 73% of the sample. Per site, the nocturnal fraction is 78.6, 50.0, 33.3, 100, 28.6, 0 and 100%. Restricting to the seven bobcat sites with at least five detections (solo and shared pooled) the fractions are 78.6, 50.0, 28.6, 100, 60.0, 100 and 66.7%. Two of those seven are at or below 50%.

**What should be done.** Report the proportion with an interval that resamples sites, and either weaken "wherever" to an aggregate statement or show the per-site values.

![Per-camera-site nocturnal percentage for domestic cats and bobcats at single-species and shared sites, marker area proportional to the square root of detections at that site, with the detection-weighted percentage quoted in the paper and the mean over adequately sampled sites marked separately.](fig_alavinaini_site_unit.png)

**What changes.** The site-level mean nocturnal fraction at bobcat-only sites is 55.8% with a site-bootstrap 95% CI of 30.3–82.7%, and P(site-level mean ≤ 50%) = 0.342. The aggregate statement "bobcats were predominantly nocturnal" survives (69.1% across adequately sampled sites); "wherever they were present" does not. Separately, bobcat activity does not differ between solo and shared sites (Watson's U² = 0.0736, p = 0.46), which is the real support for the "wherever" framing and is worth reporting in place of the percentage.

### C3 — Mis-specified (B). An unidentifiable contrast, an absence claim, and a misreported p.

**What was done.** Watson's U² compared 49 bobcat detections at seven bobcat-only sites with 696 domestic cat detections at 19 cat-only sites; U² = 0.0753, reported as p < 0.20, and read as "the diel activity patterns were similar".

**What it assumes.** That the only systematic difference between the two samples is species, and that a non-significant U² licenses a statement of similarity.

**Why that fails here.** Three separate problems. First, species and site set are perfectly confounded: no bobcat-only site contributes a cat observation and no cat-only site contributes a bobcat observation, so a difference here could equally be a difference between two disjoint sets of cameras in two different parts of the metropolitan area (50% vs 82% developed cover). The contrast is not identifiable, and that is a property of the design, not of the test. Second, "similar" is an absence claim made from a failure to reject; no equivalence margin is stated and none can be inferred (skill R6.2). Third, the reported p is inconsistent with the statistic: U² = 0.0753 corresponds to an asymptotic p of 0.447, and the tabulated critical value at alpha = 0.20 is U² ≈ 0.117, so the correct tabular statement is p **>** 0.20, not p < 0.20.

**What should be done.** Report p > 0.20 or the exact asymptotic p; state the confounding explicitly; and if similarity is the claim, state the overlap coefficient with its interval as the equivalence evidence rather than the non-significant test.

**What changes.** Recomputed p = 0.4469 (0.3674 after the 30-minute filter), so the direction of the conclusion is unchanged and in fact more clearly null than reported. The claim should be worded as "no evidence of a difference", and the inference that this reflects *species* similarity rather than site-set similarity cannot be made from this design.

### C6 — Supported, overstated (B). A difference of two estimates presented without either one's uncertainty.

**What was done.** Δ̂₁ = 0.852 at single-species sites and Δ̂₁ = 0.647 at shared sites were reported as point estimates and contrasted in words: activity patterns "overlapped much less where they co-occurred".

**What it assumes.** That the gap between two kernel-density overlap estimates computed on disjoint, modestly sized samples is larger than its own sampling variability.

**Why that fails here.** Δ̂ is an estimate, not a test, and no interval or comparison accompanies it — even though the deposited R script computes `bootstrap(..., nb = 1000)` and `bootCI()` for both. The smaller sample behind the shared-site estimate is 32 bobcat detections from seven cameras, five of which contributed one or two detections.

**What should be done.** Report both Δ̂ values with bootstrap intervals, and put an interval on the difference, resampling sites rather than detections.

![Coefficient of overlap with percentile 95 percent bootstrap intervals at single-species and shared sites, resampling detections and resampling sites, plus the difference between the two estimates with its interval, which spans zero under both resampling schemes.](fig_alavinaini_overlap_ci.png)

**What changes.** Smoothed bootstrap (2,000 resamples, von Mises kernel as in the `overlap` package): solo Δ̂₁ = 0.852, percentile 95% CI 0.726–0.895; shared Δ̂₁ = 0.646, 95% CI 0.536–0.797. The intervals overlap. The difference is 0.206 with a percentile 95% CI of −0.004 to 0.312, P(difference ≤ 0) = 0.031. Resampling sites as clusters: solo 0.574–0.856, shared 0.494–0.759, difference 95% CI −0.088 to 0.310, P(difference ≤ 0) = 0.117. The direction is consistent across both schemes and the point estimate is substantial, so the claim survives as a direction; "much less" as an established fact does not.

### C7 — Supported, overstated (B). The paper's headline effect is real and large, untested as published, and confounded.

**What was done.** 85% of domestic cat detections at cat-only sites and 51% at shared sites occurred at night (I reproduce 85.5% and 51.5%), and the abstract concludes that domestic cats "shifted to more daytime activity" where bobcats were present.

**What it assumes.** That the two site groups differ only in bobcat presence, and that the detection-level percentages describe sites.

**Why that fails here.** No test of this contrast appears in the paper; the reported shared-site Watson's U² is a cat-versus-bobcat comparison, not a cat-versus-cat one. On the data: 59 of 99 shared-site cat detections come from WCJP and 31 from FHNA, so two cameras carry 91% of the "shifted" sample and the remaining four shared sites contribute one detection each (all nocturnal). The site groups also differ systematically in exactly the covariate the paper itself reports — 82 ± 14% developed cover at cat-only sites against 65 ± 16% at shared sites — and in distance from downtown, so bobcat presence is entangled with urbanisation. This is a design-level confound that no re-analysis repairs (skill §1).

**What should be done.** Test the contrast the claim makes, at the site level, and state the confounding rather than attributing the shift to bobcats.

**What changes.** The difference is real and not small. Watson's U² for cat-solo vs cat-shared is 1.281 (detection-level p = 2.1×10⁻¹¹; site-level permutation p = 0.059). On nocturnal fraction, a site-level permutation of the detection-weighted difference gives p = 0.0034; with the site as an unweighted unit and restricting to the 20 cat sites with at least five detections (17 solo, 3 shared), the difference is 24.5 percentage points (78.0% vs 53.5%), bootstrap 95% CI 11.8–36.3 points, permutation p = 0.088. Naive detection-level χ² gives p = 1.6×10⁻¹⁵, which is the number the paper's framing implies and which overstates the evidence by many orders of magnitude. The defensible sentence: domestic cats at the seven shared sites were markedly less nocturnal than at cat-only sites (about 25 percentage points, 95% CI 12–36), based on three adequately sampled shared sites, and this difference cannot be attributed to bobcat presence rather than to the lower urbanisation of those sites.

### C10 — Supported, overstated (B). A mechanism claim from a cross-sectional observational design.

**What was done.** The abstract concludes that "both temporal and spatial niche partitioning appear to facilitate predator coexistence in urban landscapes", and the discussion that temporal partitioning "may allow domestic cats to avoid interspecific competition with sympatric bobcats".

**What it assumes.** That the association between bobcat presence and cat activity timing reflects a response to bobcats.

**Why that fails here.** Site type is not assigned; it is observed, and it covaries with developed land cover (50%, 82%, 65% across the three groups), distance from downtown, and whatever else separates parks and golf courses on the urban fringe from inner-loop sites. There is no within-site contrast (no site where bobcats arrive or leave), no temporal control, and no randomisation. Hedged verbs do not change what the design can identify.

**What should be done.** Frame as a hypothesis consistent with the data, state the land-cover confound alongside it, and name the design that would test it — within-site activity before and after bobcat colonisation, or site-level modelling with land cover as a covariate.

**What changes.** The conclusion survives as a hypothesis, which is appropriate for a short-format report; what should be removed is the implication that the data discriminate between the predator-avoidance explanation and the urbanisation explanation. They do not.

### C8 — Not assessable (B). A dichotomy at a cutpoint equal to a group mean, with no deposited data.

**What was done.** "Bobcats were detected more frequently in areas with ≤65% developed land cover, while domestic cats were detected more frequently in areas with ≥65% developed land cover."

**What it assumes.** That 65% is a meaningful boundary and that the two-sided comparison was specified independently of the data.

**Why that fails here.** 65% is exactly the reported mean developed-land cover of the shared-site group, so the threshold is a feature of the data being described. No test accompanies the claim, and per-site land cover — measured by hand in Google Earth Pro — is not in the deposit, so neither the cutpoint nor the comparison can be checked.

**What should be done.** Deposit per-site land cover and report the continuous covariate by site group with a site-level test, rather than a dichotomy at a sample-derived cutpoint.

**What changes.** Nothing can be recomputed. The claim is Not assessable; the description of the pattern (bobcats at less developed sites) is consistent with the reported group means, but the specific 65% dichotomy carries no support that the deposit can demonstrate.

### C4 — Supported, overstated (C). The estimate reproduces; the interval was computed and not reported.

**What was done.** Δ̂₁ = 0.852 at single-species sites, described as "high overlap", with no interval.

**What it assumes.** That a point estimate communicates a confidence statement.

**Why that fails here.** It does not (skill §"everything is a random variable"), and in this case the authors' own script already produces the missing interval.

**What should be done.** Report the bootstrap interval the script computes, using at least 10,000 resamples rather than the scripted 1,000 (skill R5.12), and prefer the percentile interval: the basic interval here runs to 0.979 and would run above 1 for a parameter bounded at 1.

**What changes.** Δ̂₁ = 0.8525 reproduces the published value exactly; Δ̂₄ = 0.842. Percentile 95% CI 0.726–0.895 at the detection level, 0.574–0.856 with sites resampled. "High overlap" is a fair reading of the point estimate; the site-level lower bound of 0.57 should temper it.

### C9, C12 — Not assessable (C). Spatial and land-cover data were not deposited.

The `Latitude` and `Longitude` columns in both CSVs hold a single fixed reference point — the 1910 Harris County Courthouse — repeated on every row, by design, because the solar-time conversion used one representative coordinate. The consequence is that the deposit contains no site coordinates and no per-site land cover. The distance claims (bobcat-only sites all >13.7 km from downtown, cat-only sites nearly all within 12 km) and the land-cover summaries (50 ± 19%, 82 ± 14%, 65 ± 16% developed) cannot be recomputed. These are descriptive statements, so their absence is a data-availability defect rather than an analytical error, but it blocks verification of the entire spatial half of the paper's "spatial and temporal partitioning" conclusion.

### Reporting and transparency notes (C, no claim affected)

- The two analyses use **different time variables** for the same comparison: Watson's U² is computed on fixed-CST clock minutes, Δ̂ on solar time. Neither is wrong, but a reader comparing U² to Δ̂ is comparing analyses on different clocks, and the paper does not say so.
- The deposited MATLAB script reads two CSV filenames that are **not in the deposit**, and the vectors actually analysed are pasted in as literals described in the README as "manually curated". I verified them against the CSVs and they are exact, so the curation is correct — but as deposited the script does not run, and the correctness is not self-evident to a reader.
- The MATLAB script **computes no p-value**. U² is returned and the reported p must have been read from a table. This is where the C3 inequality error enters; a two-line asymptotic p (`p = 2 Σ (−1)^{m−1} exp(−2m²π²U²)`) would have prevented it.
- **Multiplicity**: two tests are reported. These are plausibly pre-specified primary contrasts, so no correction is required (skill §8) — but it is worth noting that even Bonferroni across just these two would put the shared-site result at p = 0.095.
- The text gives Δ̂ = 0.647 for shared sites while the figure and README give 0.646; the computed value is 0.6465.
- No p-hacking signature is present. Two tests, both pre-specified in the methods, both reported with their statistics, no subgroup proliferation, no evidence of optional stopping, no selective reporting of arms or seasons. The one borderline p (0.0476) is a single result, not a pattern; a p-curve on two values would be meaningless and is not reported.

---

## 4. Limitations of this review

- **The design-level confound is not resolvable with any data.** Site type (bobcat-only / cat-only / shared) is observed, not assigned, and covaries with developed land cover and distance from downtown. No re-analysis I can perform separates a response to bobcats from a response to urbanisation. This caveat attaches to C7 and C10 regardless of how the tests are run.
- **Per-site land cover and site coordinates are not in the deposit**, so C8, C9 and C12 could not be recomputed at all. They are recorded as Not assessable, not as errors.
- **The independence filter is a judgement, not a fact.** 30 minutes is the common camera-trap convention; I report 5, 15, 30 and 60-minute thresholds (n falls from 49/696/32/99 to 42/610/28/88 at 60 minutes) and the conclusion that C5 loses significance holds across all of them, but the authors never state a filter and there is no way to know what they intended.
- **No individual identification.** Bobcats are individually identifiable from pelage in good photographs; the deposit records none, so "how many animals" remains unknown and the site is the best available unit, not the ideal one. Cameras at least 1 km apart addresses between-site duplication but not repeated detection of the same animal at one camera over four years.
- **Bootstrap scheme.** I reimplemented `overlap::densityFit` (von Mises kernel) and a Best–Fisher von Mises sampler because the compiled `overlap` package could not be installed in this environment; the reimplementation is validated by reproducing both published Δ̂₁ values to four decimals and Δ̂₄ in addition. Bootstrap replicates: 2,000 for the Δ̂ intervals, 2,000 for the site-cluster scheme, 10,000 for the proportion intervals, 5,000–20,000 for permutations. The site-cluster interval for shared sites discarded 51 of 2,000 resamples in which a resampled site set yielded fewer than 8 detections for one species.
- **Watson's U² p-values are asymptotic.** I used the standard series P(U² ≥ u) = 2 Σ (−1)^{m−1} exp(−2m²π²u), verified against the published critical values (0.187 → 0.0499; 0.152 → 0.0995). At n = 32 vs 99 the asymptotic approximation is reasonable but not exact; the permutation results reported for C5 do not depend on it.
- **Not assessed:** seasonal structure (16 sampling periods pooled; a season × site-type interaction is plausible and untested, by the authors and by me), camera-model effects (three models, confounded with deployment), and detection probability (no occupancy model; "occupancy" here means ≥1 detection, which conflates true absence with non-detection).
