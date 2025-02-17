import json

MOCK_DATA = {
    "customerData": {
        "id": "A2E3R-8OJYT-UJH5-6HRRD2",
        "healthData": {
            "allergies": [
                {"allergenID": 90210, "allergenName": "Peanut"},
                {"allergenID": 91233, "allergenName": "Honey"},
            ],
            "dietaryNoteList": [
                {
                    "dietaryNote": {
                        "noteType": "Restriction",
                        "conditionType": "Diabetes Type 1",
                        "severity": "High",
                    }
                },
                {
                    "dietaryNote": {
                        "noteType": "Restriction",
                        "conditionType": "Stage 1 hypertension",
                        "severity": "Medium",
                    }
                },
                {
                    "dietaryNote": {
                        "noteType": "Food Modification",
                        "conditionType": "Dysphagia",
                        "severity": "Medium",
                        "otherNote": "Food must be minced",
                    }
                },
            ],
        },
        "foodConsumptionData": [
            {
                "consumptionDateTime": "2024-11-07 08:08:08.000 -5:00",
                "itemData": {
                    "itemID": 90000987,
                    "itemName": "Orange Juice",
                    "itemQty": 2,
                    "recipeID": 90000999,  # not itemID - links with ingredients - USDA DB
                },
            },
            {
                "consumptionDateTime": "2024-11-07 11:08:08.00 -5:00",
                "itemData": {
                    "itemID": 90087612,
                    "itemName": "Char-Grilled Burger",
                    "itemQty": 1,
                    "recipeID": 90087678,
                },
            },
        ],
    }
}


def get_customer_data(id):
    # TODO: Get data from CW customer API call
    return json.dumps(MOCK_DATA)


def get_transactions(id, start_date, end_date):
    # TODO: Query transaction DB to get transactions for a given time window
    pass


def get_nutritional_data(transactions):
    pass


def aggregate_data():
    # TODO: Aggregate the data retrieved from get_customer_data, get_transactions, and get_nutritional_data
    # Results JSON should be as small as possible to reduce tokens send to AI model

    # Load data from cardwatch_food_transaction.json
    with open("data_aggregation/test_data/cardwatch_food_transaction.json", "r") as f:
        transactions = json.load(f)

    # Initialize a dictionary to hold the aggregated data
    aggregated_data = {}

    # Process each transaction
    for transaction in transactions:
        item_name = transaction.get("ItemName")
        if item_name:
            if item_name not in aggregated_data:
                aggregated_data[item_name] = {
                    "total_quantity": 0,
                    "total_calories": 0,
                    "total_fat": 0,
                    "total_protein": 0,
                }

            # Update the total quantity
            aggregated_data[item_name]["total_quantity"] += transaction.get(
                "quantity", 1
            )

            # If recipeData is available, aggregate nutritional information
            recipe_data = transaction.get("recipeData")
            if recipe_data:
                nutrients = recipe_data.get("labelNutrients", {})
                aggregated_data[item_name]["total_calories"] += nutrients.get(
                    "calories", {}
                ).get("value", 0)
                aggregated_data[item_name]["total_fat"] += nutrients.get("fat", {}).get(
                    "value", 0
                )
                aggregated_data[item_name]["total_protein"] += nutrients.get(
                    "protein", {}
                ).get("value", 0)

    # Save the aggregated data to a new JSON file
    output_file = "data_aggregation/test_data/aggregated_summary.json"
    with open(output_file, "w") as f:
        json.dump(aggregated_data, f, indent=4)

    return {"status": "Data aggregated and saved", "file": output_file}
