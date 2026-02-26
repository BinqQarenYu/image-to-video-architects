const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();

    // Listen to console logs
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));

    // Listen for file chooser properly matching
    const [fileChooser] = await Promise.all([
        page.waitForFileChooser(),
        page.goto('http://localhost:3002/studio'),
        // Small delay to ensure the page loads completely and attaches handlers
        page.waitForSelector('[data-testid="dropzone"]')
    ]).catch(e => {
        console.error('Initial load error:', e);
        return [];
    });

    try {
        console.log("Waiting for dropzone click");

        // We must invoke click manually on the input element because UI click might not propagate properly inside puppeteer headless
        const fileInputElement = await page.$('input[type="file"]');

        const [fileChooserAsync] = await Promise.all([
            page.waitForFileChooser(),
            fileInputElement.evaluate(b => b.click())
        ]);

        console.log("Uploading file");
        await fileChooserAsync.accept(['e:/012A_Github/image-to-video-architects/frontend/public/index.html']);

        // Wait for the upload network request to complete and check response
        console.log("Waiting for API response");
        const response = await page.waitForResponse(response =>
            response.url().includes('/api/upload-images') && response.request().method() === 'POST',
            { timeout: 10000 }
        );

        console.log(`API responded with status: ${response.status()}`);
        const text = await response.text();
        console.log(`API response body: ${text}`);

    } catch (error) {
        console.error("Test failed:", error);
    } finally {
        await browser.close();
    }
})();
