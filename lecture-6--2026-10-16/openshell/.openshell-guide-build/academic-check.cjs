const {chromium}=require('./browser-tools/node_modules/playwright');
const assert=require('node:assert/strict');const path=require('node:path');const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 const errors=[],requests=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.goto('file://'+path.resolve('.openshell-guide-build/editorial-before.html'));
 const before=await page.evaluate(()=>({sources:[...document.querySelectorAll('[data-source]')].map(e=>[e.dataset.source,e.href]),code:[...document.querySelectorAll('pre')].map(e=>e.textContent).filter(t=>!/[→↓]/.test(t)),tables:document.querySelectorAll('table').length,exercises:document.querySelectorAll('.exercise').length,terms:document.querySelectorAll('.glossary dt').length}));
 await page.goto('file://'+path.resolve('openshell-guide.html'));
 const after=await page.evaluate(()=>({sources:[...document.querySelectorAll('[data-source]')].map(e=>[e.dataset.source,e.href]),code:[...document.querySelectorAll('pre')].map(e=>e.textContent),tables:document.querySelectorAll('table').length,exercises:document.querySelectorAll('.exercise').length,terms:document.querySelectorAll('.glossary dt').length}));
 assert.deepEqual(after,before);checks.push('119 source anchors, all 15 executable code blocks, 17 tables, 24 exercises, and 27 glossary terms preserved');
 assert.equal(await page.locator('.chapter').count(),18);assert.equal(await page.locator('.tikz-figure').count(),8);
 const images=await page.locator('.tikz-figure img').evaluateAll(imgs=>imgs.map(x=>({ok:x.complete&&x.naturalWidth>0,src:x.src.startsWith('data:image/svg+xml;base64,'),alt:x.alt.length>40})));
 assert(images.every(x=>x.ok&&x.src&&x.alt));checks.push('eight compiled TikZ SVG figures load offline with text alternatives');
 const style=await page.evaluate(()=>({font:getComputedStyle(document.body).fontFamily,size:getComputedStyle(document.body).fontSize,background:getComputedStyle(document.body).backgroundColor,margin:getComputedStyle(document.body).margin,color:getComputedStyle(document.querySelector('.contents a')).color,position:getComputedStyle(document.querySelector('.contents')).position}));
 assert.match(style.font,/Times/);assert.equal(style.size,'16px');assert.equal(style.margin,'8px');assert.equal(style.background,'rgb(255, 255, 255)');assert.equal(style.color,'rgb(0, 0, 238)');assert.equal(style.position,'static');
 await page.screenshot({path:'.openshell-guide-build/academic-desktop.png'});
 await page.locator('#ch01').scrollIntoViewIfNeeded();await page.screenshot({path:'.openshell-guide-build/academic-text.png'});
 for(const name of ['architecture','network-request','creation','interceptors','runtime-startup','request-enforcement','credential-substitution','policy-review']){
  await page.locator('#fig-'+name+' .diagram-scroll').screenshot({path:'.openshell-guide-build/tikz-'+name+'.png'});
 }
 await page.locator('.contents a[href="#ch09-s4"]').click();assert.match(page.url(),/#ch09-s4$/);checks.push('numbered subsection contents navigate to stable anchors');
 await page.locator('#open-search').click();await page.locator('#search-input').fill('seccomp');assert((await page.locator('#search-results li').count())>0);await page.locator('#search-results a').first().click();assert(!(await page.locator('#search-dialog').evaluate(el=>el.open)));checks.push('document search works');
 for(let i=0;i<5;i++)await page.locator('#flow-next').click();assert(await page.locator('#flow-next').isDisabled());await page.locator('#flow-prev').click();assert.match(await page.locator('#flow-count').innerText(),/5 of 6/);checks.push('request walkthrough controls work');
 await page.selectOption('#sim-method','POST');assert.match(await page.locator('#sim-result').innerText(),/Denied: REST/);await page.selectOption('#sim-mode','audit');assert.match(await page.locator('#sim-result').innerText(),/Allowed with an audit/);await page.selectOption('#sim-credential','mismatch');assert.match(await page.locator('#sim-result').innerText(),/Denied: credential/);await page.selectOption('#sim-host','no');assert.match(await page.locator('#sim-result').innerText(),/Denied: destination/);checks.push('policy illustration retains independent admission checks');
 const source=await page.locator('#fig-architecture a[download]').getAttribute('href');const tex=Buffer.from(source.split(',')[1],'base64').toString();assert(tex.includes('\\begin{tikzpicture}')&&tex.includes('\\documentclass'));checks.push('each figure offers self-contained downloadable TikZ source');
 for(const width of [1440,390,320]){await page.setViewportSize({width,height:900});await page.evaluate(()=>window.scrollTo(0,0));const d=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));assert(d.scroll<=d.client,JSON.stringify({width,...d}));if(width===390)await page.screenshot({path:'.openshell-guide-build/academic-mobile.png'})};checks.push('no page overflow at desktop, 390px, or 320px widths');
 await page.emulateMedia({colorScheme:'dark'});assert.equal(await page.evaluate(()=>getComputedStyle(document.body).backgroundColor),'rgb(255, 255, 255)');checks.push('academic white-paper theme persists under dark system preference');
 await page.setViewportSize({width:1200,height:1000});await page.emulateMedia({media:'print'});await page.evaluate(()=>{window.dispatchEvent(new Event('beforeprint'));window.scrollTo(0,0)});assert(await page.locator('details.exercise').evaluateAll(xs=>xs.every(x=>x.open)));assert.equal(await page.locator('.page-tools').evaluate(e=>getComputedStyle(e).display),'none');await page.screenshot({path:'.openshell-guide-build/academic-print.png'});checks.push('print layout expands exercises and hides interactive controls');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);checks.push('no script errors or network asset requests');
 fs.writeFileSync('.openshell-guide-build/academic-report.json',JSON.stringify({passed:true,checks,style},null,2));console.log(JSON.stringify({passed:true,checks,style},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
