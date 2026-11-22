// Headless regression tests for app/index.html.
// Run from spl_reference_tool/:  node tests/app.test.js
// Expected values are recomputed here from app/model.json with an independent interpolation,
// so a change in the app's arithmetic, input handling or row matching fails loudly.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const ROOT = path.join(__dirname, "..");
const APP = "file://" + path.join(ROOT, "app", "index.html");
const M = JSON.parse(fs.readFileSync(path.join(ROOT, "app", "model.json"), "utf8"));
const C = M.age_model.curve;

function lin(arr, age) { // independent of the app's interp(): bisection on the age grid
  const a = C.age;
  if (age <= a[0]) return arr[0];
  if (age >= a[a.length - 1]) return arr[arr.length - 1];
  let lo = 0, hi = a.length - 1;
  while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (a[mid] <= age) lo = mid; else hi = mid; }
  return arr[lo] + (age - a[lo]) / (a[hi] - a[lo]) * (arr[hi] - arr[lo]);
}
const zAge = (age, spl) => (spl - lin(C.mean, age)) / lin(C.sd, age);
const fz = (z) => (z >= 0 ? "+" : "−") + Math.abs(z).toFixed(2);

let failures = 0, passes = 0;
function check(name, cond, detail = "") {
  if (cond) { passes++; console.log("  ok   " + name); }
  else { failures++; console.log("  FAIL " + name + (detail ? "  ->  " + detail : "")); }
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error" && !/fonts\.(googleapis|gstatic)/.test(m.text())) errors.push(m.text()); });
  await page.goto(APP);

  const set = async (vals) => {
    for (const [id, v] of Object.entries(vals)) {
      const el = page.locator("#" + id);
      const tag = await el.evaluate((e) => e.tagName + ":" + (e.type || ""));
      if (tag.endsWith("checkbox")) { if ((await el.isChecked()) !== !!v) await el.click(); }
      else if (tag.startsWith("SELECT")) await el.selectOption(String(v));
      else await el.fill(String(v));
    }
  };
  const reset = () => set({ ageY: "", ageM: "", ageD: "", stG: "", stPH: "", tv: "", pop: "", spl: "", cPreterm: false, cEarly: false, cObese: false, cFat: true });
  const headlineZ = () => page.locator(".headline .card .v").first().innerText();
  const out = () => page.locator("#out").innerText();
  const tableText = () => page.locator("#tbl tbody").innerText();
  const stageCells = () => page.locator("#tbl tbody tr td:nth-child(5)").allInnerTexts();

  console.log("Boot");
  check("no script errors on load", errors.length === 0, errors.join(" | "));
  check("example values render a z-score", /[+−]\d\.\d\d/.test(await headlineZ()));

  console.log("Pooled age z-score matches an independent calculation from model.json");
  const grid = [[{ ageD: 3 }, 3 / 365.25, 2.6], [{ ageY: 0, ageM: 6 }, 0.5, 3.4], [{ ageY: 2, ageM: 0 }, 2, 4.0],
                [{ ageY: 7, ageM: 3 }, 7.25, 4.1], [{ ageY: 12, ageM: 0 }, 12, 6.0], [{ ageY: 15, ageM: 6 }, 15.5, 9.0], [{ ageY: 17, ageM: 11 }, 17 + 11 / 12, 11.0]];
  for (const [inp, age, spl] of grid) {
    await reset(); await set({ ...inp, spl });
    const got = await headlineZ(), want = fz(zAge(age, spl));
    check(`age ${age.toFixed(3)} y, SPL ${spl} cm: z ${want}`, got === want, `app shows ${got}`);
  }

  console.log("Age input handling");
  await reset(); await set({ ageY: 5, ageM: 0, spl: 4 }); await set({ ageD: 10 });
  check("typing newborn days clears years/months", (await page.inputValue("#ageY")) === "" && (await page.inputValue("#ageM")) === "");
  check("result states the newborn age used", /newborn, 10 days/.test(await out()));
  await reset(); await set({ ageY: 19, spl: 10 });
  check("age > 18 y gives an explicit error", /birth to 18 years/.test(await out()));

  console.log("Pubertal scales are never conflated");
  await reset(); await set({ ageY: 14, ageM: 0, spl: 9, stG: 2 });
  let cells = (await stageCells()).filter((c) => /^(G|PH|TV|Tanner)/.test(c));
  check("G2 entered: stage rows are G2 or system-not-stated only", cells.length > 0 && cells.every((c) => /^G2\b|^Tanner 2 \(system not stated\)/.test(c)), cells.join(" / "));
  await reset(); await set({ ageY: 14, ageM: 0, spl: 9, stPH: 3 });
  cells = (await stageCells()).filter((c) => /^(G|PH|TV|Tanner)/.test(c));
  check("PH3 entered: stage rows are PH3 or system-not-stated only", cells.length > 0 && cells.every((c) => /^PH3\b|^Tanner 3 \(system not stated\)/.test(c)), cells.join(" / "));
  await reset(); await set({ ageY: 14, ageM: 0, spl: 9, tv: 15 });
  cells = (await stageCells()).filter((c) => /^(G|PH|TV|Tanner)/.test(c));
  check("testis 15 mL maps to the source's own class (TV class 3, 12-20 mL)", cells.length > 0 && cells.every((c) => /^TV class 3 \(12-20 mL\)/.test(c)), cells.join(" / "));
  await reset(); await set({ ageY: 14, ageM: 0, spl: 9, tv: 20 });
  check("testis 20 mL is TV class 3 (12-20 mL inclusive)", /TV class 3/.test(await out()));
  await reset(); await set({ ageY: 15, ageM: 0, spl: 9, tv: 25 });
  check("testis 25 mL is TV class 4 (>20 mL)", /TV class 4/.test(await out()));

  console.log("Measurement-concern rule applies to stage references (author decision: shown, not pooled)");
  await reset(); await set({ ageY: 15, ageM: 0, spl: 9, stG: 4 });
  const o = await out();
  const gLine = o.split("\n").find((l) => /^Mean .* from /.test(l)) || "";
  const gSources = (gLine.match(/ from (.*?)(?: \(n =|;)/) || [])[1] || "";
  check("G4 reference does not pool Sotos 2017", gSources && !/Sotos/.test(gSources), "sources: " + gSources);
  check("Sotos 2017 is listed as shown, not pooled", /not pooled \(measurement concern\): .*Sotos/.test(o));
  const g4 = M.stage_model.G.stages["4"];
  check("G4 headline z uses the model's G4 mean/SD", o.includes(fz((9 - g4.mean) / g4.sd)));

  console.log("Duplicate Jaiswal stage rows no longer leak into the age table");
  await reset(); await set({ ageY: 15, ageM: 0, spl: 9 });
  const t15 = await tableText();
  check("no 'Genital stage'/'Pubic hair' rows without a stage entered", !/Genital stage|Pubic hair/.test(t15));

  console.log("Wang/Bhat/Puri: visible but not pooled (author decision 2026-11-22, revised)");
  await reset(); await set({ ageY: 7, ageM: 0, spl: 4.5 });
  const t7 = await tableText();
  check("Wang 2018 and Bhat 2015 rows visible at 7 y", /Wang YN 2018/.test(t7) && /Bhat 2015/.test(t7));
  const wRow = await page.locator("#tbl tbody tr", { hasText: "Wang YN 2018" }).first().innerText();
  check("Wang 2018 row carries the concern flag", /⚠/.test(wRow));
  check("all three are flagged in the model rows (never pooled)", ["Wang2018_CHN", "Bhat2015_IND", "Puri2017_IND"].every((id) => M.rows.filter((r) => r.study === id).length > 0 && M.rows.filter((r) => r.study === id).every((r) => r.concern)));
  check("none of the three is counted in the pooled age model", M.curation.studies_flagged.includes("Wang2018_CHN") && M.curation.studies_flagged.includes("Bhat2015_IND") && M.curation.studies_flagged.includes("Puri2017_IND"));

  console.log("Headline shows age and puberty (author decision 2026-11-22)");
  await reset(); await set({ ageY: 14, ageM: 0, spl: 9 });
  check("no puberty entered: one headline card (age)", (await page.locator(".headline .card").count()) === 1);
  await set({ stPH: 4, tv: 15 });
  const cards = await page.locator(".headline .card").allInnerTexts();
  check("puberty entered: two headline cards, age then puberty", cards.length === 2 && /age reference/i.test(cards[0]) && /puberty reference/i.test(cards[1]), cards.join(" || "));
  check("puberty card uses the best-supported scale (TV class with n reported beats provisional PH)", /TV class 3/i.test(cards[1] || ""), cards[1]);
  const tv3 = M.stage_model.TV.stages["3"];
  check("puberty card z matches the model", (cards[1] || "").includes(fz((9 - tv3.mean) / tv3.sd)));

  console.log("Optional population layer");
  const PMm = M.population_model, idx = (a) => Math.round(a / (C.age[1] - C.age[0]));
  await reset(); await set({ ageY: 7, ageM: 0, spl: 4.5, pop: "WPR" });
  const w = PMm.WPR, i7 = idx(7);
  const oPop = await out();
  check("WPR at 7 y: population block with the model's mean and z", oPop.includes(`Population: ${w.label}`) && oPop.includes(fz((4.5 - w.mean[i7]) / w.sd[i7])));
  const firstRow = await page.locator("#tbl tbody tr").first().innerText();
  check("matched-population rows listed first and marked", /matches selected population/.test(firstRow));
  await reset(); await set({ ageY: 7, ageM: 0, spl: 4.5, pop: "AFR" });
  check("AFR at 7 y: says no regional study covers this age", /No eligible study from this region covers this age/.test(await out()));
  await reset(); await set({ ageD: 2, spl: 2.6, pop: "AFR" });
  const a0 = PMm.AFR;
  check("AFR newborn: pooled from 4 studies with an interval", /Population: Sub-Saharan Africa/.test(await out()) && a0.k_studies[0] === 4 && a0.pi_lo[0] != null);
  await reset(); await set({ ageY: 15, ageM: 0, spl: 7.2, pop: "AMR" });
  check("population z in a different band from age z triggers the disagreement alert", /The references disagree.*Population/s.test(await out()));

  console.log("Safety alerts");
  await reset(); await set({ ageD: 2, spl: 2.4, cPreterm: true });
  check("preterm newborn: critical alert, reference is term-only", /built from term boys only/.test(await out()));
  await reset(); await set({ ageY: 12, ageM: 0, spl: 7 });
  check("> 9 y without puberty data: prompt to enter stage or testis volume", /genital stage, the pubic-hair stage or the testis volume/.test(await out()));
  await reset(); await set({ ageY: 3, ageM: 0, spl: 1.5 });
  check("very low z: second-examiner warning", /second trained examiner/.test(await out()));

  await reset(); await set({ ageY: 15, ageM: 0, spl: 8, stG: 5, stPH: 5, tv: 25 });
  const oDis = await out();
  check("mature boy, age z reassuring but stage z low: 'references disagree' alert", /The references disagree/.test(oDis));
  const firstAlert = await page.locator("#out .alerts").evaluate((e) => !!e.previousElementSibling && e.previousElementSibling.classList.contains("sds"));
  check("alerts sit directly under the headline scale", firstAlert);

  console.log("Methods text is generated from the data");
  const methods = await page.locator("#methods").evaluate((e) => e.textContent);
  check("no stale 'will be added when available' claim", !/will be added when available/.test(methods));
  check("states the current study count", methods.includes(`from ${M.age_model.k_studies} studies`) || methods.includes(`${M.age_model.k_studies} studies`));

  console.log("Layout");
  await page.setViewportSize({ width: 375, height: 800 });
  await reset(); await set({ ageY: 14, ageM: 0, spl: 9, stG: 3, stPH: 3, tv: 15 });
  const sw = await page.evaluate(() => document.documentElement.scrollWidth);
  check("no horizontal page scroll at 375 px", sw <= 375, `scrollWidth ${sw}`);
  check("still no script errors", errors.length === 0, errors.join(" | "));

  await browser.close();
  console.log(`\n${passes} passed, ${failures} failed`);
  process.exit(failures ? 1 : 0);
})();
