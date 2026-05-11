"""
MODULE 6 - RFM CUSTOMER ANALYSIS
=================================
Recency, Frequency, Monetary analysis for customer segmentation.

RFM Metrics:
- Recency: Days since last purchase
- Frequency: Number of transactions
- Monetary: Total spending

Customer Segments:
- Champions: High R, F, M
- Loyal Customers: High F, M
- Potential Loyalists: High R, F, M (new)
- New Customers: High R
- At Risk: Low R, Low F
- Lost Customers: Very Low R
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")


class RFMAnalyzer:
    """Performs RFM analysis for customer segmentation"""
    
    def __init__(self, cleaned_data_path):
        self.df = pd.read_csv(cleaned_data_path)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.rfm_df = None
        self.segmentation_df = None
        
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"🔍 {title}")
        print("="*80)
    
    def calculate_rfm_metrics(self):
        """Calculate RFM metrics for each customer"""
        print("\n" + "="*80)
        print("📊 CALCULATING RFM METRICS")
        print("="*80)
        
        # Reference date (latest date in dataset + 1 day)
        reference_date = self.df['InvoiceDate'].max() + timedelta(days=1)
        print(f"\n📅 Reference Date: {reference_date.date()}")
        print(f"   (Latest transaction in dataset: {self.df['InvoiceDate'].max().date()})")
        
        # Calculate RFM metrics
        rfm_df = self.df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
            'InvoiceNo': 'count',  # Frequency
            'TotalPrice': 'sum'    # Monetary
        }).reset_index()
        
        rfm_df.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        
        print(f"\n✓ Calculated metrics for {len(rfm_df):,} customers")
        print(f"\n📈 RFM Metrics Summary:")
        print(rfm_df[['Recency', 'Frequency', 'Monetary']].describe().round(2))
        
        self.rfm_df = rfm_df
        return rfm_df
    
    def assign_rfm_scores(self, num_tiers=5):
        """Assign RFM scores based on quartiles"""
        print(f"\n🏆 ASSIGNING RFM SCORES (Tiers: {num_tiers})")
        
        # Recency: Lower is better, so reverse the ranking
        self.rfm_df['R_Score'] = pd.qcut(
            self.rfm_df['Recency'], 
            q=num_tiers, 
            labels=range(num_tiers, 0, -1),
            duplicates='drop'
        ).astype(int)
        
        # Frequency: Higher is better
        self.rfm_df['F_Score'] = pd.qcut(
            self.rfm_df['Frequency'], 
            q=num_tiers, 
            labels=range(1, num_tiers + 1),
            duplicates='drop'
        ).astype(int)
        
        # Monetary: Higher is better
        self.rfm_df['M_Score'] = pd.qcut(
            self.rfm_df['Monetary'], 
            q=num_tiers, 
            labels=range(1, num_tiers + 1),
            duplicates='drop'
        ).astype(int)
        
        # Combined RFM score
        self.rfm_df['RFM_Score'] = (
            self.rfm_df['R_Score'].astype(str) +
            self.rfm_df['F_Score'].astype(str) +
            self.rfm_df['M_Score'].astype(str)
        )
        
        print("✓ RFM scores assigned")
        print(f"\n📊 Score Distribution:")
        print(f"   • R_Score (Recency): {sorted(self.rfm_df['R_Score'].unique())}")
        print(f"   • F_Score (Frequency): {sorted(self.rfm_df['F_Score'].unique())}")
        print(f"   • M_Score (Monetary): {sorted(self.rfm_df['M_Score'].unique())}")
    
    def segment_customers(self):
        """Segment customers based on RFM scores"""
        print("\n" + "="*80)
        print("🎯 CUSTOMER SEGMENTATION")
        print("="*80)
        
        def assign_segment(row):
            """Assign customer segment based on RFM scores"""
            r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
            
            # Champions
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            # Loyal Customers
            elif f >= 4 and m >= 3:
                return 'Loyal Customers'
            # Potential Loyalists
            elif r >= 4 and f >= 3 and m >= 2:
                return 'Potential Loyalists'
            # New Customers
            elif r >= 4 and f <= 2:
                return 'New Customers'
            # At Risk
            elif r <= 2 and f >= 2:
                return 'At Risk Customers'
            # Lost Customers
            elif r <= 2 and f <= 2:
                return 'Lost Customers'
            else:
                return 'Other'
        
        self.rfm_df['Segment'] = self.rfm_df.apply(assign_segment, axis=1)
        
        print("\n✓ Customers segmented")
        
        # Segment statistics
        segment_stats = self.rfm_df.groupby('Segment').agg({
            'CustomerID': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': ['mean', 'sum']
        }).round(2)
        
        segment_stats.columns = ['Customers', 'Avg_Recency', 'Avg_Frequency', 
                                 'Avg_Spending', 'Total_Revenue']
        segment_stats = segment_stats.sort_values('Total_Revenue', ascending=False)
        
        print("\n📊 Segment Statistics:")
        print(segment_stats.to_string())
        
        return segment_stats
    
    def display_segment_details(self):
        """Display detailed information about each segment"""
        self.print_header("DETAILED SEGMENT ANALYSIS")
        
        segments = self.rfm_df['Segment'].unique()
        
        for segment in sorted(segments):
            segment_data = self.rfm_df[self.rfm_df['Segment'] == segment]
            
            print(f"\n{'─'*80}")
            print(f"📌 {segment.upper()}")
            print(f"{'─'*80}")
            print(f"   • Customers: {len(segment_data):,}")
            print(f"   • Percentage: {(len(segment_data)/len(self.rfm_df)*100):.1f}%")
            print(f"   • Avg Recency: {segment_data['Recency'].mean():.0f} days")
            print(f"   • Avg Frequency: {segment_data['Frequency'].mean():.1f} purchases")
            print(f"   • Avg Spending: £{segment_data['Monetary'].mean():.2f}")
            print(f"   • Total Revenue: £{segment_data['Monetary'].sum():,.2f}")
            print(f"   • Revenue %: {(segment_data['Monetary'].sum()/self.rfm_df['Monetary'].sum()*100):.1f}%")
            
            # Top customers in segment
            top_cust = segment_data.nlargest(3, 'Monetary')[['CustomerID', 'Recency', 'Frequency', 'Monetary']]
            print(f"\n   Top 3 Customers:")
            for idx, (_, row) in enumerate(top_cust.iterrows(), 1):
                print(f"      {idx}. Customer {int(row['CustomerID'])}: "
                      f"£{row['Monetary']:.2f}, {int(row['Frequency'])} purchases")
    
    def visualize_segments(self):
        """Create segment visualizations"""
        print("\n" + "="*80)
        print("📊 CREATING VISUALIZATIONS")
        print("="*80)
        
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Segment distribution by count
        ax1 = plt.subplot(2, 3, 1)
        segment_counts = self.rfm_df['Segment'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(segment_counts)))
        segment_counts.plot(kind='bar', ax=ax1, color=colors)
        ax1.set_title('Customer Count by Segment', fontweight='bold', fontsize=12)
        ax1.set_xlabel('Segment')
        ax1.set_ylabel('Number of Customers')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Segment distribution by revenue
        ax2 = plt.subplot(2, 3, 2)
        segment_revenue = self.rfm_df.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)
        colors2 = plt.cm.RdYlGn(np.linspace(0, 1, len(segment_revenue)))
        segment_revenue.plot(kind='bar', ax=ax2, color=colors2)
        ax2.set_title('Total Revenue by Segment', fontweight='bold', fontsize=12)
        ax2.set_xlabel('Segment')
        ax2.set_ylabel('Total Revenue (£)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Pie chart - percentage distribution
        ax3 = plt.subplot(2, 3, 3)
        segment_pct = (self.rfm_df['Segment'].value_counts() / len(self.rfm_df) * 100)
        colors3 = plt.cm.Pastel1(np.linspace(0, 1, len(segment_pct)))
        ax3.pie(segment_pct.values, labels=segment_pct.index, autopct='%1.1f%%',
               colors=colors3, startangle=90)
        ax3.set_title('Customer Percentage Distribution', fontweight='bold', fontsize=12)
        
        # 4. RFM Score distribution
        ax4 = plt.subplot(2, 3, 4)
        segment_avg_recency = self.rfm_df.groupby('Segment')['Recency'].mean()
        segment_avg_frequency = self.rfm_df.groupby('Segment')['Frequency'].mean()
        x = np.arange(len(segment_avg_recency))
        width = 0.35
        ax4.bar(x - width/2, segment_avg_recency.values, width, label='Avg Recency', alpha=0.8)
        ax4.bar(x + width/2, segment_avg_frequency.values, width, label='Avg Frequency', alpha=0.8)
        ax4.set_xlabel('Segment')
        ax4.set_ylabel('Value')
        ax4.set_title('Recency vs Frequency by Segment', fontweight='bold', fontsize=12)
        ax4.set_xticks(x)
        ax4.set_xticklabels(segment_avg_recency.index, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. Scatter plot: Recency vs Monetary
        ax5 = plt.subplot(2, 3, 5)
        for segment in self.rfm_df['Segment'].unique():
            segment_data = self.rfm_df[self.rfm_df['Segment'] == segment]
            ax5.scatter(segment_data['Recency'], segment_data['Monetary'], 
                       label=segment, alpha=0.6, s=50)
        ax5.set_xlabel('Recency (days)')
        ax5.set_ylabel('Monetary Value (£)')
        ax5.set_title('Recency vs Monetary Value', fontweight='bold', fontsize=12)
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3)
        
        # 6. Box plot: Monetary by Segment
        ax6 = plt.subplot(2, 3, 6)
        segment_data_list = [self.rfm_df[self.rfm_df['Segment'] == seg]['Monetary'].values 
                            for seg in sorted(self.rfm_df['Segment'].unique())]
        bp = ax6.boxplot(segment_data_list, labels=sorted(self.rfm_df['Segment'].unique()),
                        patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('#87CEEB')
        ax6.set_xlabel('Segment')
        ax6.set_ylabel('Monetary Value (£)')
        ax6.set_title('Revenue Distribution by Segment', fontweight='bold', fontsize=12)
        ax6.tick_params(axis='x', rotation=45)
        ax6.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('outputs/10_rfm_segmentation.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: outputs/10_rfm_segmentation.png")
        plt.close()
    
    def save_rfm_data(self):
        """Save RFM analysis results"""
        print("\n" + "="*80)
        print("💾 SAVING RFM DATA")
        print("="*80)
        
        # Save full RFM data
        output_path = 'outputs/rfm_analysis.csv'
        self.rfm_df.to_csv(output_path, index=False)
        print(f"✓ Saved RFM analysis: {output_path}")
        
        # Save segment summary
        segment_summary = self.rfm_df.groupby('Segment').agg({
            'CustomerID': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': ['mean', 'sum']
        }).round(2)
        
        segment_summary.to_csv('outputs/segment_summary.csv')
        print("✓ Saved segment summary: outputs/segment_summary.csv")
    
    def run_complete_rfm(self):
        """Execute complete RFM analysis"""
        print("\n" + "="*80)
        print("🚀 MODULE 6: RFM CUSTOMER ANALYSIS")
        print("="*80)
        
        # Calculate metrics
        self.calculate_rfm_metrics()
        
        # Assign scores
        self.assign_rfm_scores(num_tiers=5)
        
        # Segment customers
        segment_stats = self.segment_customers()
        
        # Display details
        self.display_segment_details()
        
        # Visualize
        self.visualize_segments()
        
        # Save results
        self.save_rfm_data()
        
        print("\n" + "="*80)
        print("✅ RFM ANALYSIS COMPLETE!")
        print("="*80)
        
        return self.rfm_df


def main():
    """Main execution"""
    analyzer = RFMAnalyzer('outputs/online_retail_cleaned.csv')
    analyzer.run_complete_rfm()


if __name__ == "__main__":
    main()
