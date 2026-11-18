## 1. Introduction

Stretched penile length (SPL) is measured in the newborn period for a single purpose: to identify the boy whose penis is abnormally small, because micropenis may be the first sign of congenital hypogonadotropic hypogonadism, combined pituitary hormone deficiency or a difference of sex development [@Lee2006; @Hatipoglu2013; @Boehm2015]. The neonatal period is the moment of greatest diagnostic leverage. In the first months of life the hypothalamic–pituitary–gonadal axis is physiologically active, and gonadotropin deficiency can be confirmed directly [@KuiriHanninen2014; @Grumbach2005]. Early gonadotropin replacement is under active investigation [@Bouvattier2011].

The diagnostic threshold is conventionally 2.5 SD below the mean. A threshold defined in this way is only as good as the reference that supplies the mean and the SD.

The reference most often quoted is half a century old. Feldman and Smith reported a stretched length of "3.5 cm plus or minus 0.7 cm" in term newborns [@Feldman1975]. The widely taught absolute cut-off of 2.5 cm corresponds to −2.5 SD only if the SD is 0.4 cm, a value later reported in 1,962 Danish and Finnish boys (3.49 ± 0.4 cm) [@Boas2006]. Since then, many national and regional studies have reported newborn SPL, often with means that differ materially from these values [@Matsuo2014]. They have also used techniques that differ in whether, and how firmly, the suprapubic fat pad is depressed.

Population differences matter more than their size might suggest. The diagnosis is made in the extreme tail of the distribution, so a shift of the reference mean by half an SD multiplies or divides the apparent prevalence of micropenis by a factor of about four. This is shown in Paper 4 of this series, a companion Monte Carlo study.

No previous study has synthesised newborn SPL quantitatively across populations. We therefore conducted a systematic review and random-effects meta-analysis with four aims:

1. to estimate the mean and the within-population SD of SPL in healthy term newborns;
2. to quantify between-population heterogeneity, and its association with geographic region, publication period and technique;
3. to derive population-specific −2.5 SD thresholds;
4. to estimate how a single fixed threshold of 2.5 cm misclassifies newborns across populations.

## 2. Methods

The review is reported according to PRISMA 2020 [@Page2021] and the MOOSE guidance for meta-analyses of observational studies [@Stroup2000].

### 2.1 Eligibility

**Included.** Primary studies that reported SPL in healthy male newborns born at term (≥37 weeks' gestation) and measured within the first 28 days of life. Each study had to report a sample size and either a mean or a median.

**Excluded.**

- Reviews.
- Studies restricted to infants with a disease or anomaly.
- Studies reporting only non-stretched (flaccid) length.
- Duplicate reports of the same cohort; in that case the more complete report was retained.

**Secondary eligibility.** Studies reporting SPL by gestational-age band in preterm infants were eligible for a secondary synthesis.

### 2.2 Search and selection

PubMed was searched from inception to 18 November 2026. The search used general and country-specific query strings, supplemented by related-article searches from key studies. The full strategy, dates and hit counts are given in Supplementary File S1. Records were screened by title and abstract, and the full text was obtained from PubMed Central where available.

### 2.3 Data extraction

For each study, or for each subgroup where a study reported more than one population, we extracted:

- country and WHO region;
- population or ethnicity;
- sample size;
- gestational-age criteria;
- age at measurement;
- measurement technique: instrument, and whether depression of the suprapubic fat pad was described;
- the summary statistics reported: mean, SD, SE, median, quartiles, range, and any −2.5 SD value.

Every number was stored with the verbatim sentence or table cell from which it was taken, and with an indicator of whether it came from the full text or only the abstract.

### 2.4 Statistical analysis

**Conversion of summary statistics.** When only a median with quartiles or range was reported, the mean was estimated by the method of Luo et al. [@Luo2018] and the SD by that of Wan et al. [@Wan2014]. An SD was derived from an SE when necessary. Where no measure of dispersion was available, the study contributed to the pooled mean with an imputed SD equal to the median SD of the other studies. Such studies were excluded from the pooled SD, and their influence was tested in sensitivity analysis.

**Pooled mean.** The study-level effect was the mean SPL, with variance SD²/n. Means were pooled with a random-effects model:

- τ² estimated by restricted maximum likelihood [@Viechtbauer2005];
- confidence intervals from the Hartung–Knapp–Sidik–Jonkman method [@Hartung2001; @IntHout2014];
- a 95% prediction interval for the mean of a new population [@Higgins2009; @Riley2011];
- heterogeneity summarised by τ, I² [@Higgins2002] and a Q-profile confidence interval for τ².

**Pooled SD.** The within-population SD was pooled on the log scale. The effect was ln(SD) + 1/[2(n − 1)], with variance 1/[2(n − 1)], using the same random-effects machinery.

**Thresholds and misclassification.** Population-specific −2.5 SD thresholds were computed as mean − 2.5 × SD. For each study with a reported SD, we computed the expected percentage of newborns below the fixed 2.5 cm threshold, Φ[(2.5 − mean)/SD], under normality, and compared it with the nominal 0.62%.

**Sources of heterogeneity.**

- Subgroup analysis by WHO region, tested with Q-between.
- Mixed-effects meta-regression on WHO region, publication year (per decade), explicit description of fat-pad depression, and source level (full text vs abstract), each with Knapp–Hartung t-tests.

**Small-study effects** were examined by funnel plot and Egger's test [@Egger1997] when at least 10 studies were available.

**Robustness** was examined by leave-one-out analysis and by restricting the analysis to four subsets:

- studies with full text;
- studies that described fat-pad depression;
- studies with n ≥ 100;
- studies reporting mean and SD directly.

**Software.** All analyses were performed in Python 3.13 with purpose-written code. The code was validated against the reference implementation in *metafor*, using a standard benchmark dataset: estimates, standard errors, τ² and its Q-profile CI, and meta-regression coefficients all agreed to four decimal places. Code and data are provided as supplementary material.

### 2.5 Risk of bias and certainty

The methodological quality of each study was assessed against the domains of the JBI checklist for prevalence studies, adapted to a continuous normative outcome [@Munn2015]. The domains were:

- sample frame and recruitment;
- adequacy of sample size;
- description of subjects and setting;
- a valid, reliable measurement method, including a described technique and examiner training;
- standard measurement for all participants.

Certainty in the pooled estimates was rated with GRADE, applying the framework for evidence from observational and prognostic or normative estimates [@Guyatt2008; @Iorio2015].
