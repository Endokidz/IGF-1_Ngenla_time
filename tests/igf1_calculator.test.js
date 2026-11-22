// Headless checks for the IGF-1 adjustment calculator (index.html).
// Run:  node tests/igf1_calculator.test.js [path/to/index.html]
// Needs Node with Playwright and Chromium. CDN scripts load from the network; to run offline, set
// IGF1_VENDOR_DIR to a folder holding react.production.min.js, react-dom.production.min.js,
// babel.min.js and tailwind.min.css (the same pinned versions), and requests are served from there.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const PAGE = "file://" + path.resolve(process.argv[2] || path.join(__dirname, "..", "index.html"));
const VENDOR = process.env.IGF1_VENDOR_DIR;
let passes = 0, failures = 0;
const check = (name, ok, detail = "") => { ok ? passes++ : failures++; console.log(`  ${ok ? "ok  " : "FAIL"} ${name}${ok || !detail ? "" : "  ->  " + detail}`); };

async function open(browser, timezoneId) {
  const ctx = await browser.newContext({ timezoneId, viewport: { width: 1000, height: 900 } });
  if (VENDOR) {
    const map = [[/react-dom/, "react-dom.production.min.js", "text/javascript"], [/\/react@/, "react.production.min.js", "text/javascript"],
                 [/babel/, "babel.min.js", "text/javascript"], [/tailwind/, "tailwind.min.css", "text/css"]];
    await ctx.route(/^https?:\/\//, (route) => {
      const hit = map.find(([re]) => re.test(route.request().url()));
      if (!hit) return route.abort();
      return route.fulfill({ body: fs.readFileSync(path.join(VENDOR, hit[1])), contentType: hit[2] });
    });
  }
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e).slice(0, 200)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text().slice(0, 200)); });
  await page.goto(PAGE);
  await page.waitForTimeout(1500);   // in-browser Babel compile
  return { page, errors, ctx };
}

async function calc(page, { hours, unit, value }) {
  await page.click("text=Reset").catch(() => {});
  await page.check(unit === "sds" ? "input[name=unit] >> nth=1" : "input[name=unit] >> nth=0");
  await page.fill("#hours", String(hours));
  await page.fill("#measured-value", String(value));
  await page.click("text=Calculate");
  const err = await page.locator("[role=alert]").count() ? await page.locator("[role=alert]").innerText() : null;
  if (err) return { err };
  return { adjusted: await page.locator("[data-k=adjusted]").innerText(), factor: await page.locator("[data-k=factor]").innerText(),
           text: await page.locator("#result").innerText() };
}

(async () => {
  const browser = await chromium.launch();
  console.log("Page boots");
  const { page, errors, ctx } = await open(browser, "Asia/Jerusalem");
  // On the broken page the stray JSX is parsed as loose HTML (a heading appears) while #root stays empty,
  // so require that React mounted the calculator inside #root.
  const rendered = await page.locator("#root h1", { hasText: "IGF-1 Measurement Adjustment Calculator" }).count();
  const rawCode = (await page.locator("body").innerText()).includes("const IGF1Calculator");
  check("React mounted the calculator in #root", rendered === 1);
  check("source code is not shown as page text", !rawCode);
  check("no script errors", errors.length === 0, errors.join(" | "));
  if (!rendered) { await browser.close(); console.log(`\n${passes} passed, ${failures} failed`); process.exit(1); }
  check("reference table shows all 14 intervals", (await page.locator("table tbody tr").count()) === 14);

  console.log("Hours input bounds match the calculation (> 0 and < 168, decimals allowed)");
  const hoursAttrs = await page.$eval("#hours", (el) => ({ min: el.min, max: el.max, step: el.step }));
  check("hours field: min=0, max=168, step=any", hoursAttrs.min === "0" && hoursAttrs.max === "168" && hoursAttrs.step === "any",
        JSON.stringify(hoursAttrs));
  for (const v of ["0.5", "12.5", "167.9"]) {
    await page.fill("#hours", v);
    check(`hours field accepts ${v} without a browser validity error`, await page.$eval("#hours", (el) => el.validity.valid));
  }

  console.log("Hours mode: adjustment table applied");
  // [input, adjusted value shown, adjustment factor shown (null = not checked), reason]
  const cases = [
    [{ hours: 100, unit: "sds", value: -1.5 }, "-1.50 SDS", null, "Day 4 window: no adjustment"],
    [{ hours: 6, unit: "sds", value: -1 }, "0.80 SDS", null, ">0-12 h: +1.8"],
    [{ hours: 12, unit: "sds", value: 0 }, "1.80 SDS", null, "12 h belongs to >0-12 h"],
    [{ hours: 12.1, unit: "sds", value: 0 }, "0.70 SDS", null, "12.1 h belongs to >12-24 h"],
    [{ hours: 50, unit: "ngml", value: 150 }, "120.00 ng/mL", null, ">48-60 h: x0.8"],
    [{ hours: 30, unit: "ngml", value: 200 }, "200.00 ng/mL", null, ">24-36 h: x1.0"],
    [{ hours: 160, unit: "sds", value: -2 }, "-0.40 SDS", null, ">156-<168 h: +1.6"],
    [{ hours: 100, unit: "ngml", value: 200 }, "200.00 ng/mL", "× 1", ">96-108 h: x1.0"],
    [{ hours: 10, unit: "ngml", value: 150 }, "300.00 ng/mL", "× 2", ">0-12 h: x2.0"],
    [{ hours: 30, unit: "sds", value: -1.0 }, "-1.10 SDS", "-0.1", ">24-36 h: -0.1"],
    [{ hours: 12, unit: "ngml", value: 100 }, "200.00 ng/mL", "× 2", "12 h is the upper edge of >0-12 h"],
    [{ hours: 12.5, unit: "ngml", value: 100 }, "130.00 ng/mL", "× 1.3", "12.5 h belongs to >12-24 h"],
    [{ hours: 0.5, unit: "ngml", value: 100 }, "200.00 ng/mL", "× 2", "sub-hour interval is accepted"],
  ];
  for (const [inp, want, wantFactor, why] of cases) {
    const r = await calc(page, inp);
    const ok = r.adjusted === want && (wantFactor === null || r.factor === wantFactor);
    check(`${inp.hours} h, ${inp.value} ${inp.unit} -> ${want}${wantFactor ? ` (${wantFactor})` : ""} [${why}]`, ok,
          r.err || `${r.adjusted} / ${r.factor}`);
  }
  let r = await calc(page, { hours: 100, unit: "sds", value: -1.5 });
  check("Day-4 note shown at 100 h", /optimal 96-108 hour range/.test(r.text || ""));
  r = await calc(page, { hours: 168, unit: "sds", value: 0 });
  check("168 h rejected", /between 0 and 168 hours/.test(r.err || ""));
  r = await calc(page, { hours: 0, unit: "sds", value: 0 });
  check("0 h rejected", /between 0 and 168 hours/.test(r.err || ""));

  console.log("Value entry");
  await page.check("input[name=unit] >> nth=0");
  await page.fill("#measured-value", "");
  await page.type("#measured-value", "-12");
  check("ng/mL field refuses a minus sign", (await page.inputValue("#measured-value")) === "12");
  await page.check("input[name=unit] >> nth=1");
  await page.fill("#measured-value", "1.2");
  await page.click("text=+/-");
  check("SDS +/- button makes the value negative", (await page.inputValue("#measured-value")) === "-1.2");
  await ctx.close();

  console.log("Date/time mode (west and east of UTC; across a DST change)");
  for (const tz of ["America/Los_Angeles", "Asia/Jerusalem"]) {
    const o = await open(browser, tz);
    const p = o.page;
    await p.check("input[name=input-method] >> nth=1");
    await p.fill("#injection-date", "2026-06-10"); await p.fill("#injection-time", "08:00");
    await p.fill("#measurement-date", "2026-06-14"); await p.fill("#measurement-time", "10:00");
    await p.check("input[name=unit] >> nth=1"); await p.fill("#measured-value", "-1");
    await p.click("text=Calculate");
    check(`${tz}: 10 Jun 08:00 -> 14 Jun 10:00 = 98.0 h`, (await p.locator("[data-k=hours]").innerText()) === "98.0 hours");
    await p.fill("#injection-date", "2026-06-14"); await p.fill("#injection-time", "08:00");
    await p.fill("#measurement-date", "2026-06-14"); await p.fill("#measurement-time", "20:00");
    await p.click("text=Calculate");
    check(`${tz}: same-day 08:00 -> 20:00 = 12.0 h`, (await p.locator("[data-k=hours]").innerText()) === "12.0 hours");
    await p.fill("#measurement-time", "07:00");
    await p.click("text=Calculate");
    check(`${tz}: measurement before injection is rejected`, /must be after injection/.test(await p.locator("[role=alert]").innerText()));
    check(`${tz}: no script errors`, o.errors.length === 0, o.errors.join(" | "));
    await o.ctx.close();
  }
  const ny = await open(browser, "America/New_York");   // DST began 8 Mar 2026 at 02:00
  await ny.page.check("input[name=input-method] >> nth=1");
  await ny.page.fill("#injection-date", "2026-03-07"); await ny.page.fill("#injection-time", "12:00");
  await ny.page.fill("#measurement-date", "2026-03-09"); await ny.page.fill("#measurement-time", "12:00");
  await ny.page.fill("#measured-value", "100");
  await ny.page.click("text=Calculate");
  check("New York across DST start: elapsed time is 47.0 h (real hours, not clock hours)", (await ny.page.locator("[data-k=hours]").innerText()) === "47.0 hours");
  await ny.ctx.close();

  // Elapsed time must be real hours, which can move a sample into a different adjustment bin.
  const dstErrors = [];
  const dst = async (tz, inj, meas) => {
    const o = await open(browser, tz);
    const p = o.page;
    await p.check("input[name=input-method] >> nth=1");
    await p.fill("#injection-date", inj[0]); await p.fill("#injection-time", inj[1]);
    await p.fill("#measurement-date", meas[0]); await p.fill("#measurement-time", meas[1]);
    await p.check("input[name=unit] >> nth=0"); await p.fill("#measured-value", "100");
    await p.click("text=Calculate");
    const out = { hours: await p.locator("[data-k=hours]").innerText(), factor: await p.locator("[data-k=factor]").innerText() };
    dstErrors.push(...o.errors);
    await o.ctx.close();
    return out;
  };
  // Israel DST began Fri 27 Mar 2026 at 02:00: 98 clock hours, 97 real hours. (The original parser also got this
  // one right east of UTC, so it guards against regressions; the Los Angeles case below is the one it failed.)
  let d = await dst("Asia/Jerusalem", ["2026-03-26", "08:00"], ["2026-03-30", "10:00"]);
  check("Jerusalem across DST start: 26 Mar 08:00 -> 30 Mar 10:00 = 97.0 h", d.hours === "97.0 hours", d.hours);
  d = await dst("Asia/Jerusalem", ["2026-03-26", "09:30"], ["2026-03-30", "10:00"]);
  check("Jerusalem across DST start: 26 Mar 09:30 -> 30 Mar 10:00 = 95.5 h, ×0.9 (clock hours would give 96.5 h, ×1.0)",
        d.hours === "95.5 hours" && d.factor === "× 0.9", `${d.hours} / ${d.factor}`);
  // US DST began Sun 8 Mar 2026. The original new Date('YYYY-MM-DD') parser read 8 Mar as 7 Mar west of UTC,
  // pulling the DST change out of the interval: 95.5 h (×0.9) instead of 96.5 h (×1.0).
  d = await dst("America/Los_Angeles", ["2026-03-08", "10:30"], ["2026-03-12", "11:00"]);
  check("Los Angeles, injection on DST-start day: 8 Mar 10:30 -> 12 Mar 11:00 = 96.5 h, ×1 (original parser: 95.5 h, ×0.9)",
        d.hours === "96.5 hours" && d.factor === "× 1", `${d.hours} / ${d.factor}`);
  check("DST cases: no script errors", dstErrors.length === 0, dstErrors.join(" | "));

  console.log("Phone width");
  const m = await open(browser, "Asia/Jerusalem");
  await m.page.setViewportSize({ width: 375, height: 800 });
  const sw = await m.page.evaluate(() => document.documentElement.scrollWidth);
  check("no horizontal page scroll at 375 px", sw <= 375, `scrollWidth ${sw}`);
  await m.ctx.close();

  await browser.close();
  console.log(`\n${passes} passed, ${failures} failed`);
  process.exit(failures ? 1 : 0);
})();
