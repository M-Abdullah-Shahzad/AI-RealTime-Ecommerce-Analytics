"""
MODULE 10 - STREAMLIT DASHBOARD
================================
Interactive dashboard for precomputed batch analytics and customer intelligence.

Features:
- Sales and customer analytics
- Historical inactivity classification
- RFM customer segments
- Sales insights
- Interactive filters and charts
- Business metrics
- Association-rule product recommendations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pickle
import warnings
warnings.filterwarnings('ignore')


# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load all required data"""
    try:
        df_clean = pd.read_csv('outputs/online_retail_cleaned.csv')
        df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
        
        rfm_df = pd.read_csv('outputs/rfm_analysis.csv')
        churn_df = pd.read_csv('outputs/churn_predictions.csv')
        insights_df = pd.read_csv('outputs/ai_insights.csv')
        rules_df = pd.read_csv('outputs/association_rules.csv')
        
        return df_clean, rfm_df, churn_df, insights_df, rules_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None


def sidebar_filters(df_clean):
    """Create sidebar filters"""
    st.sidebar.title("🎛️ Filters")
    
    with st.sidebar.container():
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(datetime(2010, 12, 1), datetime(2011, 12, 9)),
            key="date_range"
        )
        
        countries = st.sidebar.multiselect(
            "Select Countries",
            ["All"] + sorted(df_clean['Country'].unique().tolist()),
            default=["All"]
        )
        
        return date_range, countries


def apply_filters(df, date_range, countries):
    """Apply selected filters to dataframe"""
    if len(date_range) < 2:
        return df

    df_filtered = df[
        (df['InvoiceDate'].dt.date >= date_range[0]) &
        (df['InvoiceDate'].dt.date <= date_range[1])
    ]
    
    if "All" not in countries:
        df_filtered = df_filtered[df_filtered['Country'].isin(countries)]
    
    return df_filtered


def display_kpis(df_filtered):
    """Display key performance indicators"""
    st.markdown("## 📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_revenue = df_filtered['TotalPrice'].sum()
        st.metric("Total Revenue", f"£{total_revenue:,.0f}")
    
    with col2:
        total_orders = len(df_filtered)
        st.metric("Total Orders", f"{total_orders:,}")
    
    with col3:
        unique_customers = df_filtered['CustomerID'].nunique()
        st.metric("Unique Customers", f"{unique_customers:,}")
    
    with col4:
        avg_order_value = df_filtered['TotalPrice'].mean()
        st.metric("Avg Order Value", f"£{avg_order_value:.2f}")
    
    with col5:
        unique_products = df_filtered['StockCode'].nunique()
        st.metric("Unique Products", f"{unique_products:,}")


def display_sales_analytics(df_filtered):
    """Display sales analytics"""
    st.markdown("## 📈 Sales Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly sales trend
        df_monthly = df_filtered.copy()
        df_monthly['YearMonth'] = df_monthly['InvoiceDate'].dt.to_period('M')
        monthly_sales = df_monthly.groupby('YearMonth')['TotalPrice'].sum().reset_index()
        monthly_sales['YearMonth'] = monthly_sales['YearMonth'].astype(str)
        
        fig_monthly = px.line(
            monthly_sales,
            x='YearMonth',
            y='TotalPrice',
            title='Monthly Sales Revenue',
            labels={'TotalPrice': 'Revenue (£)', 'YearMonth': 'Month'},
            markers=True
        )
        fig_monthly.update_layout(height=400)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Top products
        top_products = df_filtered.groupby('Description')['TotalPrice'].sum().nlargest(10).reset_index()
        top_products = top_products.sort_values('TotalPrice', ascending=True)
        
        fig_products = px.bar(
            top_products,
            x='TotalPrice',
            y='Description',
            title='Top 10 Products by Revenue',
            labels={'TotalPrice': 'Revenue (£)', 'Description': 'Product'},
            orientation='h'
        )
        fig_products.update_layout(height=400)
        st.plotly_chart(fig_products, use_container_width=True)


def display_customer_analytics(rfm_df):
    """Display customer analytics"""
    st.markdown("## 👥 Customer Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # RFM Segments
        segment_counts = rfm_df['Segment'].value_counts()
        fig_segments = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title='Customer Segments (RFM)',
            hole=0.3
        )
        fig_segments.update_layout(height=400)
        st.plotly_chart(fig_segments, use_container_width=True)
    
    with col2:
        # Top customers
        top_customers = rfm_df.nlargest(10, 'Monetary')[['CustomerID', 'Monetary']].sort_values('Monetary', ascending=True)
        top_customers['CustomerID'] = top_customers['CustomerID'].astype(str)
        
        fig_customers = px.bar(
            top_customers,
            x='Monetary',
            y='CustomerID',
            title='Top 10 Customers by Lifetime Value',
            labels={'Monetary': 'Total Spending (£)', 'CustomerID': 'Customer ID'},
            orientation='h'
        )
        fig_customers.update_layout(height=400)
        st.plotly_chart(fig_customers, use_container_width=True)


def display_churn_analytics(churn_df):
    """Display churn prediction analytics"""
    st.markdown("## ⚠️ Churn Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_risk = len(churn_df[churn_df['ChurnProbability'] > 0.6])
        st.metric("High Risk Customers", f"{high_risk:,}")
    
    with col2:
        at_risk_revenue = churn_df[churn_df['ChurnProbability'] > 0.6]['TotalMonetary'].sum()
        st.metric("Revenue at Risk", f"£{at_risk_revenue:,.0f}")
    
    with col3:
        churn_rate = (churn_df['ChurnProbability'].mean()) * 100
        st.metric("Avg Churn Probability", f"{churn_rate:.1f}%")
    
    # Churn distribution
    fig_churn_dist = px.histogram(
        churn_df,
        x='ChurnProbability',
        nbins=30,
        title='Churn Probability Distribution',
        labels={'ChurnProbability': 'Churn Probability', 'count': 'Number of Customers'},
        color_discrete_sequence=['#FF6B6B']
    )
    fig_churn_dist.update_layout(height=400)
    st.plotly_chart(fig_churn_dist, use_container_width=True)
    
    # High-risk customers table
    st.markdown("### High-Risk Customers (Churn Probability > 60%)")
    high_risk_df = churn_df[churn_df['ChurnProbability'] > 0.6].nlargest(10, 'ChurnProbability')[
        ['CustomerID', 'Recency', 'Frequency', 'TotalMonetary', 'ChurnProbability']
    ]
    
    st.dataframe(
        high_risk_df.assign(**{'ChurnProbability': high_risk_df['ChurnProbability'].apply(lambda x: f"{x:.1%}")}),
        use_container_width=True
    )


def display_geographical_analytics(df_filtered):
    """Display geographical analytics"""
    st.markdown("## 🌍 Geographical Analytics")
    
    country_sales = df_filtered.groupby('Country').agg({
        'TotalPrice': 'sum',
        'InvoiceNo': 'count',
        'CustomerID': 'nunique'
    }).reset_index()
    country_sales.columns = ['Country', 'Revenue', 'Orders', 'Customers']
    country_sales = country_sales.nlargest(20, 'Revenue')
    
    fig_geo = px.bar(
        country_sales,
        x='Country',
        y='Revenue',
        hover_data=['Orders', 'Customers'],
        title='Top 20 Countries by Revenue',
        labels={'Revenue': 'Revenue (£)', 'Country': 'Country'},
        color='Revenue',
        color_continuous_scale='Viridis'
    )
    fig_geo.update_layout(height=400)
    st.plotly_chart(fig_geo, use_container_width=True)


def display_ai_insights(insights_df):
    """Display rule-based business insights"""
    st.markdown("## 💡 Rule-based Business Insights")
    
    # Filter insights by category
    category = st.selectbox(
        "Filter by Category",
        ["All"] + sorted(insights_df['Category'].unique().tolist())
    )
    
    if category == "All":
        filtered_insights = insights_df
    else:
        filtered_insights = insights_df[insights_df['Category'] == category]
    
    # Display insights by impact
    for impact in ['Critical', 'High', 'Medium', 'Low']:
        impact_insights = filtered_insights[filtered_insights['Impact'] == impact]
        
        if len(impact_insights) > 0:
            st.markdown(f"### {impact} Impact")
            for _, row in impact_insights.iterrows():
                with st.container():
                    col1, col2 = st.columns([0.1, 0.9])
                    with col1:
                        if impact == 'Critical':
                            st.error("⚠️", )
                        elif impact == 'High':
                            st.warning("🔴")
                        elif impact == 'Medium':
                            st.info("🟡")
                        else:
                            st.success("🟢")
                    with col2:
                        st.markdown(f"**{row['Category']}:** {row['Insight']}")


def display_recommendations(rules_df):
    """Display product recommendations"""
    st.markdown("## 🎁 Product Recommendations")
    
    # Select a product for recommendations
    products = rules_df['antecedent_str'].unique()[:20]
    selected_product = st.selectbox("Select a Product:", products)
    
    # Get recommendations
    recommendations = rules_df[rules_df['antecedent_str'] == selected_product].nlargest(5, 'lift')
    
    if len(recommendations) > 0:
        st.markdown(f"### Customers buying '{selected_product}' also buy:")
        
        for idx, (_, row) in enumerate(recommendations.iterrows(), 1):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(f"#{idx}", row['consequent_str'][:20])
            with col2:
                st.metric("Lift", f"{row['lift']:.2f}")
            with col3:
                st.metric("Confidence", f"{row['confidence']:.1%}")
            with col4:
                st.metric("Support", f"{row['support']:.3f}")
    else:
        st.info("No recommendations available for this product")


def main():
    """Main dashboard application"""
    st.title("🏪 E-commerce Analytics Dashboard")
    st.markdown("**Batch Sales Analytics, Customer Segmentation & Inactivity Analysis**")
    
    # Load data
    df_clean, rfm_df, churn_df, insights_df, rules_df = load_data()
    
    if df_clean is None:
        st.error("Failed to load data. Please ensure all output files are present.")
        return
    
    # Sidebar filters
    date_range, countries = sidebar_filters(df_clean)
    df_filtered = apply_filters(df_clean, date_range, countries)
    
    # Navigation
    st.sidebar.markdown("---")
    nav_option = st.sidebar.radio(
        "📍 Navigation",
        ["Dashboard", "Sales Analytics", "Customer Analytics", "Churn Analysis", 
         "Insights", "Recommendations"]
    )
    
    # Display selected page
    if nav_option == "Dashboard":
        display_kpis(df_filtered)
        st.markdown("---")
        display_sales_analytics(df_filtered)
        st.markdown("---")
        display_geographical_analytics(df_filtered)
    
    elif nav_option == "Sales Analytics":
        display_sales_analytics(df_filtered)
    
    elif nav_option == "Customer Analytics":
        display_customer_analytics(rfm_df)
    
    elif nav_option == "Churn Analysis":
        display_churn_analytics(churn_df)
    
    elif nav_option == "Insights":
        display_ai_insights(insights_df)
    
    elif nav_option == "Recommendations":
        display_recommendations(rules_df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
        <p>🚀 AI-Powered E-Commerce Analytics Platform</p>
        <p style='font-size: 0.8rem; color: gray;'>
        Built with Streamlit | Data: Online Retail II Dataset
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
