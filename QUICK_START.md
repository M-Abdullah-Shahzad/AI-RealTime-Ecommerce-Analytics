# Quick Start

## 1. Prepare the dataset

Download the Online Retail II CSV separately and place it at:

```text
data/online_retail_II.csv
```

## 2. Install dependencies

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Generate batch analytics

```bash
python batch_processing.py
python visualization.py
python rfm_analysis.py
python churn_model.py
python ai_insights.py
python recommendation.py
```

## 4. Open the dashboard

```bash
streamlit run dashboard.py
```

Open `http://localhost:8501`. The dashboard reads the generated CSV files in `outputs/`; it is a batch dashboard, not a live Kafka dashboard.

## 5. Optional Kafka/Spark demo

Start Kafka, then run these in separate terminals:

```bash
python spark_streaming.py
python producer.py
```

Set `KAFKA_BROKER` to the broker address. The producer replays the cleaned historical transaction rows to Kafka.

## Important note

The current churn label describes historical 90-day inactivity at the end of the dataset. It is not a validated future churn forecast. The README explains this limitation and the reason Recency is excluded from the model inputs.
