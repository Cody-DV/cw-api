from fpdf import FPDF

# TODO: Use templating to make PDFs consistent with what dietitians expect


def generate_pdf_report(input_data):
    # Implement PDF report generation logic
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Report", ln=True, align="C")
    # Add more content to the PDF
    # Extract nutrients and notes from input_data
    nutrients = input_data.get("nutrients", {})
    notes = input_data.get("notes", {})

    # Add Nutrients section
    pdf.cell(200, 10, txt="Nutrients", ln=True, align="L")
    for nutrient, value in nutrients.items():
        pdf.cell(200, 10, txt=f"{nutrient.capitalize()}: {value}", ln=True, align="L")

    # Add a line break
    pdf.ln(10)

    # Add Notes section
    pdf.cell(200, 10, txt="Notes", ln=True, align="L")
    for note_type, note_content in notes.items():
        pdf.multi_cell(
            0, 10, txt=f"{note_type.replace('_', ' ').capitalize()}: {note_content}"
        )
    pdf.output("report.pdf")
    return {"status": "Report generated", "file": "report.pdf"}
