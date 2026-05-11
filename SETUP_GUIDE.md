# SETUP & INSTALLATION GUIDE

## Complete Setup Instructions for Big Data + AI Analytics Project

---

## Prerequisites Verification

### Check Python Version
```bash
python --version
# Required: Python 3.8 or higher
```

### Check Java Installation
```bash
java -version
# Required: Java 8+
```

---

## Step 1: Project Initialization

### 1.1 Create Project Directory
```bash
cd C:\Users\usama\OneDrive\Desktop
mkdir BDA_project
cd BDA_project
```

### 1.2 Create Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

### 1.3 Upgrade pip
```bash
python -m pip install --upgrade pip
```

---

## Step 2: Install Python Dependencies

### 2.1 Install all packages
```bash
pip install -r requirements.txt
```

### 2.2 Verify installations
```bash
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import sklearn; print(f'Scikit-learn: {sklearn.__version__}')"
python -c "import pyspark; print(f'PySpark: {pyspark.__version__}')"
```

---

## Step 3: Apache Spark Setup (Optional for streaming)

### 3.1 Download Spark
```bash
# Visit https://spark.apache.org/downloads.html
# Download spark-3.2.0-bin-hadoop3.2.tgz

# Extract to a location (e.g., C:\Spark)
```

### 3.2 Set Environment Variables (Windows)
```bash
# System Properties → Environment Variables → New

Variable Name: SPARK_HOME
Variable Value: C:\Spark\spark-3.2.0-bin-hadoop3.2

# Add to PATH:
%SPARK_HOME%\bin
```

### 3.3 Verify Spark Installation
```bash
spark-submit --version
```

### 3.4 Download Hadoop (Optional)
If you get Java errors, download winutils.exe:
```bash
# Create C:\hadoop\bin directory
# Download winutils.exe from GitHub
# Set HADOOP_HOME environment variable
```

---

## Step 4: Apache Kafka Setup (For real-time streaming)

### 4.1 Download Kafka
```bash
# Visit https://kafka.apache.org/downloads
# Download kafka_2.13-3.0.0.tgz
# Extract to C:\Kafka\
```

### 4.2 Start Zookeeper (Terminal 1)
```bash
cd C:\Kafka\kafka_2.13-3.0.0

# Windows
bin\windows\zookeeper-server-start.bat config\zookeeper.properties

# Linux/Mac
bin/zookeeper-server-start.sh config/zookeeper.properties
```

### 4.3 Start Kafka Broker (Terminal 2)
```bash
cd C:\Kafka\kafka_2.13-3.0.0

# Windows
bin\windows\kafka-server-start.bat config\server.properties

# Linux/Mac
bin/kafka-server-start.sh config/server.properties
```

### 4.4 Create Kafka Topic (Terminal 3)
```bash
cd C:\Kafka\kafka_2.13-3.0.0

# Windows
bin\windows\kafka-topics.bat --create --topic retail_orders \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1

# Linux/Mac
bin/kafka-topics.sh --create --topic retail_orders \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1
```

### 4.5 Verify Topic Creation
```bash
# Windows
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

# Linux/Mac
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

---

## Step 5: Project Execution

### Phase 1: Data Preparation

#### 5.1 Data Cleaning
```bash
cd C:\Users\usama\OneDrive\Desktop\BDA_project
python batch_processing.py
```

**Expected Output**:
```
✓ Dataset loaded: 500,000 rows × 8 columns
✓ Data cleaning complete!
✓ Cleaned data saved successfully!
Output: outputs/online_retail_cleaned.csv
```

#### 5.2 Exploratory Data Analysis
```bash
python visualization.py
```

**Expected Output**:
```
✓ EDA COMPLETE!
📊 All visualizations saved to outputs/ directory
Files: 01_monthly_sales_trends.png through 09_seasonal_trends.png
```

### Phase 2: Customer Analytics

#### 5.3 RFM Customer Segmentation
```bash
python rfm_analysis.py
```

**Expected Output**:
```
✓ RFM ANALYSIS COMPLETE!
Output: outputs/rfm_analysis.csv
Output: outputs/segment_summary.csv
Output: outputs/10_rfm_segmentation.png
```

#### 5.4 Machine Learning Churn Prediction
```bash
python churn_model.py
```

**Expected Output**:
```
✓ CHURN PREDICTION COMPLETE!
Output: outputs/churn_predictions.csv
Output: outputs/11_churn_prediction_model.png
Output: outputs/churn_model.pkl
Output: outputs/churn_scaler.pkl
```

#### 5.5 AI Insights Generation
```bash
python ai_insights.py
```

**Expected Output**:
```
✓ AI INSIGHTS GENERATION COMPLETE!
Output: outputs/ai_insights.csv
```

#### 5.6 Recommendation System
```bash
python recommendation.py
```

**Expected Output**:
```
✓ RECOMMENDATION SYSTEM COMPLETE!
Output: outputs/association_rules.csv
Output: outputs/12_recommendation_rules.png
```

### Phase 3: Real-Time Streaming (Optional)

#### 5.7 Start Kafka Producer
```bash
# Terminal 1: Start producer
python producer.py

# Select mode:
# 1. Demo Mode (10 records)
# 2. Full Streaming (all records, slow)
# 3. Fast Streaming (all records, fast)
```

#### 5.8 Start Spark Streaming Consumer
```bash
# Terminal 2: Start streaming consumer
python spark_streaming.py

# Select analytics:
# 1. Real-time Sales Analytics
# 2. Top Products
# 3. Country-wise Sales
# 4. Active Customers
# 5. Multiple Analytics (all)
```

### Phase 4: Interactive Dashboard

#### 5.9 Launch Streamlit Dashboard
```bash
# Terminal 3: Launch dashboard
streamlit run dashboard.py
```

**Access at**: `http://localhost:8501`

**Dashboard Features**:
- Real-time KPIs
- Sales analytics
- Customer insights
- Churn analysis
- Geographical analysis
- AI insights
- Recommendations

---

## Troubleshooting Guide

### Issue 1: Module Not Found
```bash
# Solution:
pip install [module-name]

# Example:
pip install pyspark
```

### Issue 2: Kafka Connection Refused
```bash
# Solution: Ensure Kafka is running
# Check if Zookeeper and Kafka broker are started
jps  # Should show QuorumPeerMain and Kafka processes

# Restart Kafka
# Stop and restart zookeeper and broker
```

### Issue 3: Spark Python Not Found
```bash
# Solution:
export PYSPARK_PYTHON=python
export PYSPARK_DRIVER_PYTHON=python

# Windows:
set PYSPARK_PYTHON=python
set PYSPARK_DRIVER_PYTHON=python
```

### Issue 4: Memory Error
```bash
# Solution: Increase memory allocation
# Windows:
set SPARK_LOCAL_IP=127.0.0.1
set SPARK_DRIVER_MEMORY=4g
set SPARK_EXECUTOR_MEMORY=2g

# Linux/Mac:
export SPARK_LOCAL_IP=127.0.0.1
export SPARK_DRIVER_MEMORY=4g
export SPARK_EXECUTOR_MEMORY=2g
```

### Issue 5: Port Already in Use
```bash
# Solution: Kill process using port
# Windows:
netstat -ano | findstr :9092
taskkill /PID [PID] /F

# Linux/Mac:
lsof -i :9092
kill -9 [PID]
```

---

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Java 8+ installed
- [ ] Virtual environment created and activated
- [ ] All pip packages installed
- [ ] Data file exists: `data/online_retail_II.csv`
- [ ] Can run: `python batch_processing.py`
- [ ] Outputs generated in `outputs/` folder
- [ ] RFM analysis complete
- [ ] Churn model trained
- [ ] Dashboard accessible at localhost:8501

---

## Environment Variables Summary

### Windows
```batch
REM Java
set JAVA_HOME=C:\Program Files\Java\jdk1.8.0_281

REM Spark
set SPARK_HOME=C:\Spark\spark-3.2.0-bin-hadoop3.2
set PATH=%PATH%;%SPARK_HOME%\bin

REM Hadoop (if needed)
set HADOOP_HOME=C:\hadoop

REM Python
set PYSPARK_PYTHON=python
```

### Linux/Mac
```bash
# Java
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk

# Spark
export SPARK_HOME=/opt/spark/spark-3.2.0-bin-hadoop3.2
export PATH=$PATH:$SPARK_HOME/bin

# Python
export PYSPARK_PYTHON=python3
```

---

## Quick Start Commands

### Run Everything Sequentially
```bash
python batch_processing.py && \
python visualization.py && \
python rfm_analysis.py && \
python churn_model.py && \
python ai_insights.py && \
python recommendation.py && \
streamlit run dashboard.py
```

### Run Specific Module
```bash
# Clean data only
python batch_processing.py

# EDA only
python visualization.py

# All analytics (no streaming)
python batch_processing.py
python visualization.py
python rfm_analysis.py
python churn_model.py
python ai_insights.py
python recommendation.py
```

---

## Performance Notes

- **Data Cleaning**: ~2-5 minutes (500K records)
- **EDA**: ~2-3 minutes
- **RFM Analysis**: ~1-2 minutes
- **Churn Prediction**: ~3-5 minutes (model training)
- **AI Insights**: ~1 minute
- **Recommendations**: ~2-3 minutes
- **Total Batch**: ~15-20 minutes

---

## Success Criteria

✅ All modules execute without errors
✅ Output files generated in `outputs/` directory
✅ Visualizations display correctly
✅ Dashboard loads and is interactive
✅ Insights and recommendations are meaningful
✅ No memory errors or timeouts

---

## Next Steps

1. ✅ Complete setup
2. ✅ Run batch processing
3. ✅ Explore visualizations
4. ✅ Review RFM segments
5. ✅ Check churn predictions
6. ✅ Launch dashboard
7. ✅ Generate reports
8. ✅ Prepare for viva/presentation

---

## Support Resources

- **Spark Documentation**: https://spark.apache.org/docs/latest/
- **Kafka Docs**: https://kafka.apache.org/documentation/
- **Pandas**: https://pandas.pydata.org/docs/
- **Scikit-learn**: https://scikit-learn.org/stable/documentation.html
- **Streamlit**: https://docs.streamlit.io/

---

**Setup Complete! Ready for Big Data Analytics! 🚀**
