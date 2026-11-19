# Search log: SPL measurement reliability and technique effects (P4)

- Database: PubMed via the PubMed MCP tools.
- All searches were run on 2026-11-18, with no date limits.
- Extraction file: `reliability_extraction.csv`. It has 33 rows covering 18 studies.
  - 12 studies are paediatric in vivo SPL studies.
  - 2 are paediatric 3D-model studies (context only).
  - 1 is a systematic review (B12).
  - 3 are adult studies (indirect evidence, flagged "ADULT").

## Pre-specified queries

| # | Query | Hits |
|---|---|---|
| B1 | penile length measurement reliability children | 14 |
| B2 | interobserver variability stretched penile length | 5 |
| B3 | penile length measurement technique infants | 147 (all 147 retrieved and screened) |
| B4 | penile length caliper ruler comparison | 0 |
| B5 | intraobserver penile length neonates | 0 |
| B6 | penile measurement accuracy pediatric urology | 11 |

## Supplementary queries

These were run because B4 and B5 returned nothing.

| # | Query | Hits |
|---|---|---|
| B7 | penile length interobserver | 25 |
| B8 | penile length reproducibility AND (child OR infant OR newborn OR boys) | 42 |
| B9 | (penile length[Title/Abstract]) AND (ultrasound OR ultrasonography) AND (infant OR newborn OR boys) NOT fetal[Title] | 44 |
| B10 | stretched penile length erect length correlation | 15 |
| B11 | penile length measurement error | 22 |
| B12 | suprapubic fat penile length children | 4 |
| — | syringe penile length measurement children | 1 (duplicate) |

## Queries run but discarded (not screened)

| Query | Hits | Reason |
|---|---|---|
| penile length reproducibility OR intra-observer OR inter-observer OR agreement measurement | 157,863 | Malformed boolean: the OR terms were not bracketed |
| penile length ultrasound children | 79 | Mostly fetal; replaced by B9 |
| penile length reproducibility | 135 | Not age-restricted; replaced by B8 |
| stretched penile length examiner OR observer OR measurer experience | 4,987,602 | Malformed boolean |
| stretched penile length AND (examiner OR observers OR experience OR trainee) | 193 | Non-specific: "examiner" was expanded to "physical examination" |
| penile length suprapubic fat compression OR depression measurement children | 26,998 | Malformed boolean; replaced by B12 |

## Related articles (find_related_articles)

| Seed PMID | Links screened | New unique |
|---|---|---|
| 39691923 (Goel 2024, SPLINT reliability) | top 40 | |
| 24931740 (Matsuo 2014) | top 40 | |
| **Both seeds** | 80 | **44** |

Most of the 44 new records were reliability studies of unrelated measurements (spine, hip, imaging). Six were newborn penile normative studies. None reported a penile-length reliability metric.

## Citation chasing (from the Goel 2024 SPLINT review, PMC11521232)

- Boas 2006 (PMID 16382001): the inter- and intra-observer figures appear only in the review. They are entered as secondary.
- Al-Herbish 2002 (PMID 11938424): the abstract has no reliability values.
- Ozbey (syringe method): no PubMed record was found with the query above.
- Gabrich 2007 (apparent vs real length): abstract only.

## Flow

- Records identified: 330 unique (286 from B1–B12 plus 44 from related articles). Metadata were retrieved for all 330.
- Title/abstract screened: 330.
- Excluded at title/abstract: 292. The main reasons were:
  - hypospadias surgery and penile curvature
  - urethral length
  - anogenital distance only
  - fetal sonography
  - adult surgery, prosthesis or Peyronie's disease
  - normative SPL data without any reliability or technique-comparison content
  - non-penile reliability studies (from related articles)
- Eligibility assessed in depth: 38.
  - Full text retrieved from PMC: 8 (Goel 2024; Righi 2026; Goel 2024 SPLINT review; Habous 2017; Roy 2019; Bhat 2015; Thankamony 2013; Romano-Riquer 2007, whose PMC record returned empty text).
  - Abstract only: 30.
- **Included: 18.**

## Exclusions at eligibility (n = 20)

| PMID | Study | Reason |
|---|---|---|
| 40819658 | Krämmer 2025 | Bland–Altman compares measurements at birth vs follow-up (growth), not observer agreement |
| 24316680 | Thankamony 2013 | Full text; triplicate caliper readings averaged, but no reliability statistic |
| 11938424 | Al-Herbish 2002 | Reliability computed in a 10% subsample per the review, but no values available |
| 21682766 | Cinaz 2011 | Duplicate readings by one investigator, but no metric |
| 32396926 | Shah 2020 | Standardised technique, but no metric in the abstract |
| 27424616 | Elusiyan 2016 | Digital caliper, but no metric |
| 42287854 | Goel 2026 | Two observers, but no agreement metric in the abstract |
| 9767514 | Tuladhar 1998 | Single examiner; no metric |
| 34283215 | Mancini 2021 | New non-stretch method, but no agreement statistics in the abstract (used in P3) |
| 38454829 | Lee 2024 | Technique description only (used in P3) |
| 33660450 | Ergashev 2021 | Technique description only (used in P3) |
| 22733627 | Sharony 2012 | Fetal ultrasound vs postnatal |
| 42247184 | Hata 2026 | Fetal |
| 22714795 | Danon 2012 | Fetal |
| 12187548 | Harding 2002 | Adult self-measured erect length with paper strips (test–retest r = .60) |
| 25824881 | Sathyanarayana 2015 | Penile width, not length |
| 41104616 | Kroon 2025 | Testicular ultrasound |
| 15665508 | Fok 2005 | Normative newborn data, no reliability content |
| 21980812 | Akin 2011 | Normative newborn data, no reliability content |
| 30068977 | Yafi 2018 | Adult flaccid-to-erect predictors; not added beyond B16–B18 |

## Notes

- Several included values are derived and labelled as such in `notes`:
  - Matsuo 2014 point LoA and SD of differences, from the 95% CIs of the limits.
  - Boas 2006 implied SD of differences.
  - Akyüz 2020 and Smith 1995 between-method differences.
  - Smith 1995 mm→cm conversion.
- Goel 2024 Table 3 cells are quoted with the cells joined by spaces.
- No paediatric study comparing stretched with erect length was found.
- No paediatric study reporting SPL with vs without fat-pad depression by BMI group was found.
