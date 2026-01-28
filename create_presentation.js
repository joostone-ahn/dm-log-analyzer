const pptxgen = require('pptxgenjs');
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function html2pptx(htmlFile, pres) {
    console.log(`Processing: ${htmlFile}`);
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.setViewportSize({ width: 960, height: 540 });
    await page.goto(`file://${path.resolve(htmlFile)}`);
    await page.waitForTimeout(500);
    const screenshot = await page.screenshot({ type: 'png' });
    await browser.close();

    const slide = pres.addSlide();
    slide.addImage({
        data: `data:image/png;base64,${screenshot.toString('base64')}`,
        x: 0, y: 0, w: '100%', h: '100%'
    });
    return { slide };
}

async function main() {
    const pres = new pptxgen();
    pres.layout = 'LAYOUT_16x9';
    pres.title = 'LTE/NR Protocol Analyzer';
    pres.author = 'Development Team';
    pres.subject = 'Multi-Format Log Call Flow Visualization Tool';

    const slides = [
        'slides/01-title.html',
        'slides/02-log-formats.html',
        'slides/03-overview.html',
        'slides/04-architecture.html',
        'slides/05-parsing-enhancement.html',
        'slides/06-protocols.html',
        'slides/07-tech-stack.html',
        'slides/08-conclusion.html'
    ];

    for (const slideFile of slides) {
        if (fs.existsSync(slideFile)) {
            await html2pptx(slideFile, pres);
        } else {
            console.log(`Warning: ${slideFile} not found`);
        }
    }

    await pres.writeFile('LTE_NR_Protocol_Analyzer.pptx');
    console.log('\n✅ Presentation created: LTE_NR_Protocol_Analyzer.pptx');
}

main().catch(console.error);
