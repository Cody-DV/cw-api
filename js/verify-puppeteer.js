/**
 * Verification script for Puppeteer
 * 
 * This script attempts to launch a Puppeteer browser to verify installation
 */

// Try to find Puppeteer in different locations
let puppeteerPath;
try {
  puppeteerPath = require.resolve('puppeteer');
  console.log('Puppeteer found at:', puppeteerPath);
} catch (e) {
  console.log('Could not resolve puppeteer path with require.resolve():', e.message);
  console.log('Trying alternate methods...');

  // List all possible locations
  const possiblePaths = [
    './node_modules/puppeteer',
    '../node_modules/puppeteer',
    '/usr/local/lib/node_modules/puppeteer',
    '/app/node_modules/puppeteer',
    '/app/js/node_modules/puppeteer'
  ];

  for (const path of possiblePaths) {
    try {
      console.log(`Checking if puppeteer exists at: ${path}`);
      require.resolve(path);
      console.log(`Found puppeteer at: ${path}`);
      puppeteerPath = path;
      break;
    } catch (err) {
      console.log(`Not found at ${path}`);
    }
  }
}

(async () => {
  try {
    const puppeteer = require('puppeteer');
    console.log('Puppeteer version:', puppeteer.version());
    
    console.log('Attempting to launch browser...');
    const browser = await puppeteer.launch({
      headless: 'new', 
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
      ]
    });
    
    console.log('Browser launched successfully!');
    
    const page = await browser.newPage();
    console.log('New page created');
    
    await page.setContent('<html><body><h1>Puppeteer Test</h1></body></html>');
    console.log('Set page content');
    
    console.log('Taking screenshot...');
    await page.screenshot({ path: 'test.png' });
    console.log('Screenshot saved to test.png');
    
    await browser.close();
    console.log('Browser closed successfully');
    console.log('Puppeteer verification SUCCESSFUL');
  } catch (error) {
    console.error('Puppeteer verification FAILED:');
    console.error(error);
    process.exit(1);
  }
})();