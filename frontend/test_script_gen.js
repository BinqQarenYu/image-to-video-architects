const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();

    // Listen to console logs
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));

    try {
        await page.goto('http://localhost:3002/studio');

        // Wait 3 seconds to let React settle
        await new Promise(r => setTimeout(r, 3000));

        // Print out the HTML to see what is actually rendered
        const html = await page.evaluate(() => document.body.innerHTML);
        console.log("HTML:", html.substring(0, 1500));

    } catch (error) {
        console.error("Test failed:", error);
    } finally {
        await browser.close();
    }
})();
