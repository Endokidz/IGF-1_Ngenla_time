# P2 – Hormonal treatment of micropenis / small penis: search and selection log

- Date of all searches and retrieval: **2026-11-18**
- Source: PubMed (via PubMed MCP tools: `search_articles`, `get_article_metadata`, `get_full_text_article`, `find_related_articles`, `convert_article_ids`). No date limits applied (all years). NCBI E-utilities and other databases (Embase, CENTRAL, Scopus) were not reachable from this environment and were **not** searched.
- Eligibility: primary studies (RCT, cohort, case series n ≥ 3) of hormonal treatment (IM/topical testosterone, DHT, hCG ± FSH, recombinant gonadotropins incl. minipuberty infusion, pulsatile GnRH, letrozole/other) in infants, children or adolescents with CHH/Kallmann, PAIS, 5α-reductase deficiency, isolated micropenis, hypospadias **with small penis**, or DSD, reporting SPL before and after treatment. Excluded: single case reports (and n = 2), adult-only studies, surgical phalloplasty, reviews.
- Operational rule adopted for hypospadias: included only when the study population was selected for small penis / microphallus (e.g. "microphallic hypospadias", "hypospadias and small penis < 2 SD"). Hypospadias series selected only by meatal position or all-comers were excluded and are listed below as flagged records for possible sensitivity analysis.

## 1. Database searches (PubMed)

| # | Query (as entered) | Hits | Retrieved IDs |
|---|---|---|---|
| Q1 | `micropenis testosterone treatment` | 162 | 162 |
| Q2 | `micropenis dihydrotestosterone` | 48 | 48 |
| Q3 | `micropenis hCG` | 62 | 62 |
| Q4 | `recombinant gonadotropins minipuberty congenital hypogonadotropic hypogonadism penile length` | 3 | 3 |
| Q5 | `gonadotropin infusion infancy micropenis` | 3 | 3 |
| Q6 | `topical testosterone penile length children` | 11 | 11 |
| Q7 | `penile growth androgen therapy infants` | 68 | 68 |
| Q8 | `stretched penile length treatment` | 221 | 221 |
| Q9 | `(minipuberty OR infancy OR infant) AND (gonadotropin OR gonadotrophin OR rFSH OR rhLH) AND hypogonadotropic hypogonadism AND (penis OR penile)` | 49 | 49 |
| Q10 | `(micropenis OR "small penis" OR "penile length") AND (letrozole OR "aromatase inhibitor" OR anastrozole)` | 3 | 3 |
| Q11 | `(pulsatile GnRH OR "GnRH pump" OR "gonadotropin-releasing hormone pump") AND (penile OR penis OR micropenis)` | 27 | 27 |
| Q12 | `(hypospadias) AND (preoperative OR "pre-operative") AND (testosterone OR dihydrotestosterone OR hCG) AND (penile length OR penis size OR glans)` | 48 | 48 |
| Q13 | `(micropenis OR "small penis") AND (gonadotropin OR gonadotrophin OR FSH OR LH) AND (treatment OR therapy)` | 123 | 123 |
| Q14 | `("androgen insensitivity" OR "5-alpha reductase" OR "5alpha-reductase" OR SRD5A2) AND (dihydrotestosterone OR testosterone) AND (penile OR penis OR phallus) AND (treatment OR therapy OR gel)` | 87 | 87 |
| Q15 | `(micropenis OR "small penis" OR "penile length") AND (testosterone enanthate OR testosterone cypionate OR "intramuscular testosterone" OR "testosterone gel" OR "transdermal testosterone")` | 37 | 37 |
| Q16 | `(Kallmann OR "hypogonadotropic hypogonadism") AND (micropenis OR "penile length" OR "penile growth") AND (infant OR infancy OR children OR boys OR adolescents)` | 134 | 134 |
| Q17 | Concept search: `(micropenis[tiab] OR microphallus[tiab] OR "small penis"[tiab] OR "penile length"[tiab] OR "penile size"[tiab] OR "penile growth"[tiab] OR "penis size"[tiab] OR "phallic size"[tiab] OR "penile enlargement"[tiab]) AND (testosterone[tiab] OR dihydrotestosterone[tiab] OR androgen[tiab] OR gonadotropin[tiab] OR gonadotropins[tiab] OR gonadotrophin[tiab] OR hCG[tiab] OR letrozole[tiab] OR GnRH[tiab])` | 737 | 737 |
| Q18 | `(minipuberty OR mini-puberty OR "mini puberty") AND (treatment OR therapy OR induction OR replacement) AND (hypogonadotropic OR hypogonadism) AND (boys OR infants OR male)` | 47 | 47 |
| Q19 | `(gonadotropin OR gonadotrophin OR FSH OR hCG) AND (infant OR infants OR neonatal OR "mini-puberty" OR minipuberty) AND (hypogonadotropic OR hypogonadotrophic) AND (testicular descent OR cryptorchidism OR micropenis)` (a date_from=2023 parameter was passed but the tool returned all years, 1967-2026; all 107 screened) | 107 | 107 |
| Q20 | `(dihydrotestosterone OR androstanolone) AND (gel OR transdermal OR percutaneous OR topical) AND (micropenis OR microphallus OR "penile length" OR hypospadias)` | 30 | 30 |
| | **Total hits (Q1-Q20)** | **2007** | |
| | **Unique records after de-duplication** | **1137** | (870 duplicates removed) |

Q17-Q20 were added during the review after it became apparent that Q1-Q16 missed some records (e.g. "microphallus"-only titles such as Choi 1993, PMID 8326617).

## 2. Other methods
- `find_related_articles` run on two seed sets (gonadotropin seeds: 28081535, 36724045, 31240270, 27379168, 39598127; androgen seeds: 37920173, 40813749, 29176021, 15201804, 24235789). The top-ranked ~100 records of each list were taken: **195 unique**, of which **119 were not already in the database set** and were screened.
- Citation checking of two recent reviews retrieved in full: Rhys-Evans 2025 systematic review (PMID 39673783, PMC11913089; 11 included infant gonadotropin studies) and Cammisa 2026 review (PMID 41597141, PMC12840254; 12 studies). Every study with n ≥ 3 named in their tables/text was already identified, except **"Roddick et al."** (cited by Cammisa 2026 with SPL 1.0 ± 0.3 → 3.0 ± 0.4 cm), which could not be located in PubMed (author searches returned only an unrelated review, PMID 39360615). Case reports with n < 3 named in these reviews are ineligible: Main 2002, Bougnères 2008 and Stuckey 2023 were identified and excluded at title/abstract; Sarfati 2015 (n=1) and Alvarez Casaño 2019 (n=2) were not separately retrieved.

## 3. Automated pre-screening (records removed by automation tools; PRISMA 2020 category)
Because per-record title retrieval was limited to 20 records per call, two transparent, reproducible PubMed-executed filters were applied before manual screening:
1. **Concept filter (329 records removed):** records retrieved by Q1-Q16 that do **not** match Q17 (i.e. lack a penile-size term AND a hormone term in title/abstract).
2. **MeSH/publication-type filter (186 records removed):** records matching Q17 that also match `((adult[mh] NOT (infant[mh] OR child[mh] OR adolescent[mh])) OR (animals[mh] NOT humans[mh]) OR (review[pt] NOT case reports[pt]))`, run as two queries (penile-term halves × hormone terms × filter). Records also tagged Case Reports were kept for manual screening. A QC title check of the 83 filtered Q1-Q16 candidates confirmed they were reviews, adult studies or rat/mouse experiments.
- Total removed by automation: **515** (329 + 186). Limitation: records without abstracts and without the concept terms in the title could have been missed by filter 1.

## 4. PRISMA 2020 flow counts

| Stage | Databases (PubMed Q1-Q20) | Other methods (related articles / citations) |
|---|---|---|
| Records identified | 2007 | 195 (119 new) |
| Duplicates removed | 870 | 76 (already in database set) |
| Removed by automation tools | 515 | 0 |
| Records screened (title/abstract) | **622** | **119** |
| Records excluded at title/abstract | 544 (incl. 1 systematic review used only for citation checking) | 119 |
| Reports sought for retrieval | 78 | 0 |
| Reports not retrieved in full (no PMC full text) | 53 | – |
|   of which included as abstract-only (SPL data in abstract) | 13 | – |
|   of which not assessable (no SPL numbers in abstract) | 40 | – |
| Full-text reports assessed for eligibility | **25** | – |
| Full-text reports excluded | 7 | – |
| **Studies included** | **31** (18 full text + 13 abstract-only) | 0 |

- Arms extracted: **39** (arm_extraction.csv); total N across arms reporting n = **739** (arms without n: Nerli 2013 ×2 [cohort total 25], Velásquez-Urzola 1998 ×2 [40 treated overall], Zenaty 2006). N is **not** de-duplicated: several cohorts overlap (see section 8).
- IPD rows: **51** (ipd_extraction.csv) from Lambert 2025 (11), Sheng 2025 (34), Stoupa 2017 (1), Becker 2016 (2), Tack 2023 (3).

## 5. Full-text reports excluded (n = 7)

| PMID | Study | Reason |
|---|---|---|
| 40510958 | Baghel 2025 | hypospadias population not selected for small penis (all-comer hypospadias, 6 months-10 years); IM testosterone propionate; SPL 2.43 ± 0.84 → 3.54 ± 0.54 cm, difference 1.05 ± 0.21 (n = 40) – flagged for possible sensitivity analysis |
| 38520239 | Ali 2024 | proximal hypospadias selected by meatal position, not small penis; IM T (n = 12); SPL 3.058 → 3.9 cm; values reported as mean ± SE – flagged |
| 21976926 | Ahmad 2011 | hypospadias population not selected for small penis (all hypospadias types, 6 months-10 years); IM testosterone – flagged |
| 33953511 | Khokar 2021 | proximal/mid-penile hypospadias not selected for small penis; outcome was degree of hypospadias – flagged |
| 30519672 | Kohva 2018 | no penile length data reported (adolescent CHH, r-hFSH/hCG) |
| 31031332 | Cheng 2019 | no SPL pre/post data; DHT given to 1 prepubertal and 2 postpubertal patients (case-level narrative) |
| 42786427 | Aouchiche 2026 | gonadotropin therapy given to 7 CHH infants but no SPL before/after treatment reported in full text |

## 6. Included studies (31)
Full text (18): Mesas-Aróstegui 2024 (39598127); Harada 2025 (40813749); Wang 2025 (40099791); Karrou 2023 (37920173); Avril 2023 (36724045); Papadimitriou 2019 (31240270); Kohva 2019 (31067328); Lambert 2016 (27379168); Nerli 2013 (24235789); Kim 2011 (22111055); Agarwal 2020 (35187206); Liu 2021 5ARD (34938965); Liu 2021 CHH adolescents (33813517); Wen 2023 (37313883); Lambert 2025 (40042209); Sheng 2025 (41225491); Wen 2026 (41504504); Tack 2023 (39659563).
Abstract-only (13): listed in section 7b.

## 7a. Reports sought but not retrieved (no PMC full text; abstract lacked extractable SPL data) – n = 40

| PMID | Reason / content |
|---|---|
| 42386451 | hypospadias preop IM T; SPL increase stated; no PMC, no numbers in abstract |
| 41442431 | adolescent HH gonadotropin vs TRT; SPL increased; no PMC, no numbers in abstract |
| 39210488 | pulsatile GnRH 45 CHH males (age not stated, fertility outcomes); no PMC; no SPL numbers in abstract |
| 38981692 | CHH infants GnRH pump or hCG+hMG n=8; PL increased; no PMC, no PL numbers in abstract |
| 36216557 | 5ARD n=4, IM T then DHT in infancy, SPL; no PMC; no SPL numbers in abstract |
| 33894111 | CHH cryptorchidism beyond infancy n=6 (paediatric to postpubertal) hMG+hCG; SPL only as % increase; no PMC |
| 27321554 | hypospadias RCT topical testosterone propionate vs estradiol vs placebo; SPL increase stated without numbers; no PMC |
| 27051040 | 46,XY DSD micropenis DHT gel n=76 (genetics + safety); SPL numbers not in abstract; no PMC |
| 24432625 | Kallmann 12 males (ages not stated; 3 treated for sterility) hCG+hMG+TU; penile length improvement without numbers; no PMC |
| 22412043 | PAIS 14 males longitudinal; penile response to pubertal androgen in some; no numbers; no PMC |
| 21964959 | idiopathic 46,XY DSD (severe hypospadias+microphallus) n=19; early T increased length (no numbers); no PMC |
| 18989681 | RCT topical vs parenteral T in microphallic hypospadias n=21; no numbers in abstract; no PMC |
| 16450457 | letter: topical testosterone in idiopathic micropenis; no abstract; no PMC |
| 15055348 | congenital gonadotropin deficiency boys n=19 (9 micropenis); T restored length (no numbers); no PMC |
| 11992480 | case series n=3 micropenis poor response to hCG and T; no numbers; no PMC |
| 11285063 | topical 5% testosterone ointment n=50; abstract reports systemic effects only, no SPL numbers; no PMC |
| 10999816 | AIS kindred n=4 (3 brothers+uncle) testosterone response; no numbers; no PMC |
| 10492232 | proximal hypospadias + severe chordee hCG n=12; length change only as % in abstract; no PMC |
| 10228293 | CHH n=8 IM TE in infancy/childhood; adult outcome; post-course SPL not in abstract; no PMC |
| 9826209 | Robinow syndrome; hCG 4 weeks in 3 boys increased penile length (no numbers); no PMC |
| 9033786 | 46,XY DSD small penis n=6; low- vs high-dose testosterone heptylate test; no numbers (French); no PMC |
| 8606628 | 5ARD n=16; prepubertal T and/or DHT doubled penis size (no numbers); no PMC |
| 8326617 | transdermal DHT gel in 22 patients with microphallus; change only as % increase rate; no PMC |
| 7441936 | micropenis series III (n=28; 11 received androgen); no numbers; no PMC |
| 7382242 | micropenis series II HH (n=14; 5 received androgen); adult SDS only; no PMC |
| 7361738 | topical 5% testosterone cream in 5 boys with hypopituitarism and microphallus; no numbers; no PMC |
| 7081859 | hypospadias with penile hypoplasia; hCG (37) vs 2% testosterone cream (39); no numbers (Spanish); no PMC |
| 6860874 | microphallic hypospadias topical testosterone cream n=7; no numbers; no PMC |
| 6497555 | micropenis transcutaneous TP vs IM TE; no numbers (French); no PMC |
| 6497554 | penile hypoplasia (16 micropenis, 21 hypospadias) IM testosterone x3; no numbers (French); no PMC |
| 4826635 | letter on testosterone and micropenis; no abstract; no PMC |
| 4717581 | testosterone for micropenis in early childhood; no abstract; no PMC |
| 3166693 | micropenis testosterone cyclopentylate; no abstract (Spanish); no PMC |
| 3017038 | 17bHSD deficiency infants n=7 IM TE courses; penile size normalized (no numbers); no PMC |
| 1202720 | topical 5% testosterone cream in 3 prepubertal boys; no numbers; no PMC |
| 1185416 | congenital hypopituitarism 4 cases (3 treated IM TE; phallic growth, no numbers); no PMC |
| 894812 | micropenis series n=34, therapies resulting in growth (no numbers); no PMC |
| 862205 | isolated gonadotropin deficiency boys 3-20 y androgen therapy; penile length (no numbers); no PMC |
| 660741 | HH micropenis n=5 hCG then topical 10% T; % change only; mixed pre/postpubertal; no PMC |
| 91775 | microphallus n=14 IM TE 1-2 courses; penile size normalized (no numbers); no PMC |

## 7b. Reports without PMC full text, included as abstract-only (SPL data in abstract) – n = 13

| PMID | Content |
|---|---|
| 39039878 | oral testosterone undecanoate in PAIS; SPL pre/post in abstract (Liu 2024) |
| 31178538 | 5ARD n=4 transdermal DHT; median SPL pre/post in abstract (Sasaki 2019) |
| 29176021 | DHT gel n=23 idiopathic micropenis; SPL mean ± SD in abstract (Xu 2017) |
| 28081535 | CHH/panhypopituitarism/PAIS infants rhLH+rhFSH SC infusion n=6; SPL mean ± SD in abstract (Stoupa 2017) |
| 26352087 | PAIS n=3 topical DHT case series (2 paediatric with SPL in abstract; 1 adult excluded) (Becker 2016) |
| 25894960 | RCT oral TU in microphallic hypospadias; change mean ± SD in abstract (Chen 2015) |
| 17095345 | bilateral anorchia; testosterone; SPL gain in SDS (mean ± SD); n treated not stated (Zenaty 2006) |
| 15379413 | micropenis suboptimal responders to T (n=20); median SPL SDS pre/post (Husmann 2004) |
| 15201804 | IM TE 25 mg micropenis n=53; median PL/SDS pre/post (Ishii 2004) |
| 12721732 | hypospadias with small penis, IM TE 25 mg x3, n=25; mean ± SD pre/post (Luo 2003) |
| 12596107 | hypospadias + small penis, topical vs IM testosterone (13 each); means pre/post (Chalapathi 2003) |
| 11910204 | DHT gel n=6 micropenis variable aetiology; range of increase (Charmandari 2001) |
| 9759289 | penile hypoplasia isolated vs with hypospadias; IM testosterone heptylate; SDS gain mean ± SD per group (French) (Velásquez-Urzola 1998) |

## 7c. Title/abstract exclusions flagged for possible sensitivity analysis (not included; listed for transparency)

| PMID | Reason |
|---|---|
| 42145763 | case report n=2 (pulsatile GnRH siblings) |
| 40177735 | population 47,XXY infants not selected for micropenis/small penis (RCT, T cypionate) |
| 35670320 | case report n=2 (LHCGR brothers, TE) |
| 33060765 | case report n=2 siblings (TE and DHT) |
| 31737857 | population 47,XXY infants not selected for micropenis/small penis (T vs untreated; SPL secondary outcome) |
| 20350750 | hypospadias not selected for small penis (baseline PL -1.16 SD); IM TE; abstract has change data (Ishii 2010) |
| 18381569 | case report n=2 (rLH+rFSH pump neonates; same group as Lambert 2016) (Bougnères 2008) |
| 11751071 | single case report (rhFSH+rhLH infant) (Main 2002) |
| 3656564 | hypospadias/epispadias/fistula not selected for small penis; IM TE; mean change only (Gearhart 1987) |
| 1871911 | hypospadias not selected for small penis (testosterone ointment n=15); no numbers (Sakakibara 1991) |
| 28111208 | distal hypospadias RCT with micropenis explicitly excluded (not small-penis population); no PMC (Menon 2017) |

## 8. Suspected overlapping cohorts (do not pool together without de-duplication)
- **Bicêtre/Paris rhLH+rhFSH pump programme:** Bougnères 2008 (n=2, excluded) ⊂ Lambert 2016 (n=8) and Lambert 2025 (n=11, same unit, patients treated from 2008) and Avril 2023 pump group (n=18, Bicêtre + Robert-Debré 2004-2019). Use one (Lambert 2025 has IPD).
- **Beijing Children's Hospital (BCH) 5ARD:** Liu 2021 (oral TU, n=90, 2009-2020) and Wen 2023 (PHS with oral TU, n=60, 2007-2021).
- **BCH PAIS:** Liu 2024 (oral TU, abstract-only) and Wen 2026 (PHS with oral TU, n=25, 2007-2023).
- **BCH hypospadias:** Chen 2015 (microphallic hypospadias, oral TU) – possible partial overlap with BCH DSD cohorts.
- **Robert-Debré, Paris:** Velásquez-Urzola 1998 and Zenaty 2006 (anorchia) – possible partial overlap.
- **Data-integrity concern:** Nerli 2013 (India) and Kim 2011 (Korea) report identical penile-measurement methods text and identical testicular-volume results (5.45 → 6.83 cc left; 5.53 → 7.03 cc right).

## 9. Notes on data availability
- PMC full texts returned by the tool omitted tables for several articles (Mesas-Aróstegui 2024, Avril 2023, Kohva 2019, Lambert 2016, Nerli 2013, Wang 2025 supplementary table). Their per-patient or tabulated SPL values could not be extracted and should be taken from the publisher PDFs.
- Lambert 2025 (Table 4) and Sheng 2025 (Table 4) per-patient values were extracted; the Sheng 2025 IPD reproduces the published summary (before 2.48 ± 1.07, after 3.32 ± 1.23 cm; n = 32/33 with values).
- Liu 2021 (CHH adolescents) measured penile length erect, not stretched.
