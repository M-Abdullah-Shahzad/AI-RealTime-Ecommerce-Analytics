"""
MODULE 2 - DATASET LOADING & CLEANING
======================================
This module handles complete data preprocessing and cleaning for the Online Retail dataset.

Tasks:
- Load CSV dataset
- Remove null Customer IDs
- Remove duplicate rows
- Remove cancelled orders
- Remove negative quantities
- Remove invalid prices
- Handle missing values
- Create TotalPrice feature
- Convert data types
- Save cleaned dataset
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """Handles data loading, cleaning, and preprocessing"""
    
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.df_cleaned = None
        
    def load_data(self):
        """Load CSV dataset"""
        print("📂 Loading dataset...")
        self.df = pd.read_csv(self.csv_path)
        self.df.rename(columns={'Invoice': 'InvoiceNo', 'Customer ID': 'CustomerID'}, inplace=True)
        print(f"✓ Dataset loaded: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        print(f"\n📋 Dataset Columns: {list(self.df.columns)}")
        print(f"\n📊 Dataset Info:")
        print(self.df.info())
        return self.df
    
    def display_initial_stats(self):
        """Display initial data statistics"""
        print("\n" + "="*80)
        print("INITIAL DATASET STATISTICS")
        print("="*80)
        print(f"Total Records: {len(self.df)}")
        print(f"Total Columns: {len(self.df.columns)}")
        print(f"\n Missing Values:\n{self.df.isnull().sum()}")
        print(f"\n Data Types:\n{self.df.dtypes}")
        print(f"\n First 5 Rows:")
        print(self.df.head())
    
    def clean_data(self):
        """Execute complete data cleaning pipeline"""
        print("\n" + "="*80)
        print("DATA CLEANING PIPELINE")
        print("="*80)
        
        self.df_cleaned = self.df.copy()
        initial_rows = len(self.df_cleaned)
        
        # Step 1: Remove rows with null Customer IDs
        print("\n1️⃣  Removing null Customer IDs...")
        before = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned[self.df_cleaned['CustomerID'].notna()]
        removed = before - len(self.df_cleaned)
        print(f"   ✓ Removed {removed} rows with null CustomerID")
        
        # Step 2: Remove cancelled orders (InvoiceNo starts with 'C')
        print("\n2️⃣  Removing cancelled orders...")
        before = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned[~self.df_cleaned['InvoiceNo'].astype(str).str.startswith('C')]
        removed = before - len(self.df_cleaned)
        print(f"   ✓ Removed {removed} cancelled orders")
        
        # Step 3: Remove negative quantities
        print("\n3️⃣  Removing negative quantities...")
        before = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned[self.df_cleaned['Quantity'] > 0]
        removed = before - len(self.df_cleaned)
        print(f"   ✓ Removed {removed} records with negative quantities")
        
        # Step 4: Remove invalid prices (negative or zero)
        print("\n4️⃣  Removing invalid prices...")
        before = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned[self.df_cleaned['Price'] > 0]
        removed = before - len(self.df_cleaned)
        print(f"   ✓ Removed {removed} records with invalid prices")
        
        # Step 5: Remove duplicate rows
        print("\n5️⃣  Removing duplicate rows...")
        before = len(self.df_cleaned)
        self.df_cleaned = self.df_cleaned.drop_duplicates()
        removed = before - len(self.df_cleaned)
        print(f"   ✓ Removed {removed} duplicate rows")
        
        # Step 6: Convert data types
        print("\n6️⃣  Converting data types...")
        self.df_cleaned['InvoiceDate'] = pd.to_datetime(self.df_cleaned['InvoiceDate'])
        self.df_cleaned['CustomerID'] = self.df_cleaned['CustomerID'].astype(int)
        print("   ✓ Converted InvoiceDate to datetime")
        print("   ✓ Converted CustomerID to integer")
        
        # Step 7: Create TotalPrice feature
        print("\n7️⃣  Creating TotalPrice feature...")
        self.df_cleaned['TotalPrice'] = self.df_cleaned['Quantity'] * self.df_cleaned['Price']
        print("   ✓ Created TotalPrice = Quantity × Price")
        
        # Step 8: Handle any remaining issues
        print("\n8️⃣  Final cleanup...")
        self.df_cleaned = self.df_cleaned.reset_index(drop=True)
        print("   ✓ Reset index")
        
        final_rows = len(self.df_cleaned)
        total_removed = initial_rows - final_rows
        removal_percentage = (total_removed / initial_rows) * 100
        
        print("\n" + "-"*80)
        print(f"✓ CLEANING COMPLETE!")
        print(f"  Initial Records: {initial_rows:,}")
        print(f"  Final Records: {final_rows:,}")
        print(f"  Records Removed: {total_removed:,} ({removal_percentage:.2f}%)")
        print(f"  Data Quality: {((final_rows/initial_rows)*100):.2f}%")
        print("-"*80)
        
        return self.df_cleaned
    
    def display_cleaned_stats(self):
        """Display cleaned data statistics"""
        print("\n" + "="*80)
        print("CLEANED DATASET STATISTICS")
        print("="*80)
        print(f"Total Records: {len(self.df_cleaned):,}")
        print(f"Total Columns: {len(self.df_cleaned.columns)}")
        print(f"\nDate Range: {self.df_cleaned['InvoiceDate'].min()} to {self.df_cleaned['InvoiceDate'].max()}")
        print(f"Total Unique Customers: {self.df_cleaned['CustomerID'].nunique():,}")
        print(f"Total Unique Products: {self.df_cleaned['StockCode'].nunique():,}")
        print(f"Total Revenue: £{self.df_cleaned['TotalPrice'].sum():,.2f}")
        print(f"\nDescriptive Statistics:")
        print(self.df_cleaned[['Quantity', 'Price', 'TotalPrice']].describe())
    
    def save_cleaned_data(self, output_path):
        """Save cleaned dataset to CSV"""
        print(f"\n💾 Saving cleaned data to {output_path}...")
        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.df_cleaned.to_csv(output_path, index=False)
        print(f"✓ Cleaned data saved successfully!")
        return output_path
    
    def get_cleaned_data(self):
        """Return cleaned dataset"""
        return self.df_cleaned


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("🚀 MODULE 2: DATASET LOADING & CLEANING")
    print("="*80)
    
    # Initialize processor
    input_path = os.getenv('RETAIL_DATASET_PATH', 'data/online_retail_II.csv')
    output_path = 'outputs/online_retail_cleaned.csv'
    
    processor = DataProcessor(input_path)
    
    # Load data
    processor.load_data()
    processor.display_initial_stats()
    
    # Clean data
    processor.clean_data()
    processor.display_cleaned_stats()
    
    # Save cleaned data
    processor.save_cleaned_data(output_path)
    
    print("\n✅ Data cleaning complete! Ready for EDA and further processing.")


if __name__ == "__main__":
    main()
