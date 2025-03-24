/**
 * PDF Generator Script for CardWatch Reporting API
 * 
 * This script uses Puppeteer to generate high-quality PDFs with JavaScript-rendered charts.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

/**
 * Generate a PDF report using HTML template and data
 * 
 * @param {string} templatePath - Path to HTML template
 * @param {string} dataPath - Path to JSON data file
 * @param {string} outputPath - Path where PDF will be saved
 * @returns {Promise<string>} - Path to generated PDF
 */
async function generatePDF(templatePath, dataPath, outputPath) {
    console.log(`Generating PDF with template: ${templatePath}`);
    console.log(`Using data from: ${dataPath}`);
    console.log(`Output will be saved to: ${outputPath}`);
    
    // Ensure output directory exists
    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Load data from JSON file
    let data;
    try {
        const dataStr = fs.readFileSync(dataPath, 'utf8');
        data = JSON.parse(dataStr);
        console.log('Data loaded successfully');
    } catch (error) {
        console.error('Error loading or parsing data:', error);
        throw new Error(`Failed to load or parse data: ${error.message}`);
    }
    
    // Load HTML template
    let htmlTemplate;
    try {
        htmlTemplate = fs.readFileSync(templatePath, 'utf8');
        console.log('Template loaded successfully');
    } catch (error) {
        console.error('Error loading template:', error);
        throw new Error(`Failed to load template: ${error.message}`);
    }
    
    // Replace placeholder with data
    const htmlWithData = htmlTemplate.replace(
        '/* DATA_PLACEHOLDER */',
        `const reportData = ${JSON.stringify(data)};`
    );
    
    // Write to temporary HTML file
    const tempPath = `${outputPath}.html`;
    try {
        fs.writeFileSync(tempPath, htmlWithData);
        console.log(`Temporary HTML file created at: ${tempPath}`);
    } catch (error) {
        console.error('Error creating temporary HTML file:', error);
        throw new Error(`Failed to create temporary HTML file: ${error.message}`);
    }
    
    // Launch browser and generate PDF
    let browser;
    try {
        console.log('Launching browser...');
        
        // Try to detect Chrome executable path
        let executablePath;
        try {
            if (process.env.PUPPETEER_EXECUTABLE_PATH) {
                executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
                console.log(`Using Chrome from environment variable: ${executablePath}`);
            } else {
                // Common locations based on OS
                const possiblePaths = [
                    '/usr/bin/chromium',
                    '/usr/bin/chromium-browser',
                    '/usr/bin/chrome',
                    '/usr/bin/google-chrome',
                    '/usr/bin/google-chrome-stable'
                ];
                
                // Check if any of these paths exist
                for (const browserPath of possiblePaths) {
                    try {
                        if (fs.existsSync(browserPath)) {
                            executablePath = browserPath;
                            console.log(`Found Chrome at: ${executablePath}`);
                            break;
                        }
                    } catch (err) {
                        // Continue to next path
                    }
                }
            }
        } catch (e) {
            console.log(`Could not determine Chrome path: ${e.message}`);
            console.log('Will use default chromium path');
        }

        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ],
            executablePath: executablePath,
            ignoreHTTPSErrors: true
        });
        
        const page = await browser.newPage();
        console.log(`Navigating to temporary HTML file: ${tempPath}`);
        await page.goto(`file://${path.resolve(tempPath)}`, {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        
        // Simple wait to ensure everything is loaded
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Wait for charts to render
        console.log('Waiting for charts to render...');
        try {
            // Wait for Charts.js to render
            await page.waitForFunction('window.chartsRendered === true', {
                timeout: 20000
            });
            
            // Extra wait to ensure high-quality rendering 
            console.log('Charts rendered, waiting for final styling...');
            await page.waitForTimeout(2000);
            
            // Take a screenshot to force render completion
            await page.screenshot({ path: `${tempPath}.debug.png`, fullPage: true });
            
            console.log('Charts rendered successfully');
        } catch (error) {
            console.warn('Warning: Timed out waiting for charts to render. Continuing with PDF generation.');
        }
        
        // Use Tabloid dimensions for better chart rendering
        await page.setViewport({
            width: 1056,  // Tabloid width in pixels at 96 DPI (11 inches)
            height: 1632, // Tabloid height in pixels at 96 DPI (17 inches)
            deviceScaleFactor: 1.5, // Balanced resolution for quality
            isMobile: false
        });
        
        // Generate PDF with tabloid settings
        console.log('Generating PDF with tabloid settings...');
        await page.pdf({
            path: outputPath,
            format: 'tabloid', // Use tabloid format (11x17 inches)
            printBackground: true,
            margin: {
                top: '0.75in',
                right: '0.75in',
                bottom: '0.75in',
                left: '0.75in'
            },
            scale: 1.0, // Default scale to match HTML
            preferCSSPageSize: true // Use CSS page size for better control
        });
        
        console.log(`PDF generated successfully at: ${outputPath}`);
        return outputPath;
    } catch (error) {
        console.error('Error generating PDF:', error);
        throw new Error(`Failed to generate PDF: ${error.message}`);
    } finally {
        // Cleanup
        if (browser) {
            console.log('Closing browser...');
            await browser.close();
        }
        
        // Remove temporary HTML file
        try {
            fs.unlinkSync(tempPath);
            console.log('Temporary HTML file removed');
            
            // Remove screenshot debug file if it exists
            const debugImage = `${tempPath}.debug.png`;
            if (fs.existsSync(debugImage)) {
                fs.unlinkSync(debugImage);
                console.log('Debug screenshot removed');
            }
        } catch (error) {
            console.warn(`Warning: Could not remove temporary files: ${error.message}`);
        }
    }
}

// If called directly from command line
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length < 3) {
        console.error('Usage: node pdf-generator.js <template> <data> <output>');
        process.exit(1);
    }
    
    const templatePath = args[0];
    const dataPath = args[1];
    const outputPath = args[2];
    
    generatePDF(templatePath, dataPath, outputPath)
        .then(path => {
            console.log(`PDF generation complete. File saved to: ${path}`);
            process.exit(0);
        })
        .catch(err => {
            console.error('PDF generation failed:', err);
            process.exit(1);
        });
}

module.exports = { generatePDF };