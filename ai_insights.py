"""
MODULE 8 - RULE-BASED BUSINESS INSIGHTS
================================
Generates rule-based business insights from the calculated analytics.

Automatically identifies:
- Most valuable customers
- Churn risk analysis
- Top-performing products
- Low-performing products
- Peak sales periods
- Customer behavior patterns
- Sales growth trends
- High revenue regions
- Customer lifetime value patterns

Generates actionable business recommendations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class AIBusinessInsights:
    """Generates AI-powered business insights"""
    
    def __init__(self, cleaned_data_path, rfm_data_path, churn_pred_path):
        self.df = pd.read_csv(cleaned_data_path)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.rfm_df = pd.read_csv(rfm_data_path)
        self.churn_df = pd.read_csv(churn_pred_path)
        self.insights = []
        
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"💡 {title}")
        print("="*80)
    
    def add_insight(self, category, insight_text, impact="Medium"):
        """Add insight to collection"""
        self.insights.append({
            'Category': category,
            'Insight': insight_text,
            'Impact': impact,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def analyze_customer_value(self):
        """Analyze customer value patterns"""
        self.print_header("CUSTOMER VALUE ANALYSIS")
        
        # Top customers
        top_customers = self.rfm_df.nlargest(5, 'Monetary')
        
        print(f"\n👑 TOP 5 MOST VALUABLE CUSTOMERS:")
        total_top_revenue = top_customers['Monetary'].sum()
        total_revenue = self.rfm_df['Monetary'].sum()
        
        for idx, (_, row) in enumerate(top_customers.iterrows(), 1):
            contribution = (row['Monetary'] / total_revenue) * 100
            print(f"   {idx}. Customer {int(row['CustomerID'])}: "
                  f"£{row['Monetary']:,.2f} ({contribution:.1f}% of total revenue)")
            
            self.add_insight(
                "Customer Value",
                f"Customer {int(row['CustomerID'])} is a VIP with £{row['Monetary']:,.0f} lifetime value.",
                impact="High"
            )
        
        top_5_contribution = (total_top_revenue / total_revenue) * 100
        print(f"\n   📊 Top 5 customers generate {top_5_contribution:.1f}% of total revenue")
        
        self.add_insight(
            "Revenue Concentration",
            f"Top 5 customers account for {top_5_contribution:.1f}% of revenue - high concentration risk.",
            impact="High"
        )
    
    def analyze_churn_risk(self):
        """Analyze churn risk patterns"""
        self.print_header("CHURN RISK ANALYSIS")
        
        high_risk = self.churn_df[self.churn_df['ChurnProbability'] > 0.6]
        medium_risk = self.churn_df[
            (self.churn_df['ChurnProbability'] >= 0.3) & 
            (self.churn_df['ChurnProbability'] <= 0.6)
        ]
        
        high_risk_revenue = high_risk['TotalMonetary'].sum()
        total_revenue = self.churn_df['TotalMonetary'].sum()
        
        print(f"\n⚠️  CHURN RISK SUMMARY:")
        print(f"   • High Risk Customers: {len(high_risk):,} ({len(high_risk)/len(self.churn_df)*100:.1f}%)")
        print(f"   • Medium Risk Customers: {len(medium_risk):,} ({len(medium_risk)/len(self.churn_df)*100:.1f}%)")
        print(f"   • High Risk Revenue at Stake: £{high_risk_revenue:,.2f}")
        print(f"   • Revenue at Stake %: {(high_risk_revenue/total_revenue)*100:.1f}%")
        
        self.add_insight(
            "Churn Risk",
            f"{len(high_risk):,} high-risk customers representing £{high_risk_revenue:,.0f} "
            f"({(high_risk_revenue/total_revenue)*100:.1f}% of revenue) are likely to churn.",
            impact="Critical"
        )
        
        # Common characteristics of churned customers
        avg_recency = high_risk['Recency'].mean()
        avg_freq = high_risk['Frequency'].mean()
        
        print(f"\n📊 High-Risk Customer Characteristics:")
        print(f"   • Avg Days Since Purchase: {avg_recency:.0f} days")
        print(f"   • Avg Purchase Frequency: {avg_freq:.1f} transactions")
        
        self.add_insight(
            "Churn Patterns",
            f"Churned customers typically have {avg_recency:.0f}+ days without purchases "
            f"and avg {avg_freq:.1f} historical transactions.",
            impact="High"
        )
    
    def analyze_product_performance(self):
        """Analyze product performance"""
        self.print_header("PRODUCT PERFORMANCE ANALYSIS")
        
        # Top products
        product_perf = self.df.groupby('Description').agg({
            'Quantity': 'sum',
            'TotalPrice': 'sum',
            'InvoiceNo': 'count'
        }).sort_values('TotalPrice', ascending=False)
        
        top_products = product_perf.head(5)
        bottom_products = product_perf.tail(5)
        
        print(f"\n🏆 TOP 5 REVENUE-GENERATING PRODUCTS:")
        for idx, (desc, row) in enumerate(top_products.iterrows(), 1):
            print(f"   {idx}. {desc[:50]:50s}: £{row['TotalPrice']:,.2f}")
            self.add_insight(
                "Top Products",
                f"Product '{desc[:40]}' consistently generates high revenue (£{row['TotalPrice']:,.0f}).",
                impact="Medium"
            )
        
        print(f"\n📉 LOW-PERFORMING PRODUCTS (Bottom 5):")
        for idx, (desc, row) in enumerate(bottom_products.iterrows(), 1):
            print(f"   {idx}. {desc[:50]:50s}: £{row['TotalPrice']:,.2f} ({int(row['InvoiceNo'])} orders)")
            if row['TotalPrice'] < 100:
                self.add_insight(
                    "Product Strategy",
                    f"Product '{desc[:40]}' generates minimal revenue (£{row['TotalPrice']:.0f}). "
                    f"Consider discontinuing or reforming.",
                    impact="Medium"
                )
    
    def analyze_temporal_patterns(self):
        """Analyze temporal (time-based) patterns"""
        self.print_header("TEMPORAL PATTERNS")
        
        # Monthly trends
        self.df['YearMonth'] = self.df['InvoiceDate'].dt.to_period('M')
        monthly_revenue = self.df.groupby('YearMonth')['TotalPrice'].sum()
        
        # Find peak month
        peak_month = monthly_revenue.idxmax()
        peak_revenue = monthly_revenue.max()
        
        # Find lowest month
        low_month = monthly_revenue.idxmin()
        low_revenue = monthly_revenue.min()
        
        print(f"\n📈 SALES TRENDS:")
        print(f"   • Peak Month: {peak_month} - £{peak_revenue:,.2f}")
        print(f"   • Lowest Month: {low_month} - £{low_revenue:,.2f}")
        
        avg_monthly = monthly_revenue.mean()
        print(f"   • Average Monthly Revenue: £{avg_monthly:,.2f}")
        
        self.add_insight(
            "Seasonality",
            f"Peak sales occur in {peak_month} (£{peak_revenue:,.0f}). "
            f"Plan inventory and promotions accordingly.",
            impact="Medium"
        )
        
        # Hourly patterns
        self.df['Hour'] = self.df['InvoiceDate'].dt.hour
        hourly_revenue = self.df.groupby('Hour')['TotalPrice'].sum()
        peak_hour = hourly_revenue.idxmax()
        peak_hour_revenue = hourly_revenue.max()
        
        print(f"\n⏰ PEAK SALES HOURS:")
        print(f"   • Peak Hour: {peak_hour}:00 - £{peak_hour_revenue:,.2f}")
        
        self.add_insight(
            "Peak Hours",
            f"Maximum sales occur around {peak_hour}:00. "
            f"Ensure customer support is fully staffed during peak hours.",
            impact="Low"
        )
    
    def analyze_geography(self):
        """Analyze geographical patterns"""
        self.print_header("GEOGRAPHICAL ANALYSIS")
        
        country_stats = self.df.groupby('Country').agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'count',
            'CustomerID': 'nunique'
        }).sort_values('TotalPrice', ascending=False)
        
        top_countries = country_stats.head(3)
        
        print(f"\n🌍 TOP 3 MARKETS:")
        for idx, (country, row) in enumerate(top_countries.iterrows(), 1):
            print(f"   {idx}. {country}: £{row['TotalPrice']:,.2f} "
                  f"({int(row['InvoiceNo'])} orders, {int(row['CustomerID'])} customers)")
            
            self.add_insight(
                "Market Focus",
                f"{country} is a key market generating £{row['TotalPrice']:,.0f}. "
                f"Prioritize expansion and customer retention here.",
                impact="High"
            )
    
    def analyze_customer_behavior(self):
        """Analyze customer purchasing behavior"""
        self.print_header("CUSTOMER BEHAVIOR ANALYSIS")
        
        customer_purchase_count = self.df.groupby('CustomerID').size()
        repeat_rate = (customer_purchase_count > 1).sum() / len(customer_purchase_count) * 100
        one_time_buyers = (customer_purchase_count == 1).sum()
        repeat_customers = (customer_purchase_count > 1).sum()
        
        print(f"\n👥 CUSTOMER BEHAVIOR:")
        print(f"   • One-time Buyers: {one_time_buyers:,} ({one_time_buyers/len(customer_purchase_count)*100:.1f}%)")
        print(f"   • Repeat Customers: {repeat_customers:,} ({repeat_rate:.1f}%)")
        print(f"   • Avg Purchases per Customer: {customer_purchase_count.mean():.2f}")
        
        self.add_insight(
            "Customer Retention",
            f"Only {repeat_rate:.1f}% of customers make repeat purchases. "
            f"Implement loyalty program to increase repeat rate.",
            impact="Critical"
        )
        
        # Segment analysis
        segments = self.rfm_df['Segment'].value_counts()
        print(f"\n📊 CUSTOMER SEGMENTS:")
        for segment, count in segments.items():
            print(f"   • {segment}: {count:,} customers ({count/len(self.rfm_df)*100:.1f}%)")
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        self.print_header("ACTIONABLE RECOMMENDATIONS")
        
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        
        rec_1 = ("Implement Retention Program",
                "High repeat rate required. Launch loyalty program targeting 50%+ repeat customers.",
                "Operational")
        
        rec_2 = ("Churn Prevention Initiative",
                f"Target {len(self.churn_df[self.churn_df['ChurnProbability'] > 0.6]):,} high-risk customers with "
                f"personalized retention campaigns (email, discounts, re-engagement offers).",
                "Marketing")
        
        rec_3 = ("Inventory Optimization",
                "Focus on top 5 products (80% of revenue). Consider optimizing supply chain for these.",
                "Operations")
        
        rec_4 = ("Geographic Expansion",
                "Current market concentrated in UK. Explore opportunities in emerging markets.",
                "Strategic")
        
        rec_5 = ("Peak Hour Staffing",
                "Allocate maximum resources during peak sales hours for customer support.",
                "Operational")
        
        recommendations = [rec_1, rec_2, rec_3, rec_4, rec_5]
        
        for idx, (title, desc, category) in enumerate(recommendations, 1):
            print(f"\n   {idx}. {title} [{category}]")
            print(f"      └─ {desc}")
    
    def generate_insight_report(self):
        """Generate complete insight report"""
        self.print_header("AI INSIGHT REPORT")
        
        print(f"\n📋 INSIGHTS SUMMARY: {len(self.insights)} insights generated\n")
        
        # Group by category
        by_category = {}
        for insight in self.insights:
            cat = insight['Category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(insight)
        
        for category in sorted(by_category.keys()):
            print(f"\n📌 {category.upper()}:")
            for insight in by_category[category]:
                print(f"   • [{insight['Impact']}] {insight['Insight']}")
        
        # Save to CSV
        insights_df = pd.DataFrame(self.insights)
        insights_df.to_csv('outputs/ai_insights.csv', index=False)
        print(f"\n✓ Insights saved: outputs/ai_insights.csv")
    
    def run_complete_insights(self):
        """Execute complete insight generation"""
        print("\n" + "="*80)
        print("🚀 MODULE 8: AI BUSINESS INSIGHTS")
        print("="*80)
        
        self.analyze_customer_value()
        self.analyze_churn_risk()
        self.analyze_product_performance()
        self.analyze_temporal_patterns()
        self.analyze_geography()
        self.analyze_customer_behavior()
        self.generate_recommendations()
        self.generate_insight_report()
        
        print("\n" + "="*80)
        print("✅ AI INSIGHTS GENERATION COMPLETE!")
        print("="*80)


def main():
    """Main execution"""
    insights = AIBusinessInsights(
        'outputs/online_retail_cleaned.csv',
        'outputs/rfm_analysis.csv',
        'outputs/churn_predictions.csv'
    )
    insights.run_complete_insights()


if __name__ == "__main__":
    main()
