"""
MODULE 3 - EXPLORATORY DATA ANALYSIS (EDA)
===========================================
Comprehensive business analytics and visualization of e-commerce data.

Performs:
- Monthly and yearly sales trends
- Top-selling products
- Top revenue-generating products
- Country-wise sales analysis
- Top customer analysis
- Customer behavior analysis
- Seasonal trends
- Distribution analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class EDAnalyzer:
    """Performs exploratory data analysis"""
    
    def __init__(self, cleaned_data_path):
        self.df = pd.read_csv(cleaned_data_path)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.df['Month'] = self.df['InvoiceDate'].dt.to_period('M')
        self.df['Year'] = self.df['InvoiceDate'].dt.year
        self.df['YearMonth'] = self.df['InvoiceDate'].dt.strftime('%Y-%m')
        
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"📊 {title}")
        print("="*80)
    
    def business_overview(self):
        """Display business overview statistics"""
        self.print_header("BUSINESS OVERVIEW")
        
        print(f"\n📈 Dataset Period: {self.df['InvoiceDate'].min().date()} to {self.df['InvoiceDate'].max().date()}")
        print(f"\n👥 Customers:")
        print(f"   • Total Unique Customers: {self.df['CustomerID'].nunique():,}")
        print(f"   • Average Orders per Customer: {len(self.df) / self.df['CustomerID'].nunique():.2f}")
        
        print(f"\n📦 Products:")
        print(f"   • Total Unique Products: {self.df['StockCode'].nunique():,}")
        print(f"   • Total Unique Descriptions: {self.df['Description'].nunique():,}")
        
        print(f"\n💰 Revenue:")
        print(f"   • Total Revenue: £{self.df['TotalPrice'].sum():,.2f}")
        print(f"   • Average Transaction Value: £{self.df['TotalPrice'].mean():.2f}")
        print(f"   • Median Transaction Value: £{self.df['TotalPrice'].median():.2f}")
        print(f"   • Max Transaction: £{self.df['TotalPrice'].max():,.2f}")
        
        print(f"\n🌍 Countries:")
        print(f"   • Operating in {self.df['Country'].nunique()} countries")
    
    def monthly_sales_trends(self):
        """Analyze monthly sales trends"""
        self.print_header("MONTHLY SALES TRENDS")
        
        monthly_sales = self.df.groupby('YearMonth').agg({
            'TotalPrice': ['sum', 'mean', 'count'],
            'CustomerID': 'nunique'
        }).round(2)
        
        monthly_sales.columns = ['Total Revenue', 'Avg Transaction', 'Orders', 'Unique Customers']
        print("\n" + monthly_sales.to_string())
        
        # Create visualization
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # Revenue trend
        monthly_revenue = self.df.groupby('YearMonth')['TotalPrice'].sum()
        axes[0].plot(range(len(monthly_revenue)), monthly_revenue.values, 
                    marker='o', linewidth=2, color='#2ecc71', markersize=6)
        axes[0].set_title('Monthly Sales Revenue Trend', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Month')
        axes[0].set_ylabel('Revenue (£)')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xticks(range(0, len(monthly_revenue), 3))
        axes[0].set_xticklabels(monthly_revenue.index[::3], rotation=45)
        
        # Order count trend
        monthly_orders = self.df.groupby('YearMonth').size()
        axes[1].bar(range(len(monthly_orders)), monthly_orders.values, 
                   color='#3498db', alpha=0.7)
        axes[1].set_title('Monthly Order Count Trend', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Month')
        axes[1].set_ylabel('Number of Orders')
        axes[1].grid(True, alpha=0.3, axis='y')
        axes[1].set_xticks(range(0, len(monthly_orders), 3))
        axes[1].set_xticklabels(monthly_orders.index[::3], rotation=45)
        
        plt.tight_layout()
        plt.savefig('outputs/01_monthly_sales_trends.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/01_monthly_sales_trends.png")
        plt.close()
    
    def top_products_analysis(self):
        """Analyze top-selling products"""
        self.print_header("TOP 15 SELLING PRODUCTS")
        
        top_products = self.df.groupby('Description').agg({
            'Quantity': 'sum',
            'TotalPrice': 'sum',
            'InvoiceNo': 'count'
        }).sort_values('Quantity', ascending=False).head(15)
        top_products.columns = ['Units Sold', 'Revenue', 'Transactions']
        print("\n" + top_products.to_string())
        
        # Visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        top_10_products = top_products.head(10)
        colors = plt.cm.viridis(np.linspace(0, 1, len(top_10_products)))
        ax.barh(range(len(top_10_products)), top_10_products['Units Sold'], color=colors)
        ax.set_yticks(range(len(top_10_products)))
        ax.set_yticklabels(top_10_products.index, fontsize=9)
        ax.set_xlabel('Units Sold', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 Best-Selling Products', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, v in enumerate(top_10_products['Units Sold']):
            ax.text(v + 50, i, f'{int(v):,}', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('outputs/02_top_products.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/02_top_products.png")
        plt.close()
    
    def revenue_products_analysis(self):
        """Analyze top revenue-generating products"""
        self.print_header("TOP 15 REVENUE-GENERATING PRODUCTS")
        
        revenue_products = self.df.groupby('Description').agg({
            'TotalPrice': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'count'
        }).sort_values('TotalPrice', ascending=False).head(15)
        revenue_products.columns = ['Total Revenue', 'Units Sold', 'Transactions']
        print("\n" + revenue_products.to_string())
        
        # Visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        top_10_revenue = revenue_products.head(10)
        colors = plt.cm.Spectral(np.linspace(0, 1, len(top_10_revenue)))
        bars = ax.barh(range(len(top_10_revenue)), top_10_revenue['Total Revenue'], color=colors)
        ax.set_yticks(range(len(top_10_revenue)))
        ax.set_yticklabels(top_10_revenue.index, fontsize=9)
        ax.set_xlabel('Revenue (£)', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 Revenue-Generating Products', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, v in enumerate(top_10_revenue['Total Revenue']):
            ax.text(v + 100, i, f'£{v:,.0f}', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('outputs/03_revenue_products.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/03_revenue_products.png")
        plt.close()
    
    def country_analysis(self):
        """Analyze country-wise sales"""
        self.print_header("TOP 15 COUNTRIES BY REVENUE")
        
        country_sales = self.df.groupby('Country').agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'count',
            'CustomerID': 'nunique'
        }).sort_values('TotalPrice', ascending=False).head(15)
        country_sales.columns = ['Total Revenue', 'Orders', 'Unique Customers']
        print("\n" + country_sales.to_string())
        
        # Visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        top_15_countries = country_sales.head(15)
        colors = plt.cm.RdYlGn(np.linspace(0, 1, len(top_15_countries)))
        ax.bar(range(len(top_15_countries)), top_15_countries['Total Revenue'], color=colors)
        ax.set_xticks(range(len(top_15_countries)))
        ax.set_xticklabels(top_15_countries.index, rotation=45, ha='right')
        ax.set_ylabel('Revenue (£)', fontsize=12, fontweight='bold')
        ax.set_title('Top 15 Countries by Revenue', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        for i, v in enumerate(top_15_countries['Total Revenue']):
            ax.text(i, v + 5000, f'£{v/1000:.0f}K', ha='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('outputs/04_country_revenue.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/04_country_revenue.png")
        plt.close()
    
    def top_customers_analysis(self):
        """Analyze top customers"""
        self.print_header("TOP 20 CUSTOMERS")
        
        top_customers = self.df.groupby('CustomerID').agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'count'
        }).sort_values('TotalPrice', ascending=False).head(20)
        top_customers.columns = ['Total Spent', 'Transactions']
        print("\n" + top_customers.to_string())
        
        # Visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        top_10_cust = top_customers.head(10)
        colors = plt.cm.plasma(np.linspace(0, 1, len(top_10_cust)))
        ax.barh(range(len(top_10_cust)), top_10_cust['Total Spent'], color=colors)
        ax.set_yticks(range(len(top_10_cust)))
        ax.set_yticklabels([f"Customer {cid}" for cid in top_10_cust.index], fontsize=10)
        ax.set_xlabel('Total Spent (£)', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 Customers by Lifetime Value', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, v in enumerate(top_10_cust['Total Spent']):
            ax.text(v + 500, i, f'£{v:,.0f}', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('outputs/05_top_customers.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/05_top_customers.png")
        plt.close()
    
    def customer_behavior_analysis(self):
        """Analyze customer purchase behavior"""
        self.print_header("CUSTOMER PURCHASE BEHAVIOR")
        
        customer_stats = self.df.groupby('CustomerID').agg({
            'InvoiceNo': 'count',
            'TotalPrice': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        customer_stats.columns = ['CustomerID', 'Purchases', 'TotalSpent', 'TotalItems']
        
        print(f"\n📊 Purchase Frequency Distribution:")
        print(f"   • Average Purchases per Customer: {customer_stats['Purchases'].mean():.2f}")
        print(f"   • Median Purchases per Customer: {customer_stats['Purchases'].median():.0f}")
        print(f"   • Max Purchases: {customer_stats['Purchases'].max():.0f}")
        print(f"   • One-time Buyers: {len(customer_stats[customer_stats['Purchases'] == 1]):,}")
        print(f"   • Repeat Customers (2+ purchases): {len(customer_stats[customer_stats['Purchases'] > 1]):,}")
        
        # Visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Purchase frequency distribution
        axes[0, 0].hist(customer_stats['Purchases'], bins=50, color='#3498db', alpha=0.7, edgecolor='black')
        axes[0, 0].set_xlabel('Number of Purchases', fontweight='bold')
        axes[0, 0].set_ylabel('Number of Customers', fontweight='bold')
        axes[0, 0].set_title('Customer Purchase Frequency Distribution', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Total spending distribution
        axes[0, 1].hist(customer_stats['TotalSpent'], bins=50, color='#2ecc71', alpha=0.7, edgecolor='black')
        axes[0, 1].set_xlabel('Total Spending (£)', fontweight='bold')
        axes[0, 1].set_ylabel('Number of Customers', fontweight='bold')
        axes[0, 1].set_title('Customer Total Spending Distribution', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Repeat vs One-time buyers
        one_time = len(customer_stats[customer_stats['Purchases'] == 1])
        repeat = len(customer_stats[customer_stats['Purchases'] > 1])
        axes[1, 0].pie([one_time, repeat], labels=['One-time Buyers', 'Repeat Customers'], 
                       autopct='%1.1f%%', colors=['#e74c3c', '#2ecc71'], startangle=90)
        axes[1, 0].set_title('One-time vs Repeat Customers', fontweight='bold')
        
        # Scatter: Purchases vs Spending
        axes[1, 1].scatter(customer_stats['Purchases'], customer_stats['TotalSpent'], 
                          alpha=0.5, s=50, color='#9b59b6')
        axes[1, 1].set_xlabel('Number of Purchases', fontweight='bold')
        axes[1, 1].set_ylabel('Total Spent (£)', fontweight='bold')
        axes[1, 1].set_title('Purchases vs Total Spending', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/06_customer_behavior.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/06_customer_behavior.png")
        plt.close()
    
    def revenue_distribution(self):
        """Analyze revenue distribution"""
        self.print_header("REVENUE DISTRIBUTION ANALYSIS")
        
        print(f"\n💰 Revenue Statistics:")
        print(f"   • Mean Transaction: £{self.df['TotalPrice'].mean():.2f}")
        print(f"   • Median Transaction: £{self.df['TotalPrice'].median():.2f}")
        print(f"   • Std Deviation: £{self.df['TotalPrice'].std():.2f}")
        print(f"   • Skewness: {self.df['TotalPrice'].skew():.2f}")
        
        # Visualization
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Histogram
        axes[0].hist(self.df['TotalPrice'], bins=100, color='#f39c12', alpha=0.7, edgecolor='black')
        axes[0].set_xlabel('Transaction Value (£)', fontweight='bold')
        axes[0].set_ylabel('Frequency', fontweight='bold')
        axes[0].set_title('Revenue Distribution', fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        axes[0].axvline(self.df['TotalPrice'].mean(), color='red', linestyle='--', 
                       label=f"Mean: £{self.df['TotalPrice'].mean():.2f}", linewidth=2)
        axes[0].axvline(self.df['TotalPrice'].median(), color='green', linestyle='--', 
                       label=f"Median: £{self.df['TotalPrice'].median():.2f}", linewidth=2)
        axes[0].legend()
        
        # Box plot
        axes[1].boxplot(self.df['TotalPrice'], vert=True)
        axes[1].set_ylabel('Transaction Value (£)', fontweight='bold')
        axes[1].set_title('Revenue Box Plot', fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('outputs/07_revenue_distribution.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/07_revenue_distribution.png")
        plt.close()
    
    def correlation_analysis(self):
        """Analyze correlations"""
        self.print_header("CORRELATION ANALYSIS")
        
        numeric_df = self.df[['Quantity', 'Price', 'TotalPrice']].copy()
        corr_matrix = numeric_df.corr()
        
        print("\n📈 Correlation Matrix:")
        print(corr_matrix)
        
        # Visualization
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=ax, cbar_kws={'label': 'Correlation'}, 
                   fmt='.3f', linewidths=1)
        ax.set_title('Correlation Matrix: Quantity, Price, TotalPrice', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('outputs/08_correlation_matrix.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/08_correlation_matrix.png")
        plt.close()
    
    def seasonal_trends(self):
        """Analyze seasonal trends"""
        self.print_header("SEASONAL TRENDS ANALYSIS")
        
        self.df['DayOfWeek'] = self.df['InvoiceDate'].dt.day_name()
        self.df['Hour'] = self.df['InvoiceDate'].dt.hour
        
        # Day of week analysis
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_sales = self.df.groupby('DayOfWeek')['TotalPrice'].sum().reindex(day_order)
        
        print(f"\n📅 Sales by Day of Week:")
        for day, revenue in daily_sales.items():
            print(f"   • {day}: £{revenue:,.2f}")
        
        # Visualization
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Day of week
        colors_days = plt.cm.Set3(np.linspace(0, 1, len(daily_sales)))
        axes[0].bar(range(len(daily_sales)), daily_sales.values, color=colors_days)
        axes[0].set_xticks(range(len(daily_sales)))
        axes[0].set_xticklabels(daily_sales.index, rotation=45, ha='right')
        axes[0].set_ylabel('Revenue (£)', fontweight='bold')
        axes[0].set_title('Sales by Day of Week', fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Hour of day
        hourly_sales = self.df.groupby('Hour')['TotalPrice'].sum()
        axes[1].plot(hourly_sales.index, hourly_sales.values, marker='o', 
                    color='#e74c3c', linewidth=2, markersize=6)
        axes[1].set_xlabel('Hour of Day', fontweight='bold')
        axes[1].set_ylabel('Revenue (£)', fontweight='bold')
        axes[1].set_title('Sales by Hour of Day', fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xticks(range(0, 24, 2))
        
        plt.tight_layout()
        plt.savefig('outputs/09_seasonal_trends.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/09_seasonal_trends.png")
        plt.close()
    
    def run_complete_eda(self):
        """Execute complete EDA"""
        print("\n" + "="*80)
        print("🚀 MODULE 3: EXPLORATORY DATA ANALYSIS")
        print("="*80)
        
        self.business_overview()
        self.monthly_sales_trends()
        self.top_products_analysis()
        self.revenue_products_analysis()
        self.country_analysis()
        self.top_customers_analysis()
        self.customer_behavior_analysis()
        self.revenue_distribution()
        self.correlation_analysis()
        self.seasonal_trends()
        
        print("\n" + "="*80)
        print("✅ EDA COMPLETE!")
        print("="*80)
        print("📊 All visualizations saved to outputs/ directory")


def main():
    """Main execution"""
    analyzer = EDAnalyzer('outputs/online_retail_cleaned.csv')
    analyzer.run_complete_eda()


if __name__ == "__main__":
    main()
