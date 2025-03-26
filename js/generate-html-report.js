
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
async function generateHTML(templatePath, dataPath, outputPath) {
    console.log(`Generating HTML with template: ${templatePath}`);
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
}

module.exports = { generateHTML };