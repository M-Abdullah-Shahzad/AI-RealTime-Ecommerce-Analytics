# E-commerce Customer Analytics and Streaming Demo

A Python project that explores the Online Retail II transaction dataset through batch analytics, customer segmentation, an exploratory inactivity classifier, market-basket recommendations, and a separate Kafka/Spark streaming demonstration.

This is an educational analytics project, not a production-ready retail platform. The Streamlit dashboard reads generated CSV files; it is **not connected to the Kafka stream**.

## What is implemented

| Component | Implementation |
|---|---|
| Data preparation | Pandas cleaning, validation, and feature creation |
| Exploratory analysis | Sales, product, country, and time-based charts |
| Customer segmentation | RFM metrics and rule-based customer groups |
| Inactivity classification | Scikit-learn Random Forest using customer-level aggregates |
| Business insights | Deterministic rules and descriptive analytics |
| Product recommendations | Apriori frequent itemsets and association rules |
| Event streaming demo | Kafka producer replays cleaned transaction rows |
| Stream processing demo | Spark Structured Streaming consumes Kafka events and calculates windowed aggregates |
| Dashboard | Streamlit views precomputed batch outputs |

## Architecture

### Batch analytics

```text
Online Retail II CSV
        |
        v
batch_processing.py
        |
        v
Cleaned transaction CSV
        |
        +------> visualization.py
        |
        +------> rfm_analysis.py
        |             |
        |             v
        |       churn_model.py
        |             |
        |             v
        |       ai_insights.py
        |
        +------> recommendation.py
                      |
                      v
             outputs/*.csv and charts
                      |
                      v
                dashboard.py
```

### Separate streaming demonstration

```text
Cleaned transaction CSV
        |
        v
producer.py
        |
        v
Kafka topic: retail_orders
        |
        v
spark_streaming.py
        |
        v
Windowed console analytics
```

The streaming consumer currently prints its aggregates; it does not write them into the Streamlit dashboard.

## Requirements

- Python 3.9 or newer
- Java 11 or newer for the Spark streaming demonstration
- Kafka for the streaming demonstration (Docker Compose can start a local broker)
- The Online Retail II CSV dataset, downloaded separately

## Dataset setup

The dataset is deliberately not stored in this repository. Create a local `data/` directory and place the downloaded CSV at:

```text
data/online_retail_II.csv
```

The default path can be overridden with `RETAIL_DATASET_PATH`. Do not commit the dataset or generated outputs.

## Local installation

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

For notebook and development tools:

```bash
pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env` if you want to configure the dataset path or Kafka broker. The scripts load this file locally; environment variables already set by the process take precedence.

## Run batch analytics

Run these scripts from the repository root, in order:

```bash
python batch_processing.py
python visualization.py
python rfm_analysis.py
python churn_model.py
python ai_insights.py
python recommendation.py
streamlit run dashboard.py
```

The dashboard expects the generated files in `outputs/`. If those files do not exist, run the batch scripts first.

## Run the Kafka and Spark demo

Start a Kafka broker and set `KAFKA_BROKER` to its address. With Docker Compose, the internal address is `kafka:29092`; for a local broker it is normally `localhost:9092`.

In separate terminals:

```bash
python spark_streaming.py
python producer.py
```

The producer asks which replay mode to use. Start the Spark consumer before the producer so it can receive the events. This simulates replaying historical transactions; it is not a live connection to an e-commerce order system.

## Docker Compose

1. Place the dataset at `data/online_retail_II.csv`.
2. Run:

   ```bash
   docker compose up --build
   ```

3. The application container runs the batch scripts and then starts Streamlit. The Kafka broker is also started by Compose.
4. Open `http://localhost:8501`.

To run the streaming demo in the application container, use separate terminals:

```bash
docker compose exec bda-app python spark_streaming.py
docker compose exec -it bda-app python producer.py
```

Stop services with `docker compose down`.

## Important modeling limitations

- The current inactivity label is defined as **no purchase in the final 90 days of the observed dataset**. This is retrospective classification, not a validated prediction of future churn.
- Recency is excluded from the Random Forest input features because it directly defines the inactivity label. A proper future-churn model needs a historical feature cutoff and a separate future label window, followed by time-based validation.
- No accuracy, ROI, revenue-protection, or business-impact claim is made in this README. Those claims require a reproducible evaluation and a clearly defined business experiment.
- The business-insight module uses rules and descriptive statistics; it does not call a generative AI model.
- The Streamlit dashboard reads batch CSV outputs and does not display Kafka/Spark streaming results.
- Streaming is a local demonstration using replayed historical records, not a production event-ingestion service.

## Repository hygiene

Local environments, datasets, generated CSVs, trained models, logs, and charts are ignored by Git and Docker. Recreate them by following the setup steps above.
