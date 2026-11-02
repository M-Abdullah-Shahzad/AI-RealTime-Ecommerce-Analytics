# Project Overview

## Purpose

Explore retail transactions and demonstrate a set of data analytics and data engineering techniques using the Online Retail II dataset.

## Implemented modules

1. **Batch processing** — clean transactions, remove invalid rows, and create total-price values.
2. **EDA** — summarize sales over time, products, and countries.
3. **RFM analysis** — calculate recency, frequency, and monetary customer measures and assign descriptive segments.
4. **Historical inactivity classification** — train a Random Forest classifier for an end-of-dataset inactivity label.
5. **Business insights** — generate deterministic recommendations from calculated customer and sales summaries.
6. **Market-basket analysis** — use Apriori and association rules to identify product combinations.
7. **Kafka producer** — replay cleaned transaction rows as events.
8. **Spark Structured Streaming consumer** — calculate windowed aggregates from Kafka events.
9. **Streamlit dashboard** — visualize generated batch output files.

## Data flow

Batch processing generates the CSV files consumed by the downstream analytics modules. The dashboard reads those output files. Kafka and Spark are a separate streaming demonstration; the dashboard is not currently wired to their streaming output.

## Technology

Python, Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Plotly, Streamlit, Apache Kafka, PySpark, and MLxtend.

## Evaluation and limitations

The churn target is defined using the final 90 days of the observed dataset. The model is therefore an exploratory historical inactivity classifier, not a future-period churn predictor. Recency is excluded from the input features because it directly defines the target. A future-prediction claim requires a time-based feature cutoff, a later label window, and independent temporal validation.

The rule-based insight module is not an LLM application. The Kafka producer replays historical records, and the dashboard displays batch results rather than live stream metrics. No ROI or production-readiness claim is made.
