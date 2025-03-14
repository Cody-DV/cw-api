from fpdf import FPDF
import matplotlib
import matplotlib.pyplot as plt
import os
import seaborn as sns

matplotlib.use('Agg')  # Use a non-interactive backend


def generate_pdf_report(input_data):
    print("Input data:", input_data)  # Debugging line
    # Create a PDF instance
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Nutrition Report", ln=True, align="C")

    # Extract nutrition profile from input_data
    nutrition_profile = input_data.get("nutrition_profile", {})

    # Add Calories Section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Calories", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    calories = nutrition_profile.get("calories", {})
    eaten = calories.get("eaten", 'na')
    target = calories.get("target", 'na')
    if eaten != 'na' and target != 'na':
        create_chart("calories", float(eaten), float(target))
        if os.path.exists("calories.png"):
            pdf.image("calories.png", x=10, y=None, w=100)
            print("Added calories chart to PDF")  # Debugging line
            os.remove("calories.png")
        else:
            print("Calories chart not found")  # Debugging line
    else:
        pdf.cell(200, 10, txt="Data not available", ln=True, align="L")

    # Add Macronutrients Section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Macronutrients", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    macronutrients = nutrition_profile.get("macronutrients", {})
    for nutrient, values in macronutrients.items():
        percentage = values.get("percentage", 'na')
        target_range = values.get("target_range", 'na')
        if percentage != 'na' and target_range != 'na':
            create_chart(nutrient, float(percentage), float(target_range))
            if os.path.exists(f"{nutrient}.png"):
                pdf.image(f"{nutrient}.png", x=10, y=None, w=100)
                print(f"Added {nutrient} chart to PDF")  # Debugging line
                os.remove(f"{nutrient}.png")
            else:
                print(f"{nutrient} chart not found")  # Debugging line
        else:
            pdf.cell(200, 10, txt=f"{nutrient.capitalize()} data not available", ln=True, align="L")

    # Add Food Consumed Section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Food Consumed", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    food_consumed = nutrition_profile.get("food_consumed", [])
    for meal in food_consumed:
        pdf.cell(200, 10, txt=f"Meal: {meal.get('meal', 'Unknown')} at {meal.get('time', 'Unknown')}", ln=True, align="L")
        for item in meal.get("items", []):
            pdf.cell(200, 10, txt=f"  - {item.get('food', 'Unknown')}: {item.get('quantity', 'Unknown')}", ln=True, align="L")

    # Add Food Group Recommendations Section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Food Group Recommendations", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    food_groups = nutrition_profile.get("food_group_recommendations", {})
    for group, values in food_groups.items():
        eaten = values.get("eaten", 'na')
        target = values.get("target", 'na')
        if eaten != 'na' and target != 'na':
            create_chart(group, float(eaten), float(target))
            if os.path.exists(f"{group}.png"):
                pdf.image(f"{group}.png", x=10, y=None, w=100)
                print(f"Added {group} chart to PDF")  # Debugging line
                os.remove(f"{group}.png")
            else:
                print(f"{group} chart not found")  # Debugging line
        else:
            pdf.cell(200, 10, txt=f"{group.replace('_', ' ').capitalize()} data not available", ln=True, align="L")

    # Add Nutrient Intake Section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Nutrient Intake", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    nutrient_intake = nutrition_profile.get("nutrient_intake", {})
    for nutrient, values in nutrient_intake.items():
        if isinstance(values, dict):
            eaten = values.get("eaten", 'na')
            target = values.get("target", 'na')
            if eaten != 'na' and target != 'na':
                create_chart(nutrient, float(eaten), float(target))
                if os.path.exists(f"{nutrient}.png"):
                    pdf.image(f"{nutrient}.png", x=10, y=None, w=100)
                    print(f"Added {nutrient} chart to PDF")  # Debugging line
                    os.remove(f"{nutrient}.png")
                else:
                    print(f"{nutrient} chart not found")  # Debugging line
            else:
                pdf.cell(200, 10, txt=f"{nutrient.capitalize()} data not available", ln=True, align="L")
        else:
            pdf.cell(200, 10, txt=f"{nutrient.capitalize()} data not available", ln=True, align="L")

    # Add Summary Section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Summary", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    summary = input_data.get("summary", {})
    for key, value in summary.items():
        pdf.multi_cell(0, 10, txt=f"{key.capitalize()}: {value}")

    # Output the PDF
    pdf.output("report.pdf")
    return {"status": "Report generated", "file": "report.pdf"}


def create_chart(nutrient, consumed, target):
    print(f"Generating chart for {nutrient}: Consumed={consumed}, Target={target}")  # Debugging line
    # Create a bar chart using seaborn
    categories = ['Consumed', 'Target']
    values = [consumed, target]

    plt.figure(figsize=(5, 3))
    sns.barplot(x=categories, y=values, palette='pastel')
    plt.title(f"{nutrient.capitalize()} Consumption")
    plt.ylabel('Amount')
    plt.savefig(f"{nutrient}.png")
    print(f"Chart saved as {nutrient}.png")  # Debugging line
    plt.close()