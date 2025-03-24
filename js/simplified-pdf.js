/**
 * Simplified PDF Generator Script that doesn't rely on Puppeteer
 * 
 * This is a fallback option that uses html-pdf or similar lightweight libraries
 */

const fs = require('fs');
const path = require('path');

/**
 * Generate a PDF from an HTML file using a lightweight approach
 */
async function generateSimplePdf(htmlPath, outputPath) {
  try {
    console.log(`Starting simplified PDF generation from ${htmlPath} to ${outputPath}`);
    
    // Read the HTML file
    const html = fs.readFileSync(htmlPath, 'utf8');
    console.log(`Read HTML file: ${htmlPath}`);
    
    try {
      // Try to use html-pdf if available
      const htmlPdf = require('html-pdf');
      console.log('Using html-pdf library');
      
      // Configure options to avoid Chromium issues
      const options = {
        format: 'A4',
        border: {
          top: '1cm',
          right: '1cm',
          bottom: '1cm',
          left: '1cm'
        },
        // Use a more reliable rendering engine
        type: 'pdf',
        quality: '100',
        // Avoid Phantom/Chrome issues
        phantomPath: null // Force html-pdf to use its default rendering engine
      };
      
      return new Promise((resolve, reject) => {
        htmlPdf.create(html, options).toFile(outputPath, (err, res) => {
          if (err) {
            console.error('Error generating PDF with html-pdf:', err);
            reject(err);
          } else {
            console.log(`PDF created at: ${res.filename}`);
            resolve(outputPath);
          }
        });
      });
    } catch (err) {
      console.log('html-pdf not available, writing HTML file instead');
      
      // Just copy the HTML file with a .pdf extension as last resort
      fs.copyFileSync(htmlPath, outputPath);
      console.log(`Copied HTML to ${outputPath} (not a real PDF)`);
      return outputPath;
    }
  } catch (error) {
    console.error('Error in simplified PDF generation:', error);
    throw error;
  }
}

// If called directly
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.error('Usage: node simplified-pdf.js <html-file> <output-pdf>');
    process.exit(1);
  }
  
  const htmlPath = args[0];
  const outputPath = args[1];
  
  generateSimplePdf(htmlPath, outputPath)
    .then(path => {
      console.log(`Simple PDF generation complete at: ${path}`);
      process.exit(0);
    })
    .catch(err => {
      console.error('Simple PDF generation failed:', err);
      process.exit(1);
    });
}

module.exports = { generateSimplePdf };