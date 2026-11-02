"""
MODULE 4 - APACHE KAFKA STREAMING: PRODUCER
=============================================
Produces real-time customer transaction events to Kafka topic.

Simulates:
- Real-time customer orders
- One-by-one record streaming
- Live transaction events
- Producer-consumer architecture
"""

import os
import pandas as pd
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RetailKafkaProducer:
    """Produces retail transaction events to Kafka"""
    
    def __init__(self, bootstrap_servers=bootstrap_servers, topic='retail_orders'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self.df = None
        self.total_records = 0
        self.sent_records = 0
        
    def connect(self):
        """Establish connection to Kafka broker"""
        try:
            print(f"\n🔗 Connecting to Kafka broker at {self.bootstrap_servers}...")
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Wait for all replicas
                retries=3
            )
            print("✓ Successfully connected to Kafka!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            logger.error(f"Kafka connection error: {e}")
            return False
    
    def load_data(self, csv_path):
        """Load cleaned retail data"""
        print(f"\n📂 Loading data from {csv_path}...")
        try:
            self.df = pd.read_csv(csv_path)
            self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
            self.total_records = len(self.df)
            print(f"✓ Loaded {self.total_records:,} records")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            logger.error(f"Data loading error: {e}")
            return False
    
    def send_record(self, record, message_key=None):
        """Send single record to Kafka"""
        try:
            # Convert record to JSON-serializable format
            message = {
                'InvoiceNo': str(record['InvoiceNo']),
                'StockCode': str(record['StockCode']),
                'Description': str(record['Description']),
                'Quantity': int(record['Quantity']),
                'InvoiceDate': record['InvoiceDate'].isoformat(),
                'Price': float(record['Price']),
                'CustomerID': int(record['CustomerID']),
                'Country': str(record['Country']),
                'TotalPrice': float(record['TotalPrice'])
            }
            
            # Use CustomerID as message key for partitioning
            key = str(int(record['CustomerID'])).encode('utf-8')
            
            # Send message
            future = self.producer.send(self.topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            
            self.sent_records += 1
            return True
            
        except Exception as e:
            logger.error(f"Error sending record: {e}")
            return False
    
    def stream_data(self, batch_size=1, delay=0.1):
        """Stream data records one-by-one to Kafka"""
        print(f"\n" + "="*80)
        print("🚀 KAFKA PRODUCER: STREAMING TRANSACTION DATA")
        print("="*80)
        print(f"\n📊 Configuration:")
        print(f"   • Kafka Topic: {self.topic}")
        print(f"   • Total Records: {self.total_records:,}")
        print(f"   • Batch Size: {batch_size}")
        print(f"   • Delay between records: {delay}s")
        
        start_time = time.time()
        print(f"\n⏱️  Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✓ Streaming transactions...")
        
        try:
            for idx, (_, row) in enumerate(self.df.iterrows()):
                # Send record
                self.send_record(row)
                
                # Progress indicator
                if (idx + 1) % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = (idx + 1) / elapsed
                    remaining = (self.total_records - (idx + 1)) / rate if rate > 0 else 0
                    
                    print(f"\r✓ Sent {idx + 1:,}/{self.total_records:,} records | "
                          f"Rate: {rate:.0f} rec/s | "
                          f"ETA: {remaining:.0f}s", end='', flush=True)
                
                # Add delay between records to simulate streaming
                time.sleep(delay)
            
            # Flush any remaining messages
            self.producer.flush()
            
            total_time = time.time() - start_time
            print(f"\n\n✅ STREAMING COMPLETE!")
            print(f"   • Total Records Sent: {self.sent_records:,}")
            print(f"   • Total Time: {total_time:.2f}s")
            print(f"   • Average Rate: {self.sent_records/total_time:.2f} records/second")
            print(f"   • Ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Streaming interrupted by user")
            print(f"   • Records sent before interruption: {self.sent_records:,}")
        except Exception as e:
            print(f"\n\n❌ Error during streaming: {e}")
            logger.error(f"Streaming error: {e}")
        finally:
            self.close()
    
    def stream_data_demo(self, num_records=10):
        """Stream demo with first N records"""
        print(f"\n" + "="*80)
        print(f"🎬 KAFKA PRODUCER: DEMO MODE (First {num_records} records)")
        print("="*80)
        
        demo_df = self.df.head(num_records)
        print(f"\n📊 Streaming {len(demo_df)} sample records to topic: {self.topic}")
        print(f"   • Kafka Broker: {self.bootstrap_servers}")
        
        try:
            for idx, (_, row) in enumerate(demo_df.iterrows()):
                self.send_record(row)
                print(f"✓ Sent record {idx + 1}/{num_records}: "
                      f"Invoice {row['InvoiceNo']} | "
                      f"Product: {row['Description'][:40]:40s} | "
                      f"Amount: £{row['TotalPrice']:.2f}")
                time.sleep(1)
            
            self.producer.flush()
            print(f"\n✅ Demo streaming complete!")
            
        except Exception as e:
            print(f"\n❌ Error in demo mode: {e}")
            logger.error(f"Demo mode error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close Kafka connection"""
        if self.producer:
            print("\n🔌 Closing Kafka connection...")
            self.producer.close()
            print("✓ Kafka producer closed")


def check_kafka_availability(bootstrap_servers=None):
    """Check the configured Kafka broker before starting the producer."""
    bootstrap_servers = bootstrap_servers or os.getenv('KAFKA_BROKER', 'localhost:9092')
    print("\n" + "="*80)
    print("🔍 CHECKING KAFKA AVAILABILITY")
    print("="*80)
    
    try:
        from socket import create_connection
        from urllib.parse import urlsplit
        parsed = urlsplit(f'//{bootstrap_servers}')
        host = parsed.hostname or 'localhost'
        port = parsed.port or 9092
        sock = create_connection((host, port), timeout=2)
        sock.close()
        print(f"✓ Kafka broker is available at {bootstrap_servers}")
        return True
    except Exception as e:
        print(f"❌ Kafka broker not available: {e}")
        print("\n📌 TROUBLESHOOTING:")
        print("   1. Ensure Kafka is installed")
        print("   2. Start Zookeeper: bin/zookeeper-server-start.sh config/zookeeper.properties")
        print("   3. Start Kafka broker: bin/kafka-server-start.sh config/server.properties")
        print("   4. Create topic: bin/kafka-topics.sh --create --topic retail_orders --bootstrap-server localhost:9092")
        return False


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("🚀 MODULE 4: APACHE KAFKA STREAMING - PRODUCER")
    print("="*80)
    
    # Respect the broker address supplied by Docker Compose or the local environment.
    bootstrap_servers = os.getenv('KAFKA_BROKER', 'localhost:9092')
    if not check_kafka_availability(bootstrap_servers):
        print("\n⚠️  Please start Kafka before running the producer")
        return
    
    # Initialize producer
    producer = RetailKafkaProducer(
        bootstrap_servers='localhost:9092',
        topic='retail_orders'
    )
    
    # Connect to Kafka
    if not producer.connect():
        print("❌ Cannot connect to Kafka. Exiting.")
        return
    
    # Load data
    if not producer.load_data('outputs/online_retail_cleaned.csv'):
        print("❌ Cannot load data. Exiting.")
        return
    
    # Choose mode
    print("\n" + "="*80)
    print("SELECT STREAMING MODE")
    print("="*80)
    print("1. Demo Mode (stream first 10 records)")
    print("2. Full Streaming (stream all records with delay)")
    print("3. Fast Streaming (stream all records quickly)")
    
    mode = input("\nEnter choice (1-3): ").strip()
    
    if mode == '1':
        producer.stream_data_demo(num_records=10)
    elif mode == '2':
        producer.stream_data(batch_size=1, delay=0.1)
    elif mode == '3':
        producer.stream_data(batch_size=1, delay=0.01)
    else:
        print("❌ Invalid choice")
    
    print("\n✅ Producer execution complete!")


if __name__ == "__main__":
    main()
