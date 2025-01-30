from data_collection.collector import collect_data


def test_collect_data():
    """Test collect_data function"""
    input_data = {"sample": "data"}
    result = collect_data(input_data)
    assert result["status"] == "Data collected"
    assert result["data"] == input_data
