# Docker Deployment

## What Compose starts

- Zookeeper and Kafka broker.
- The analytics application container, which runs the batch modules and then starts Streamlit.

The Streamlit dashboard reads generated CSV files. The Kafka/Spark stream is an optional, separate demonstration and is not connected to the dashboard.

## Prepare local data

Before building, create `data/` and place the Online Retail II CSV at:

```text
data/online_retail_II.csv
```

The `data/` and `outputs/` directories are bind-mounted by Compose. They are intentionally excluded from the Docker build context and Git.

## Start

```bash
docker compose up --build
```

Open `http://localhost:8501` after the batch pipeline finishes and Streamlit starts.

## Run the streaming demo

In separate terminals:

```bash
docker compose exec bda-app python spark_streaming.py
docker compose exec -it bda-app python producer.py
```

The Compose environment sets the internal Kafka address to `kafka:29092`.

## Stop

```bash
docker compose down
```

Add `-v` only when you intentionally want to remove Compose-managed volumes.

## Notes

- The first build can take time because Spark and its Java runtime are installed.
- The dataset must exist on the host before starting the application container.
- The app container runs the batch scripts at startup; it does not automatically launch the Kafka producer or Spark consumer.
