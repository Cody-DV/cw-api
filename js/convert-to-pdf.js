const puppeteer = require('puppeteer');
const path = require('path');


async function convertToPDF(htmlPath) {
    
    // Launch Chromium
    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox'
          ]
    });

    console.log("HTML PATH: ", htmlPath)

    const page = await browser.newPage();

    const absoluteHtmlPath = path.resolve(htmlPath); 
    const baseName = path.basename(absoluteHtmlPath, '.html');
    const dirName = path.dirname(absoluteHtmlPath);
    const pdfFileName = `${baseName}.pdf`;
    const pdfPath = path.join(dirName, pdfFileName);

    const fileUrl = 'file://' + absoluteHtmlPath;
    await page.goto(fileUrl, {
        waitUntil: 'networkidle0',
    });

    await page.emulateMediaType('screen');

    // Save the PDF
    await page.pdf({
        path: pdfPath,
        printBackground: true,
        preferCSSPageSize: true,
        margin: {
            top: '0.25in',
          },
    });

    // Close Chromium
    await browser.close();
}

// If called directly from command line
if (require.main === module) {
    
    if (process.argv.length < 3) {
        console.error('Please provide an HTML file or URL as the first argument');
        process.exit(1);
    }

    const htmlPath = process.argv[2];
    console.log("HTML PATH: ", htmlPath)
    
    convertToPDF(htmlPath)
        .then(path => {
            console.log(`PDF generation complete. File saved to: ${path}`);
            process.exit(0);
        })
        .catch(err => {
            console.error('PDF generation failed:', err);
            process.exit(1);
        });
}

module.exports = { convertToPDF }