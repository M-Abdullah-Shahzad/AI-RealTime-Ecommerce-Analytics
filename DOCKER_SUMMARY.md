# Docker Compose Summary

| Service | Purpose | Port |
|---|---|---|
| Zookeeper | Kafka coordination | 2181 |
| Kafka | Local event broker | 9092 (host), 29092 (container network) |
| bda-app | Batch analytics and Streamlit dashboard | 8501 |

## Data mounts

- `./data:/app/data` — locally downloaded dataset.
- `./outputs:/app/outputs` — generated analytics consumed by the dashboard.
- `./logs:/app/logs` — local logs.

The dataset and outputs are not baked into the image. The application container runs the batch scripts and then the dashboard. Kafka is available for manual streaming demonstrations, but the dashboard does not display live Kafka/Spark results.

Start with `docker compose up --build`; stop with `docker compose down`.
