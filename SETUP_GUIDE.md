# Setup Guide

## Prerequisites

- Python 3.9+
- Java 11+ for Spark
- Kafka for the optional streaming demo
- Online Retail II CSV downloaded separately

## Dataset

Create a local directory and place the dataset file at:

```text
data/online_retail_II.csv
```

The path can be overridden with `RETAIL_DATASET_PATH`.

## Python environment

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

For notebooks and development tools, install `requirements-dev.txt` as well.

## Environment variables

Copy `.env.example` to `.env` and adjust the dataset and Kafka settings if needed:

- `RETAIL_DATASET_PATH`
- `KAFKA_BROKER`

The scripts use local .env values when present. Process environment variables take precedence.

## Batch execution

```bash
python batch_processing.py
python visualization.py
python rfm_analysis.py
python churn_model.py
python ai_insights.py
python recommendation.py
```

## Dashboard

```bash
streamlit run dashboard.py
```

Open `http://localhost:8501`. Generate the batch output CSV files before starting the dashboard.

## Kafka/Spark demo

Start a Kafka broker and set `KAFKA_BROKER` to its address. Run `python spark_streaming.py` in one terminal, then `python producer.py` in another. The producer offers replay modes for the cleaned transaction file.

The Streamlit dashboard does not currently consume the Kafka/Spark output.
