/* Optional browser QA. Install Playwright separately; no runtime website dependency. */
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const root = path.resolve(__dirname, '..');

(async () => {
  const browser = await chromium.launch({headless: true});
  try {
    if (process.argv[2] === 'cover') {
      const page = await browser.newPage({viewport: {width:1200,height:1800},deviceScaleFactor:1});
      const svg = await fs.readFile(path.join(root,'assets/cover.svg'),'utf8');
      await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({path:path.join(root,'assets/cover.png')});
      console.log('Rendered cover.png from original SVG.');
      return;
    }
    const base = process.argv[2] || 'http://127.0.0.1:8765';
    const output = path.join(root,'qa-output');
    await fs.mkdir(output,{recursive:true});
    const errors=[];
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    page.on('pageerror',e=>errors.push(e.message));
    page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
    await page.goto(base+'/index.html');
    await page.locator('.hero h1').waitFor();
    await page.screenshot({path:path.join(output,'desktop-home.png'),fullPage:true});
    await page.getByRole('link',{name:'开始阅读 →'}).click();
    await page.getByRole('heading',{level:1}).waitFor();
    const initialTheme=await page.locator('html').getAttribute('data-theme');
    await page.getByRole('button',{name:'切换明暗主题'}).click();
    assert.notEqual(await page.locator('html').getAttribute('data-theme'),initialTheme);
    await page.getByRole('button',{name:'放大字号'}).click();
    assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--font-size').trim()),'19px');
    await page.getByRole('button',{name:'搜索全书'}).click();
    await page.getByRole('searchbox').fill('replay');
    await page.locator('#search-results a').first().waitFor();
    assert.match(await page.locator('#search-status').textContent(),/找到/);
    await page.keyboard.press('Escape');
    await page.goto(base+'/03-codex-turn.html');
    await page.locator('article a[href*="evidence-c01"]').first().click();
    assert.match(page.url(),/26-sources.html#evidence-c01/);
    await page.waitForTimeout(100);
    const evidenceY=await page.locator('#evidence-c01').evaluate(e=>e.getBoundingClientRect().top);
    assert(evidenceY>-10&&evidenceY<180,`Evidence anchor offscreen: ${evidenceY}`);
    await page.goto(base+'/21-recovery.html');
    await page.screenshot({path:path.join(output,'desktop-chapter.png'),fullPage:true});
    await page.evaluate(()=>scrollTo({top:800,behavior:'instant'}));
    await page.waitForTimeout(150);
    await page.reload();
    await page.waitForTimeout(150);
    assert(await page.evaluate(()=>scrollY)>500,'Reading position was not restored');
    await page.goto(base+'/index.html');
    assert(await page.locator('#resume-reading').isVisible(),'Resume link not visible');
    const mobile=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true,reducedMotion:'reduce'});
    mobile.on('pageerror',e=>errors.push(e.message));
    await mobile.goto(base+'/index.html');
    await mobile.getByRole('button',{name:'目录',exact:true}).click();
    assert.equal(await mobile.locator('#menu-button').getAttribute('aria-expanded'),'true');
    await mobile.locator('#sidebar a[href="09-dsh-scheduler.html"]').click();
    await mobile.locator('article img').waitFor();
    assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile document overflows horizontally');
    await mobile.screenshot({path:path.join(output,'mobile-chapter.png'),fullPage:true});
    const nojs=await browser.newContext({javaScriptEnabled:false});
    const plain=await nojs.newPage();
    await plain.goto(base+'/23-lab.html');
    assert((await plain.locator('article').textContent()).includes('OutcomeUnknown'),'Chapter unavailable without JavaScript');
    const download=await page.request.get(base+'/downloads/coding-agent-engineering.epub');
    assert.equal(download.status(),200);
    assert((await download.body()).subarray(0,2).toString()==='PK');
    assert.deepEqual(errors,[]);
    const report={status:'passed',desktop:'1440×1000',mobile:'390×844',checks:['chapter navigation','search','source anchors','theme','font size','reading position','resume link','mobile menu','mobile overflow','no-JavaScript reading','EPUB download','browser errors']};
    await fs.writeFile(path.join(output,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report,null,2));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
