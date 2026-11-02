# Project Delivery Summary

## Implemented

- Transaction cleaning and feature creation.
- Exploratory data analysis and visualizations.
- RFM customer segmentation.
- Exploratory Random Forest classification of historical inactivity.
- Rule-based customer and sales insights.
- Apriori association-rule recommendations.
- Kafka transaction replay producer.
- Spark Structured Streaming consumer with windowed aggregations.
- Streamlit dashboard for precomputed batch analytics.
- Docker Compose configuration for the dashboard application and Kafka broker.

## Generated locally

The following are produced during execution and are intentionally not committed:

- Cleaned transaction data.
- RFM and churn output CSVs.
- Insight and association-rule CSVs.
- Charts, logs, model pickle files, and Spark state.

## Not claimed

This project does not currently provide a production order-ingestion service, a dashboard connected to Kafka, a validated future-churn model, or a measured business ROI. Those would require additional implementation and evaluation.

## Reproduction

See [README.md](README.md) for dataset setup, local execution, Docker Compose, and streaming-demo instructions.
