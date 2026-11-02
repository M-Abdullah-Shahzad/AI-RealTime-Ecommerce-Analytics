"""
MODULE 5 - SPARK STRUCTURED STREAMING
======================================
Real-time consumption and processing of Kafka streaming data.

Features:
- Kafka consumer integration
- Structured streaming
- Windowed aggregations
- Real-time analytics
- Micro-batch processing
"""

import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, schema_of_json, window, 
    sum as spark_sum, count, avg, max as spark_max,
    min as spark_min, countDistinct, desc
)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
import json
import time
from datetime import datetime


class SparkStreamingConsumer:
    """Consumes and processes Kafka streaming data with Spark"""
    
    def __init__(self, kafka_bootstrap=os.getenv('KAFKA_BROKER', 'localhost:9092'), kafka_topic='retail_orders'):
        self.kafka_bootstrap = kafka_bootstrap
        self.kafka_topic = kafka_topic
        self.spark = None
        self.df_stream = None
        
    def initialize_spark(self):
        """Initialize Spark session"""
        print("\n" + "="*80)
        print("⚡ INITIALIZING APACHE SPARK")
        print("="*80)
        
        try:
            self.spark = SparkSession.builder \
                .appName("RetailStreamingAnalytics") \
                .config("spark.sql.streaming.schemaInference", "true") \
                .getOrCreate()
            
            print("✓ Spark session initialized")
            print(f"   • Spark Version: {self.spark.version}")
            print(f"   • Master: local[*]")
            
            # Set log level
            self.spark.sparkContext.setLogLevel("WARN")
            
            return True
        except Exception as e:
            print(f"❌ Error initializing Spark: {e}")
            return False
    
    def define_schema(self):
        """Define schema for Kafka messages"""
        schema = StructType([
            StructField("InvoiceNo", StringType(), True),
            StructField("StockCode", StringType(), True),
            StructField("Description", StringType(), True),
            StructField("Quantity", IntegerType(), True),
            StructField("InvoiceDate", StringType(), True),
            StructField("Price", FloatType(), True),
            StructField("CustomerID", IntegerType(), True),
            StructField("Country", StringType(), True),
            StructField("TotalPrice", FloatType(), True)
        ])
        return schema
    
    def read_kafka_stream(self):
        """Read streaming data from Kafka"""
        print("\n" + "="*80)
        print("🔗 CONNECTING TO KAFKA STREAM")
        print("="*80)
        
        try:
            schema = self.define_schema()
            
            print(f"   • Kafka Broker: {self.kafka_bootstrap}")
            print(f"   • Topic: {self.kafka_topic}")
            
            df = self.spark.readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_bootstrap) \
                .option("subscribe", self.kafka_topic) \
                .option("startingOffsets", "latest") \
                .load()
            
            # Parse JSON value
            df_parsed = df.select(
                from_json(col("value").cast("string"), schema).alias("data")
            ).select("data.*")
            
            # Convert timestamp
            df_parsed = df_parsed.withColumn(
                "InvoiceDate", 
                col("InvoiceDate").cast("timestamp")
            )
            
            self.df_stream = df_parsed
            print("✓ Connected to Kafka stream")
            
            return df_parsed
            
        except Exception as e:
            print(f"❌ Error reading Kafka stream: {e}")
            return None
    
    def streaming_sales_analytics(self):
        """Real-time sales analytics"""
        print("\n" + "="*80)
        print("📊 REAL-TIME SALES ANALYTICS (1-minute windows)")
        print("="*80)
        
        if self.df_stream is None:
            print("❌ Streaming data not initialized")
            return
        
        # Windowed aggregations
        df_windowed = self.df_stream.withWatermark("InvoiceDate", "1 minute") \
            .groupBy(window(col("InvoiceDate"), "1 minute")) \
            .agg(
                spark_sum("TotalPrice").alias("TotalRevenue"),
                spark_sum("Quantity").alias("TotalItems"),
                count("*").alias("OrderCount"),
                countDistinct("CustomerID").alias("UniqueCustomers"),
                avg("TotalPrice").alias("AvgOrderValue"),
                spark_max("TotalPrice").alias("MaxOrder"),
                spark_min("TotalPrice").alias("MinOrder")
            ) \
            .select(
                col("window").getField("start").alias("TimeWindow"),
                col("TotalRevenue"),
                col("TotalItems"),
                col("OrderCount"),
                col("UniqueCustomers"),
                col("AvgOrderValue"),
                col("MaxOrder"),
                col("MinOrder")
            )
        
        query = df_windowed \
            .writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", "false") \
            .option("numRows", 10) \
            .start()
        
        print("\n✓ Real-time sales analytics streaming started")
        print("  [Press Ctrl+C to stop]")
        
        return query
    
    def streaming_top_products(self):
        """Real-time top products analysis"""
        print("\n" + "="*80)
        print("🏆 TOP PRODUCTS (5-minute windows)")
        print("="*80)
        
        if self.df_stream is None:
            print("❌ Streaming data not initialized")
            return
        
        df_top_products = self.df_stream.withWatermark("InvoiceDate", "1 minute") \
            .groupBy(
                window(col("InvoiceDate"), "5 minutes"),
                col("Description")
            ) \
            .agg(
                spark_sum("Quantity").alias("TotalQuantity"),
                spark_sum("TotalPrice").alias("Revenue"),
                count("*").alias("Orders")
            ) \
            .filter(col("TotalQuantity") > 0) \
            .orderBy(col("window"), desc("TotalQuantity"))
        
        query = df_top_products \
            .writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", "false") \
            .option("numRows", 20) \
            .start()
        
        print("\n✓ Top products streaming started")
        print("  [Press Ctrl+C to stop]")
        
        return query
    
    def streaming_country_sales(self):
        """Real-time country-wise sales"""
        print("\n" + "="*80)
        print("🌍 COUNTRY-WISE SALES (10-minute windows)")
        print("="*80)
        
        if self.df_stream is None:
            print("❌ Streaming data not initialized")
            return
        
        df_country = self.df_stream.withWatermark("InvoiceDate", "1 minute") \
            .groupBy(
                window(col("InvoiceDate"), "10 minutes"),
                col("Country")
            ) \
            .agg(
                spark_sum("TotalPrice").alias("Revenue"),
                count("*").alias("Orders"),
                countDistinct("CustomerID").alias("Customers")
            ) \
            .orderBy(col("window"), desc("Revenue"))
        
        query = df_country \
            .writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", "false") \
            .option("numRows", 30) \
            .start()
        
        print("\n✓ Country sales streaming started")
        print("  [Press Ctrl+C to stop]")
        
        return query
    
    def streaming_customer_activity(self):
        """Real-time customer activity monitoring"""
        print("\n" + "="*80)
        print("👥 ACTIVE CUSTOMERS (2-minute windows)")
        print("="*80)
        
        if self.df_stream is None:
            print("❌ Streaming data not initialized")
            return
        
        df_customers = self.df_stream.withWatermark("InvoiceDate", "1 minute") \
            .groupBy(
                window(col("InvoiceDate"), "2 minutes"),
                col("CustomerID")
            ) \
            .agg(
                count("*").alias("Transactions"),
                spark_sum("TotalPrice").alias("Spending"),
                spark_sum("Quantity").alias("ItemsCount")
            ) \
            .filter(col("Spending") > 0) \
            .orderBy(col("window"), desc("Spending"))
        
        query = df_customers \
            .writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", "false") \
            .option("numRows", 25) \
            .start()
        
        print("\n✓ Customer activity streaming started")
        print("  [Press Ctrl+C to stop]")
        
        return query
    
    def streaming_to_memory(self, query_name="sales_analytics"):
        """Stream data to memory table for interactive queries"""
        print(f"\n✓ Streaming to memory table: {query_name}")
        
        if self.df_stream is None:
            print("❌ Streaming data not initialized")
            return
        
        query = self.df_stream.writeStream \
            .outputMode("append") \
            .format("memory") \
            .queryName(query_name) \
            .start()
        
        return query
    
    def run_streaming_demo(self):
        """Run streaming demo with all analytics"""
        print("\n" + "="*80)
        print("🚀 MODULE 5: SPARK STRUCTURED STREAMING")
        print("="*80)
        
        # Initialize Spark
        if not self.initialize_spark():
            return
        
        # Connect to Kafka
        if self.read_kafka_stream() is None:
            return
        
        print("\n" + "="*80)
        print("SELECT STREAMING ANALYTICS")
        print("="*80)
        print("1. Real-time Sales Analytics")
        print("2. Top Products")
        print("3. Country-wise Sales")
        print("4. Active Customers")
        print("5. Multiple Analytics (All Combined)")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        queries = []
        
        try:
            if choice == '1':
                queries.append(self.streaming_sales_analytics())
            elif choice == '2':
                queries.append(self.streaming_top_products())
            elif choice == '3':
                queries.append(self.streaming_country_sales())
            elif choice == '4':
                queries.append(self.streaming_customer_activity())
            elif choice == '5':
                queries.append(self.streaming_sales_analytics())
                time.sleep(2)
                queries.append(self.streaming_top_products())
                time.sleep(2)
                queries.append(self.streaming_country_sales())
            else:
                print("❌ Invalid choice")
                return
            
            # Keep streaming active
            print("\n" + "="*80)
            print("⏱️  Streaming is active. Processing live data...")
            print("="*80)
            print("Press Ctrl+C to stop streaming\n")
            
            for query in queries:
                query.awaitTermination()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopping streams...")
            for query in queries:
                query.stop()
            print("✓ All streams stopped")
        except Exception as e:
            print(f"\n❌ Error during streaming: {e}")
        finally:
            if self.spark:
                self.spark.stop()
                print("✓ Spark session closed")


def main():
    """Main execution"""
    consumer = SparkStreamingConsumer(
        kafka_bootstrap='localhost:9092',
        kafka_topic='retail_orders'
    )
    
    consumer.run_streaming_demo()


if __name__ == "__main__":
    main()
