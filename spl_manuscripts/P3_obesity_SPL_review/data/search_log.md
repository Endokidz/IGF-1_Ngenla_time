# Search log: obesity/adiposity and penile length in children (P3)

- Database: PubMed via the PubMed MCP tools (search_articles, get_article_metadata, get_full_text_article, convert_article_ids, find_related_articles).
- All searches were run on 2026-11-18, with no date limits and default PubMed query translation.
- Extraction file: `obesity_extraction.csv`. It has 37 rows covering 22 studies.

## Pre-specified queries

| # | Query | Hits |
|---|---|---|
| Q1 | obesity penile length children | 24 |
| Q2 | buried penis obese boys | 11 |
| Q3 | concealed penis obesity prevalence | 4 |
| Q4 | stretched penile length BMI | 26 |
| Q5 | pubic fat pad penile length | 11 |
| Q6 | obese adolescents penile size | 10 |
| Q7 | childhood obesity micropenis | 17 |
| Q8 | penile length overweight boys | 16 |
| | **Total (with duplicates) / unique** | **119 / 100** |

## Related articles (find_related_articles, pubmed_pubmed)

Each seed returned 100 ranked links. Only the top-ranked links were screened.

| Seed PMID | Links screened | New unique |
|---|---|---|
| 34283215 (Mancini 2021) | top 40 | |
| 38454829 (Lee 2024) | top 40 | |
| 40787954 (Ma 2025) | top 30 | |
| **All seeds** | 110 | **84** |

## Supplementary queries (2026-11-18)

| Query | Hits | New |
|---|---|---|
| buried penis children obesity | 11 | 6 |
| inconspicuous penis OR hidden penis AND (obesity OR overweight OR body mass index) AND children | 4 | 1 |
| suprapubic fat penile length children | 4 | 2 |
| Camurdan penile length (citation chase from Bhat 2015) | 2 | 1 |
| penile length body mass index adolescents Indonesia (citation chase for Adriansyah, cited in Bhat 2015) | 0 | 0 |
| apparent penile length obese | 1 | 1 |
| prepubic fat penile length | 7 | 5 |

Records also surfaced through the P4 reliability searches (Ishii 2014, Soydan 2012, Joya 2026) were already in the pool.

## Flow

- Records identified: 200 (100 + 84 + 16).
- No PubMed record retrievable: 4 (PMIDs 25905331, 25905393, 32491459, 41343689; get_article_metadata returned "No articles found").
- Title/abstract screened: 196.
- Excluded at title/abstract: 157. The main reasons were:
  - adult acquired buried penis or adult surgery
  - syndromic case reports (Prader-Willi, Bardet-Biedl, Kallmann and similar)
  - adult penile normative data
  - hormonal treatment of micropenis
  - unrelated obesity outcomes
  - animal studies
- Eligibility assessed in depth: 39.
  - Full text retrieved from PMC: 7 (Lee 2024, Ergashev 2021, Roy 2019, Bhat 2015, Oyenusi 2025, Khadilkar 2025, Amirkashani 2025). Lee 2024's discussion was also used as a secondary source for Mancini 2021.
  - Abstract-level only, because there was no PMC full text: 32.
- **Included: 22 studies.**
  - Obese vs normal-weight comparisons: 6. These are A01 Mancini, A02 Lee, A03 Zhang 2013, A04 Zhang 2015, A05 Han, A06 Zhang 1997.
  - Weight-loss intervention: 1 (A07 Ma 2025).
  - Concealed or hidden penis and adiposity: 2 (A08 Ergashev, A09 Storm).
  - Apparent micropenis or buried penis in referral or surgical series: 4 (A10 Khadilkar, A11 Oyenusi, A12 Aslan, A13 Casale).
  - SPL–BMI correlation or regression in general or clinical paediatric samples: 9. These are A14 Camurdan, A15 Fawaz, A16 Ishii, A17 Roy, A18 Bhat, A19 Soydan, A20 Joya, A21 Arian and A22 Amirkashani.

## Exclusions at eligibility (n = 17)

| PMID | Study | Reason |
|---|---|---|
| 36282972 | Hassan 2022 | Obese vs lean adolescents, but no penile length comparison reported in the abstract; no PMC full text |
| 25781529 | Tomova 2015 | Penile length measured by weight class, but no penile results in the abstract; no PMC full text |
| 23729608 | Zhai 2013 | Testicular/"sex organ" volume only; no penile length result |
| 24796931 | Vandewalle 2014 | Genital Tanner staging only |
| 23713062 | De Leonibus 2013 | Puberty timing only |
| 23247617 | Robeva 2012 | Acne-focused; no BMI–penile length analysis |
| 40751588 | Nguyen 2025 | Penile measurements made in adults (prepubertal BMI reconstructed from photos); outside the 0–18 y measurement scope. Potentially useful context: prepubertal obesity vs adult stretched length β = −1.201, P = .05 |
| 17572214 | Borsellino 2007 | Surgical outcome series; obesity reported only among recurrences (3/56, all obese) |
| 40214793 | Yener 2025 | Surgical outcome series; obesity reported only among recurrences (recurrence predominantly in obese) |
| 35610128 | Wahyudi 2022 | Surgical outcome series; obesity reported only as a predictor of oedema |
| 8803305 | Peng 1996 | Surgical outcome series; obesity discussed only qualitatively |
| 24931740 | Matsuo 2014 | Newborn buried-penis prevalence 3.7%, with no adiposity analysis (used in P4) |
| 27550493 | Park 2016 | No BMI analysis in the abstract |
| 21528817 | Kilic 2011 | Gynecomastia study; SPL–BMI not reported |
| 31690265 | Cao 2019 | Hormones only |
| 41809786 | Dick 2026 | Adult bariatric/buried penis |
| 41339234 | Zhang 2025 | Infant concealed penis; no adiposity data |

## Notes

- Numbers were copied only from retrieved abstract or full text. Whitespace was normalised: thin and non-breaking spaces became ordinary spaces.
- Derived values (group n by subtraction, % from counts, before–after change) are labelled "derived" in `notes`.
- Four included studies are Chinese-language articles; only their English abstracts were used: A03, A04, A06, A07.
- Mancini 2021 is abstract-only. Its BMI–correlation result comes only from Lee 2024's discussion, so it is flagged as secondary.
- Ergashev 2021 and Bhat 2015: PMC full text was retrieved, but the table contents were not included in the retrieved text.
