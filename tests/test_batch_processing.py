from pathlib import Path

import pandas as pd

from batch_processing import DataProcessor


def _sample_transactions():
    valid = {
        "InvoiceNo": "536365",
        "StockCode": "85123A",
        "Description": "Sample product",
        "Quantity": 2,
        "InvoiceDate": "2010-12-01 08:26:00",
        "Price": 5.0,
        "CustomerID": 17850,
        "Country": "United Kingdom",
    }
    duplicate = dict(valid)
    cancelled = {**valid, "InvoiceNo": "C536366"}
    negative_quantity = {**valid, "InvoiceNo": "536367", "Quantity": -1}
    invalid_price = {**valid, "InvoiceNo": "536368", "Price": 0.0}
    missing_customer = {**valid, "InvoiceNo": "536369", "CustomerID": None}
    return pd.DataFrame([
        valid,
        duplicate,
        cancelled,
        negative_quantity,
        invalid_price,
        missing_customer,
    ])


def test_clean_data_removes_invalid_and_duplicate_rows():
    processor = DataProcessor("unused.csv")
    processor.df = _sample_transactions()

    cleaned = processor.clean_data()

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["InvoiceNo"] == "536365"
    assert cleaned.iloc[0]["CustomerID"] == 17850
    assert cleaned.iloc[0]["TotalPrice"] == 10.0


def test_save_cleaned_data_creates_parent_directory(tmp_path):
    processor = DataProcessor("unused.csv")
    processor.df_cleaned = _sample_transactions().iloc[[0]].copy()
    output_path = tmp_path / "nested" / "outputs" / "cleaned.csv"

    saved_path = processor.save_cleaned_data(output_path)

    assert Path(saved_path).is_file()
    saved = pd.read_csv(saved_path)
    assert len(saved) == 1
