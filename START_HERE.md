# Start Here

1. Download the Online Retail II CSV and place it at `data/online_retail_II.csv`.
2. Create a Python environment and run `pip install -r requirements.txt`.
3. Generate outputs:

   ```bash
   python batch_processing.py
   python visualization.py
   python rfm_analysis.py
   python churn_model.py
   python ai_insights.py
   python recommendation.py
   ```

4. Start the dashboard:

   ```bash
   streamlit run dashboard.py
   ```

5. For the optional Kafka/Spark replay demo, start Kafka, run `python spark_streaming.py`, then run `python producer.py` in a separate terminal.

Read [README.md](README.md) for the architecture, Docker instructions, and modeling limitations.
