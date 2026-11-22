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

  console.log("Hours mode: adjustment table applied");
  const cases = [
    [{ hours: 100, unit: "sds", value: -1.5 }, "-1.50 SDS", "Day 4 window: no adjustment"],
    [{ hours: 6, unit: "sds", value: -1 }, "0.80 SDS", ">0-12 h: +1.8"],
    [{ hours: 12, unit: "sds", value: 0 }, "1.80 SDS", "12 h belongs to >0-12 h"],
    [{ hours: 12.1, unit: "sds", value: 0 }, "0.70 SDS", "12.1 h belongs to >12-24 h"],
    [{ hours: 50, unit: "ngml", value: 150 }, "120.00 ng/mL", ">48-60 h: x0.8"],
    [{ hours: 30, unit: "ngml", value: 200 }, "200.00 ng/mL", ">24-36 h: x1.0"],
    [{ hours: 160, unit: "sds", value: -2 }, "-0.40 SDS", ">156-<168 h: +1.6"],
  ];
  for (const [inp, want, why] of cases) {
    const r = await calc(page, inp);
    check(`${inp.hours} h, ${inp.value} ${inp.unit} -> ${want} (${why})`, r.adjusted === want, r.err || r.adjusted);
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
