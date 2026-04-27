# app.py - COMPLETE FARM INTELLIGENCE PLATFORM (ALL CHARTS INCLUDED)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Nile.ag - Farm Intelligence Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        animation: fadeIn 1s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .metric-card {
        background: linear-gradient(135deg, #2E7D32, #4CAF50);
        padding: 0.8rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        transition: transform 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .decision-card {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .decision-card:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .urgent-card {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #e74c3c;
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { border-left-color: #e74c3c; }
        50% { border-left-color: #ff6b6b; }
        100% { border-left-color: #e74c3c; }
    }
    .warning-card {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
        background-color: #f0f2f6;
        padding: 0.3rem;
        border-radius: 12px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.3rem 0.8rem;
        font-weight: 600;
        font-size: 0.8rem;
        transition: background 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #d0d2d6;
    }
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        border-radius: 20px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def format_currency(value):
    if pd.isna(value) or value is None:
        return "R0"
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        formatted = f"R{abs_value/1_000_000:.1f}M"
    elif abs_value >= 1_000:
        formatted = f"R{abs_value/1_000:.1f}K"
    else:
        formatted = f"R{abs_value:,.0f}"
    if value < 0:
        formatted = f"-{formatted}"
    return formatted

def parse_markets(markets_str):
    try:
        if pd.isna(markets_str) or markets_str == '':
            return []
        parts = str(markets_str).split(' | ')
        result = []
        for p in parts:
            if ': R' in p:
                parts_split = p.split(': R')
                if len(parts_split) >= 2:
                    result.append({'market': parts_split[0].strip(), 'revenue': float(parts_split[1].replace(',', ''))})
        return result
    except:
        return []

def safe_size_for_plot(values, min_size=8, max_size=50):
    """Convert values to positive sizes for plotting"""
    values = np.array(values)
    # Take absolute values
    abs_values = np.abs(values)
    # If all zeros or constant, return constant size
    if abs_values.max() == abs_values.min():
        return [max_size/2] * len(abs_values)
    # Normalize to range
    normalized = min_size + (abs_values - abs_values.min()) / (abs_values.max() - abs_values.min()) * (max_size - min_size)
    return normalized

@st.cache_data(ttl=3600)
def load_data():
    if os.path.exists("nile_farm_intelligence.csv"):
        df = pd.read_csv("nile_farm_intelligence.csv", parse_dates=["harvest_date"])
        
        # Create calculated fields for missing columns
        if 'current_market_price_estimate' not in df.columns:
            if 'base_price_per_kg' in df.columns and 'quality_score' in df.columns:
                df['current_market_price_estimate'] = df['base_price_per_kg'] * (df['quality_score'] / 100) * np.random.uniform(0.8, 1.2, len(df))
            else:
                df['current_market_price_estimate'] = df['base_price_per_kg'] if 'base_price_per_kg' in df.columns else 20
        
        if 'profit_margin_pct' not in df.columns:
            if 'expected_revenue_at_recommended_market' in df.columns and 'quantity_kg' in df.columns:
                production_cost = df['quantity_kg'] * df['base_price_per_kg'] * 0.6 if 'base_price_per_kg' in df.columns else df['current_value_zar'] * 0.5
                df['profit_margin_pct'] = ((df['expected_revenue_at_recommended_market'] - production_cost) / production_cost * 100).fillna(0)
            else:
                df['profit_margin_pct'] = np.random.uniform(15, 45, len(df))
        
        if 'initial_value_zar' not in df.columns:
            df['initial_value_zar'] = df['current_value_zar'] + df['value_lost_zar'] if 'value_lost_zar' in df.columns else df['current_value_zar'] * 1.3
        
        if 'value_loss_percent' not in df.columns and 'value_lost_zar' in df.columns and 'initial_value_zar' in df.columns:
            df['value_loss_percent'] = (df['value_lost_zar'] / df['initial_value_zar'] * 100).fillna(0)
        
        # Ensure required columns exist
        required_cols = ['batch_id', 'harvest_date', 'produce_type', 'category', 'quality_score', 
                        'quality_grade', 'current_value_zar', 'value_lost_zar', 'remaining_shelf_life_days', 
                        'sell_urgency', 'recommended_market']
        for col in required_cols:
            if col not in df.columns:
                if col == 'quality_grade':
                    df['quality_grade'] = pd.cut(df['quality_score'], bins=[0,40,60,75,100], labels=['Poor', 'Fair', 'Good', 'Premium'])
                elif col == 'sell_urgency':
                    df['sell_urgency'] = np.where(df['remaining_shelf_life_days'] <= 2, 'IMMEDIATE', 
                                            np.where(df['remaining_shelf_life_days'] <= 5, 'HIGH', 'MEDIUM'))
                elif col == 'recommended_market':
                    df['recommended_market'] = 'Cape Town Market'
                elif col == 'current_value_zar':
                    df['current_value_zar'] = 1000
                elif col == 'value_lost_zar':
                    df['value_lost_zar'] = 0
                elif col == 'remaining_shelf_life_days':
                    df['remaining_shelf_life_days'] = 7
        
        # Add time-based columns
        if 'harvest_date' in df.columns:
            df['month'] = df['harvest_date'].dt.month
            df['month_name'] = df['harvest_date'].dt.strftime('%b')
            df['weekday'] = df['harvest_date'].dt.dayofweek
            df['quarter'] = df['harvest_date'].dt.quarter
            df['week'] = df['harvest_date'].dt.isocalendar().week
            df['day_of_year'] = df['harvest_date'].dt.dayofyear
        
        return df
    else:
        st.error("❌ Data file not found. Run 'python generate_data.py' first.")
        return None

def get_top_insights(df):
    insights = []
    avg_quality = df['quality_score'].mean()
    if avg_quality < 70:
        insights.append(("⚠️ Quality Alert", f"Average quality is {avg_quality:.0f}% - below target", "warning"))
    urgent_count = len(df[df['sell_urgency'] == 'IMMEDIATE'])
    if urgent_count > 0:
        insights.append(("🚨 Urgent Action", f"{urgent_count} batches need immediate sale", "urgent"))
    if 'profit_margin_pct' in df.columns:
        avg_margin = df['profit_margin_pct'].mean()
        if avg_margin > 30:
            insights.append(("📈 Strong Margins", f"Average profit margin at {avg_margin:.0f}%", "success"))
    total_loss = df['value_lost_zar'].sum() if 'value_lost_zar' in df.columns else 0
    if total_loss > 1_000_000:
        insights.append(("💰 Loss Alert", f"Total value loss: {format_currency(total_loss)}", "warning"))
    return insights

def main():
    st.markdown("""
    <div class='main-header'>
        <h1 style='font-size: 2rem; margin: 0;'>🌱 Nile.ag</h1>
        <p>Farm Intelligence Platform | Data-Driven Decisions | Profit Optimization</p>
        <p style='font-size: 0.8rem; opacity: 0.9;'>Real-time quality assessment, market intelligence, and harvest optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = load_data()
    if df is None:
        st.stop()
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### 📊 Data Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Batches", f"{len(df):,}")
        with col2:
            st.metric("Products", f"{df['produce_type'].nunique()}")
        
        st.markdown("---")
        st.markdown("### 🎮 Filters")
        
        # Date range filter
        min_date = df['harvest_date'].min().date()
        max_date = df['harvest_date'].max().date()
        date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['harvest_date'].dt.date >= start_date) & (df['harvest_date'].dt.date <= end_date)]
        
        min_quality = st.slider("Min Quality Score", 0, 100, int(df['quality_score'].quantile(0.5)), 5)
        
        if 'value_loss_percent' in df.columns:
            max_loss = st.slider("Max Loss %", 0, 100, int(df['value_loss_percent'].quantile(0.8)), 5)
        else:
            max_loss = 100
        
        urgency_options = df['sell_urgency'].unique().tolist()
        urgency_filter = st.multiselect("Urgency Level", urgency_options, default=urgency_options)
        
        product_options = ['All'] + sorted(df['produce_type'].unique().tolist())
        selected_products = st.multiselect("Product Type", product_options, default=['All'])
        
        category_options = ['All'] + sorted(df['category'].unique().tolist())
        selected_categories = st.multiselect("Category", category_options, default=['All'])
        
        st.markdown("---")
        
        # Apply filters
        df_filtered = df[df['quality_score'] >= min_quality]
        if 'value_loss_percent' in df.columns:
            df_filtered = df_filtered[df_filtered['value_loss_percent'] <= max_loss]
        df_filtered = df_filtered[df_filtered['sell_urgency'].isin(urgency_filter)]
        
        if 'All' not in selected_products:
            df_filtered = df_filtered[df_filtered['produce_type'].isin(selected_products)]
        
        if 'All' not in selected_categories:
            df_filtered = df_filtered[df_filtered['category'].isin(selected_categories)]
        
        if len(df_filtered) == 0:
            st.warning("⚠️ No data matches your filters")
            st.info(f"📊 Data ranges: Quality {df['quality_score'].min():.0f}-{df['quality_score'].max():.0f}")
            st.stop()
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📎 Download Filtered Data", csv, f"farm_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
    
    # Top metrics row
    st.markdown("### 📊 Key Performance Indicators")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"<div class='metric-card'><div style='font-size:0.7rem'>Filtered Batches</div><div style='font-size:1.3rem;font-weight:bold'>{len(df_filtered):,}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div style='font-size:0.7rem'>Avg Quality</div><div style='font-size:1.3rem;font-weight:bold'>{df_filtered['quality_score'].mean():.0f}%</div></div>", unsafe_allow_html=True)
    with col3:
        premium_pct = len(df_filtered[df_filtered['quality_grade'].str.contains('Premium', na=False)]) / len(df_filtered) * 100
        st.markdown(f"<div class='metric-card'><div style='font-size:0.7rem'>Premium %</div><div style='font-size:1.3rem;font-weight:bold'>{premium_pct:.0f}%</div></div>", unsafe_allow_html=True)
    with col4:
        total_value = df_filtered['current_value_zar'].sum() if 'current_value_zar' in df_filtered.columns else 0
        st.markdown(f"<div class='metric-card'><div style='font-size:0.7rem'>Total Value</div><div style='font-size:1.3rem;font-weight:bold'>{format_currency(total_value)}</div></div>", unsafe_allow_html=True)
    with col5:
        total_loss = df_filtered['value_lost_zar'].sum() if 'value_lost_zar' in df_filtered.columns else 0
        st.markdown(f"<div class='metric-card'><div style='font-size:0.7rem'>Total Loss</div><div style='font-size:1.3rem;font-weight:bold'>{format_currency(total_loss)}</div></div>", unsafe_allow_html=True)
    with col6:
        urgent_count = len(df_filtered[df_filtered['sell_urgency'] == 'IMMEDIATE'])
        st.markdown(f"<div class='metric-card'><div style='font-size:0.7rem'>Urgent Batches</div><div style='font-size:1.3rem;font-weight:bold'>{urgent_count}</div></div>", unsafe_allow_html=True)
    
    # Quick insights
    insights = get_top_insights(df_filtered)
    if insights:
        st.markdown("### 💡 Key Insights")
        insight_cols = st.columns(min(len(insights), 4))
        for idx, (title, message, type_) in enumerate(insights[:4]):
            with insight_cols[idx % 4]:
                card_class = {'warning': 'warning-card', 'success': 'success-card', 'urgent': 'urgent-card', 'info': 'decision-card'}.get(type_, 'decision-card')
                st.markdown(f"<div class='{card_class}'><strong>{title}</strong><br><small>{message}</small></div>", unsafe_allow_html=True)
    
    loss_text = f"Loss ≤ {max_loss}%" if 'value_loss_percent' in df.columns else ""
    st.info(f"📊 Showing {len(df_filtered):,} of {len(df):,} batches | Quality ≥ {min_quality}% {loss_text}")
    
    # Main tabs - 14 tabs with 50+ charts
    tabs = st.tabs([
        "📈 Dashboard", "🎯 Decisions", "🚨 Urgent", "📊 Quality", "💰 Financial",
        "🌾 Harvest", "📅 Seasonal", "🏆 Products", "📍 Markets", "📉 Trends",
        "🔥 Heatmaps", "📊 Stats", "🎨 Advanced", "📋 Data"
    ])
    
    # ========== TAB 0: DASHBOARD (8 charts) ==========
    with tabs[0]:
        st.markdown("### 📈 Executive Dashboard")
        
        # Row 1: Gauges
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_q = df_filtered['quality_score'].mean()
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=avg_q, title={'text': "Quality Score"},
                delta={'reference': 75, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2E7D32"},
                       'steps': [{'range': [0, 40], 'color': "#e74c3c"}, {'range': [40, 60], 'color': "#f39c12"},
                                {'range': [60, 75], 'color': "#f1c40f"}, {'range': [75, 90], 'color': "#2ecc71"},
                                {'range': [90, 100], 'color': "#27ae60"}]}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            avg_margin = df_filtered['profit_margin_pct'].mean() if 'profit_margin_pct' in df_filtered.columns else 25
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=avg_margin, title={'text': "Profit Margin %"},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#3498db"},
                       'steps': [{'range': [0, 15], 'color': "#e74c3c"}, {'range': [15, 25], 'color': "#f39c12"},
                                {'range': [25, 40], 'color': "#2ecc71"}, {'range': [40, 100], 'color': "#27ae60"}]}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            value_eff = (df_filtered['current_value_zar'].sum() / df_filtered['initial_value_zar'].sum() * 100) if 'initial_value_zar' in df_filtered.columns else 75
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=value_eff, title={'text': "Value Efficiency %"},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#9b59b6"},
                       'steps': [{'range': [0, 50], 'color': "#e74c3c"}, {'range': [50, 70], 'color': "#f39c12"},
                                {'range': [70, 85], 'color': "#2ecc71"}, {'range': [85, 100], 'color': "#27ae60"}]}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            avg_shelf = df_filtered['remaining_shelf_life_days'].mean()
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=avg_shelf, title={'text': "Shelf Life (days)"},
                gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#1abc9c"}}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        # Row 2: Trend charts
        col1, col2 = st.columns(2)
        
        with col1:
            daily_quality = df_filtered.groupby('harvest_date')['quality_score'].mean().reset_index()
            daily_quality = daily_quality.sort_values('harvest_date')
            daily_quality['MA7'] = daily_quality['quality_score'].rolling(7, min_periods=1).mean()
            daily_quality['MA30'] = daily_quality['quality_score'].rolling(30, min_periods=1).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_quality['harvest_date'], y=daily_quality['quality_score'], 
                                    name='Daily', line=dict(color='lightblue', width=1), opacity=0.5))
            fig.add_trace(go.Scatter(x=daily_quality['harvest_date'], y=daily_quality['MA7'], 
                                    name='7-day MA', line=dict(color='orange', width=2)))
            fig.add_trace(go.Scatter(x=daily_quality['harvest_date'], y=daily_quality['MA30'], 
                                    name='30-day MA', line=dict(color='red', width=2)))
            fig.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Target")
            fig.update_layout(title="Quality Trend with Moving Averages", height=400, xaxis_title="Date", yaxis_title="Quality Score")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            daily_volume = df_filtered.groupby('harvest_date')['quantity_kg'].sum().reset_index() if 'quantity_kg' in df_filtered.columns else df_filtered.groupby('harvest_date').size().reset_index(name='quantity_kg')
            daily_volume = daily_volume.sort_values('harvest_date')
            daily_volume.columns = ['harvest_date', 'volume']
            fig = px.area(daily_volume, x='harvest_date', y='volume', title="Production Volume Trend",
                         labels={'volume': 'Volume (kg)', 'harvest_date': 'Date'}, color_discrete_sequence=['#3498db'])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Row 3: Scatter and Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            if 'profit_margin_pct' in df_filtered.columns:
                sample = df_filtered.sample(min(500, len(df_filtered)))
                size_vals = safe_size_for_plot(sample['current_value_zar'].values if 'current_value_zar' in sample.columns else np.ones(len(sample)))
                fig = px.scatter(sample, x='quality_score', y='profit_margin_pct', 
                                color='category', size=size_vals, size_max=30,
                                title="Quality vs Profit Analysis",
                                trendline="ols", trendline_color_override="red",
                                labels={'quality_score': 'Quality Score (%)', 'profit_margin_pct': 'Profit Margin (%)'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(df_filtered, x='quality_score', nbins=30, title="Quality Score Distribution",
                              marginal='box', color_discrete_sequence=['#2E7D32'])
            fig.add_vline(x=75, line_dash="dash", line_color="green", annotation_text="Good")
            fig.add_vline(x=60, line_dash="dash", line_color="orange", annotation_text="Fair")
            st.plotly_chart(fig, use_container_width=True)
        
        # Row 4: Top products and markets
        col1, col2 = st.columns(2)
        
        with col1:
            top_products = df_filtered.groupby('produce_type')['current_value_zar'].sum().sort_values(ascending=False).head(10).reset_index()
            if not top_products.empty:
                fig = px.bar(top_products, x='current_value_zar', y='produce_type', orientation='h',
                            title="Top 10 Products by Value", color='current_value_zar', color_continuous_scale='Greens',
                            labels={'current_value_zar': 'Value (R)', 'produce_type': 'Product'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_markets = df_filtered.groupby('recommended_market')['current_value_zar'].sum().sort_values(ascending=False).reset_index()
            if not top_markets.empty:
                fig = px.pie(top_markets, values='current_value_zar', names='recommended_market',
                            title="Revenue Distribution by Market", hole=0.3, color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 1: DECISIONS (5 charts) ==========
    with tabs[1]:
        st.markdown("### 🎯 Smart Decisions Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Market Switch Opportunities")
            recs = []
            if 'top_markets_summary' in df_filtered.columns:
                for _, row in df_filtered.head(200).iterrows():
                    markets = parse_markets(row.get('top_markets_summary', ''))
                    if len(markets) >= 2:
                        advantage = markets[0]['revenue'] - markets[1]['revenue']
                        if advantage > 500:
                            recs.append({'product': row['produce_type'], 'profit': advantage, 'to': markets[0]['market']})
            if recs:
                rec_df = pd.DataFrame(recs).groupby('product').agg({'profit': 'sum'}).sort_values('profit', ascending=False).head(10)
                fig = px.bar(rec_df, x='profit', y=rec_df.index, orientation='h', title="Extra Profit from Market Switches",
                            color='profit', color_continuous_scale='Greens', labels={'profit': 'Extra Profit (R)', 'index': 'Product'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No market switch opportunities found")
        
        with col2:
            st.markdown("#### 📊 Harvest Recommendations")
            if 'harvest_recommendation' in df_filtered.columns:
                harvest_counts = df_filtered['harvest_recommendation'].value_counts().reset_index()
                harvest_counts.columns = ['Recommendation', 'Count']
                fig = px.pie(harvest_counts, values='Count', names='Recommendation', title="Harvest Recommendations",
                            color_discrete_sequence=['#e74c3c', '#f39c12', '#3498db', '#27ae60'], hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Harvest recommendation data not available")
        
        # Decision matrix
        st.markdown("#### 🌲 Decision Matrix")
        quality_bins = pd.cut(df_filtered['quality_score'], bins=[0, 60, 75, 90, 100], labels=['Poor', 'Fair', 'Good', 'Premium'])
        if 'current_market_price_estimate' in df_filtered.columns:
            price_trend = np.where(df_filtered['current_market_price_estimate'].pct_change().fillna(0) > 0, 'Up', 'Down')
            decision_matrix = pd.crosstab(quality_bins, price_trend, normalize='index') * 100
            
            fig = px.imshow(decision_matrix, text_auto='.1f', aspect='auto', title="Decision Matrix: Quality vs Price Trend",
                           color_continuous_scale='RdYlGn', labels={'x': 'Price Trend', 'y': 'Quality Grade', 'color': 'Percentage (%)'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 2: URGENT (3 charts) ==========
    with tabs[2]:
        st.markdown("### 🚨 Urgent Batches Analysis")
        
        urgent_df = df_filtered[df_filtered['sell_urgency'] == 'IMMEDIATE']
        if not urgent_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                urgent_by_product = urgent_df['produce_type'].value_counts().head(10).reset_index()
                urgent_by_product.columns = ['Product', 'Count']
                fig = px.bar(urgent_by_product, x='Product', y='Count', title="Urgent Batches by Product",
                            color='Count', color_continuous_scale='Reds')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                urgent_by_market = urgent_df['recommended_market'].value_counts().reset_index()
                urgent_by_market.columns = ['Market', 'Count']
                fig = px.pie(urgent_by_market, values='Count', names='Market', title="Urgent Batches by Market", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            
            # Value at risk over time
            urgent_over_time = urgent_df.groupby('harvest_date')['current_value_zar'].sum().reset_index()
            fig = px.area(urgent_over_time, x='harvest_date', y='current_value_zar', title="Value at Risk Over Time",
                         labels={'current_value_zar': 'Value at Risk (R)', 'harvest_date': 'Date'},
                         color_discrete_sequence=['#e74c3c'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Display urgent batches
            with st.expander("View Urgent Batches Details"):
                for _, row in urgent_df.head(10).iterrows():
                    st.markdown(f"""
                    <div class='urgent-card'>
                        <strong>🔴 {row['produce_type']}</strong> - {row['batch_id']}<br>
                        Quality: {row['quality_score']:.0f}% | Shelf Life: {row['remaining_shelf_life_days']:.0f} days<br>
                        Value: {format_currency(row['current_value_zar'])} | Best Market: {row['recommended_market']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ No urgent batches require immediate action")
    
    # ========== TAB 3: QUALITY (6 charts) ==========
    with tabs[3]:
        st.markdown("### 📊 Advanced Quality Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Box plot by category
            fig = px.box(df_filtered, x='category', y='quality_score', title="Quality Distribution by Category",
                        color='category', color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Violin plot
            fig = px.violin(df_filtered, x='category', y='quality_score', box=True, points='all',
                           title="Quality Violin Plot by Category", color='category')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Quality by product (top 15)
        top_products = df_filtered.groupby('produce_type')['quality_score'].mean().sort_values(ascending=False).head(15).reset_index()
        fig = px.bar(top_products, x='produce_type', y='quality_score', title="Top 15 Products by Quality",
                    color='quality_score', color_continuous_scale='RdYlGn', text='quality_score')
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Cumulative distribution
        sorted_quality = df_filtered['quality_score'].sort_values()
        cumulative_pct = np.arange(1, len(sorted_quality) + 1) / len(sorted_quality) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sorted_quality, y=cumulative_pct, mode='lines', fill='tozeroy',
                                line=dict(color='#2E7D32', width=2), name='Cumulative %'))
        fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% of batches")
        fig.update_layout(title="Cumulative Quality Distribution", xaxis_title="Quality Score", yaxis_title="Cumulative Percentage")
        st.plotly_chart(fig, use_container_width=True)
        
        # Quality degradation by category
        if 'days_since_harvest' in df_filtered.columns:
            degradation_data = df_filtered.groupby(['category', 'days_since_harvest'])['quality_score'].mean().reset_index()
            pivot_degradation = degradation_data.pivot(index='category', columns='days_since_harvest', values='quality_score')
            fig = px.imshow(pivot_degradation, title="Quality Degradation Heatmap: Category vs Days",
                           color_continuous_scale='RdYlGn', aspect='auto', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Quality over time with confidence intervals
        daily_quality = df_filtered.groupby('harvest_date')['quality_score'].agg(['mean', 'std', 'count']).reset_index()
        daily_quality.columns = ['date', 'mean', 'std', 'count']
        if daily_quality['count'].min() > 0:
            daily_quality['ci_upper'] = daily_quality['mean'] + 1.96 * daily_quality['std'] / np.sqrt(daily_quality['count'])
            daily_quality['ci_lower'] = daily_quality['mean'] - 1.96 * daily_quality['std'] / np.sqrt(daily_quality['count'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_quality['date'], y=daily_quality['mean'], mode='lines', name='Mean Quality',
                                    line=dict(color='#2E7D32', width=2)))
            fig.add_trace(go.Scatter(x=daily_quality['date'], y=daily_quality['ci_upper'], mode='lines', 
                                    line=dict(color='rgba(46, 125, 50, 0.3)', width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=daily_quality['date'], y=daily_quality['ci_lower'], mode='lines',
                                    line=dict(color='rgba(46, 125, 50, 0.3)', width=0), fill='tonexty', showlegend=False,
                                    name='95% CI'))
            fig.update_layout(title="Quality Trend with 95% Confidence Interval", xaxis_title="Date", yaxis_title="Quality Score")
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 4: FINANCIAL (7 charts) ==========
    with tabs[4]:
        st.markdown("### 💰 Financial Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Loss by category
            if 'value_loss_percent' in df_filtered.columns:
                loss_by_cat = df_filtered.groupby('category')['value_loss_percent'].mean().sort_values(ascending=False).reset_index()
                fig = px.bar(loss_by_cat, x='category', y='value_loss_percent', title="Value Loss % by Category",
                            color='value_loss_percent', color_continuous_scale='Reds')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Profit by product
            if 'profit_margin_pct' in df_filtered.columns:
                profit_products = df_filtered.groupby('produce_type')['profit_margin_pct'].mean().sort_values(ascending=False).head(15).reset_index()
                fig = px.bar(profit_products, x='produce_type', y='profit_margin_pct', title="Top 15 by Profit Margin",
                            color='profit_margin_pct', color_continuous_scale='Greens')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Waterfall chart
        initial_total = df_filtered['initial_value_zar'].sum() if 'initial_value_zar' in df_filtered.columns else 0
        current_total = df_filtered['current_value_zar'].sum() if 'current_value_zar' in df_filtered.columns else 0
        loss_total = df_filtered['value_lost_zar'].sum() if 'value_lost_zar' in df_filtered.columns else 0
        
        fig = go.Figure(go.Waterfall(
            name="Value Flow", orientation="v",
            measure=["relative", "relative", "total"],
            x=["Initial Value", "Value Lost", "Current Value"],
            y=[initial_total, -loss_total, current_total],
            text=[format_currency(initial_total), f"-{format_currency(loss_total)}", format_currency(current_total)],
            textposition="outside",
            increasing={"marker": {"color": "#e74c3c"}},
            decreasing={"marker": {"color": "#27ae60"}},
            totals={"marker": {"color": "#3498db"}}
        ))
        fig.update_layout(title="Value Flow Waterfall Chart", height=450)
        st.plotly_chart(fig, use_container_width=True)
        
        # Sunburst chart
        category_product_value = df_filtered.groupby(['category', 'produce_type'])['current_value_zar'].sum().reset_index()
        fig = px.sunburst(category_product_value, path=['category', 'produce_type'], values='current_value_zar',
                         title="Value Hierarchy: Category → Product", color='current_value_zar',
                         color_continuous_scale='Greens')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Profit distribution histogram
        if 'profit_margin_pct' in df_filtered.columns:
            fig = px.histogram(df_filtered, x='profit_margin_pct', nbins=30, title="Profit Margin Distribution",
                              marginal='box', color_discrete_sequence=['#3498db'])
            fig.add_vline(x=0, line_dash="dash", line_color="red")
            fig.add_vline(x=25, line_dash="dash", line_color="green", annotation_text="Target")
            st.plotly_chart(fig, use_container_width=True)
        
        # Scatter: Quality vs Loss
        if 'value_loss_percent' in df_filtered.columns:
            sample = df_filtered.sample(min(500, len(df_filtered)))
            fig = px.scatter(sample, x='quality_score', y='value_loss_percent', color='category',
                            title="Quality vs Loss Analysis", trendline="ols",
                            labels={'quality_score': 'Quality Score (%)', 'value_loss_percent': 'Value Loss (%)'})
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 5: HARVEST (3 charts) ==========
    with tabs[5]:
        st.markdown("### 🌾 Harvest Optimization Suite")
        
        selected_product = st.selectbox("Select Product for Analysis", sorted(df_filtered['produce_type'].unique()))
        
        if selected_product and 'days_since_harvest' in df_filtered.columns:
            prod_data = df_filtered[df_filtered['produce_type'] == selected_product]
            
            if not prod_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Scatter with trend line
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=prod_data['days_since_harvest'], y=prod_data['quality_score'], 
                                            mode='markers', name='Data', marker=dict(color='#2E7D32', size=8, opacity=0.6)))
                    
                    if len(prod_data) > 2:
                        # Linear trend
                        z = np.polyfit(prod_data['days_since_harvest'], prod_data['quality_score'], 1)
                        p = np.poly1d(z)
                        x_trend = np.linspace(prod_data['days_since_harvest'].min(), prod_data['days_since_harvest'].max(), 50)
                        fig.add_trace(go.Scatter(x=x_trend, y=p(x_trend), mode='lines', name='Linear Trend',
                                                line=dict(color='red', width=2)))
                        
                        # Polynomial trend (degree 2) if enough points
                        if len(prod_data) > 5:
                            z2 = np.polyfit(prod_data['days_since_harvest'], prod_data['quality_score'], 2)
                            p2 = np.poly1d(z2)
                            fig.add_trace(go.Scatter(x=x_trend, y=p2(x_trend), mode='lines', name='Polynomial Fit',
                                                    line=dict(color='orange', width=2, dash='dash')))
                    
                    fig.add_hline(y=90, line_dash="dot", line_color="green", annotation_text="Premium")
                    fig.add_hline(y=75, line_dash="dash", line_color="orange", annotation_text="Good")
                    fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Fair")
                    fig.update_layout(title=f"Quality Degradation - {selected_product}", 
                                     xaxis_title="Days Since Harvest", yaxis_title="Quality Score", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Optimal window visualization
                    optimal_data = prod_data[prod_data['quality_score'] >= 75]
                    if not optimal_data.empty:
                        optimal_start = optimal_data['days_since_harvest'].min()
                        optimal_end = optimal_data['days_since_harvest'].max()
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=[optimal_start, optimal_end], y=[50, 50], mode='lines',
                                                line=dict(color='green', width=20), name='Optimal Window'))
                        fig.add_trace(go.Scatter(x=[prod_data['days_since_harvest'].min(), optimal_start], y=[50, 50],
                                                mode='lines', line=dict(color='yellow', width=20), name='Pre-optimal'))
                        fig.add_trace(go.Scatter(x=[optimal_end, prod_data['days_since_harvest'].max()], y=[50, 50],
                                                mode='lines', line=dict(color='red', width=20), name='Post-optimal'))
                        fig.update_layout(title="Optimal Harvest Window", xaxis_title="Days Since Harvest",
                                         yaxis_title="", yaxis_visible=False, height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.success(f"✅ Optimal Harvest Window: Days {optimal_start:.0f} - {optimal_end:.0f}")
                        
                        current_days = prod_data['days_since_harvest'].mean()
                        if current_days < optimal_start:
                            st.info(f"⏰ Wait {optimal_start - current_days:.0f} more days for optimal quality")
                        elif current_days > optimal_end:
                            st.warning(f"⚠️ Harvest immediately! {current_days - optimal_end:.0f} days past optimal window")
                        else:
                            st.success("🎯 Currently in optimal harvest window")
        
        # Harvest volume forecast
        if 'quantity_kg' in df_filtered.columns:
            daily_volume = df_filtered.groupby('harvest_date')['quantity_kg'].sum().reset_index()
            daily_volume = daily_volume.sort_values('harvest_date')
            daily_volume['MA7'] = daily_volume['quantity_kg'].rolling(7, min_periods=1).mean()
            
            fig = px.line(daily_volume, x='harvest_date', y='quantity_kg', title="Harvest Volume Trend",
                         labels={'quantity_kg': 'Volume (kg)', 'harvest_date': 'Date'})
            fig.add_trace(go.Scatter(x=daily_volume['harvest_date'], y=daily_volume['MA7'], 
                                    name='7-day MA', line=dict(color='orange', width=2)))
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 6: SEASONAL (5 charts) ==========
    with tabs[6]:
        st.markdown("### 📅 Comprehensive Seasonal Analysis")
        
        if 'harvest_date' in df_filtered.columns:
            df_filtered['month_name'] = df_filtered['harvest_date'].dt.strftime('%b')
            month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            col1, col2 = st.columns(2)
            
            with col1:
                seasonal_quality = df_filtered.groupby('month_name')['quality_score'].mean().reset_index()
                fig = px.line(seasonal_quality, x='month_name', y='quality_score', title="Quality by Month",
                             markers=True, category_orders={'month_name': month_order})
                fig.add_hline(y=75, line_dash="dash", line_color="green")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'quantity_kg' in df_filtered.columns:
                    seasonal_volume = df_filtered.groupby('month_name')['quantity_kg'].sum().reset_index()
                    fig = px.bar(seasonal_volume, x='month_name', y='quantity_kg', title="Production Volume by Month",
                                color='quantity_kg', color_continuous_scale='Blues', category_orders={'month_name': month_order})
                    st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap by category
            heatmap_data = df_filtered.groupby(['category', 'month_name'])['quality_score'].mean().reset_index()
            pivot_heat = heatmap_data.pivot(index='category', columns='month_name', values='quality_score')
            pivot_heat = pivot_heat.reindex(columns=month_order, fill_value=0)
            fig = px.imshow(pivot_heat, title="Quality Heatmap: Category vs Month", 
                           color_continuous_scale='RdYlGn', aspect='auto', height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Seasonal loss pattern
            if 'value_loss_percent' in df_filtered.columns:
                seasonal_loss = df_filtered.groupby('month_name')['value_loss_percent'].mean().reset_index()
                fig = px.bar(seasonal_loss, x='month_name', y='value_loss_percent', title="Loss % by Month",
                            color='value_loss_percent', color_continuous_scale='Reds', category_orders={'month_name': month_order})
                st.plotly_chart(fig, use_container_width=True)
            
            # Time series decomposition
            df_filtered['week'] = df_filtered['harvest_date'].dt.isocalendar().week
            weekly_quality = df_filtered.groupby('week')['quality_score'].mean().reset_index()
            
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                subplot_titles=("Original Data", "Trend", "Seasonal Pattern"))
            
            fig.add_trace(go.Scatter(x=weekly_quality['week'], y=weekly_quality['quality_score'], 
                                    mode='lines+markers', name='Weekly Quality'), row=1, col=1)
            
            trend = weekly_quality['quality_score'].rolling(13, center=True, min_periods=1).mean()
            fig.add_trace(go.Scatter(x=weekly_quality['week'], y=trend, mode='lines', 
                                    name='Trend', line=dict(color='red', width=2)), row=2, col=1)
            
            seasonal = weekly_quality['quality_score'] - trend
            fig.add_trace(go.Scatter(x=weekly_quality['week'], y=seasonal, mode='lines', 
                                    name='Seasonal', line=dict(color='green')), row=3, col=1)
            
            fig.update_layout(title="Time Series Decomposition", height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 7: PRODUCTS (4 charts) ==========
    with tabs[7]:
        st.markdown("### 🏆 Product Performance Dashboard")
        
        # Aggregate product data
        product_summary = df_filtered.groupby('produce_type').agg({
            'quality_score': 'mean',
            'current_value_zar': 'sum',
            'batch_id': 'count'
        }).reset_index()
        
        if 'profit_margin_pct' in df_filtered.columns:
            profit_data = df_filtered.groupby('produce_type')['profit_margin_pct'].mean().reset_index()
            product_summary = product_summary.merge(profit_data, on='produce_type')
            product_summary.columns = ['Product', 'Quality', 'Value', 'Batches', 'Profit']
        else:
            product_summary.columns = ['Product', 'Quality', 'Value', 'Batches']
            product_summary['Profit'] = 50
        
        # BCG-style matrix
        median_quality = product_summary['Quality'].median()
        median_profit = product_summary['Profit'].median()
        
        product_summary['Quadrant'] = product_summary.apply(
            lambda x: 'Star (High Quality, High Profit)' if x['Quality'] >= median_quality and x['Profit'] >= median_profit
            else 'Quality Leader (High Quality, Low Profit)' if x['Quality'] >= median_quality
            else 'Profit Leader (Low Quality, High Profit)' if x['Profit'] >= median_profit
            else 'Underperformer (Low Quality, Low Profit)', axis=1)
        
        quadrant_colors = {'Star (High Quality, High Profit)': '#27ae60', 
                          'Quality Leader (High Quality, Low Profit)': '#3498db',
                          'Profit Leader (Low Quality, High Profit)': '#f39c12',
                          'Underperformer (Low Quality, Low Profit)': '#e74c3c'}
        
        size_vals = safe_size_for_plot(product_summary['Value'].values)
        
        fig = px.scatter(product_summary, x='Quality', y='Profit', size=size_vals, text='Product',
                        title="Product Portfolio Matrix (BCG Style)", color='Quadrant',
                        color_discrete_map=quadrant_colors, hover_data=['Batches', 'Value'])
        fig.add_hline(y=median_profit, line_dash="dash", line_color="gray", annotation_text="Median Profit")
        fig.add_vline(x=median_quality, line_dash="dash", line_color="gray", annotation_text="Median Quality")
        fig.update_traces(textposition='top center')
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top products tables
        col1, col2 = st.columns(2)
        with col1:
            top_by_value = product_summary.nlargest(10, 'Value')[['Product', 'Quality', 'Value', 'Batches']]
            top_by_value['Value'] = top_by_value['Value'].apply(lambda x: format_currency(x))
            st.dataframe(top_by_value, use_container_width=True)
        
        with col2:
            if 'Profit' in product_summary.columns:
                top_by_profit = product_summary.nlargest(10, 'Profit')[['Product', 'Profit', 'Quality', 'Batches']]
                st.dataframe(top_by_profit, use_container_width=True)
        
        # Value by product bar chart
        top_value = df_filtered.groupby('produce_type')['current_value_zar'].sum().sort_values(ascending=False).head(15)
        fig = px.bar(x=top_value.values, y=top_value.index, orientation='h',
                    title="Top 15 Products by Total Value", color=top_value.values,
                    color_continuous_scale='Greens', labels={'x': 'Value (R)', 'y': 'Product'})
        st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 8: MARKETS (4 charts) ==========
    with tabs[8]:
        st.markdown("### 📍 Market Intelligence Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            market_counts = df_filtered['recommended_market'].value_counts().reset_index()
            market_counts.columns = ['Market', 'Batches']
            fig = px.bar(market_counts, x='Market', y='Batches', title="Batches by Recommended Market",
                        color='Batches', color_continuous_scale='Greens', text='Batches')
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            revenue_by_market = df_filtered.groupby('recommended_market')['current_value_zar'].sum().reset_index()
            revenue_by_market.columns = ['Market', 'Revenue']
            fig = px.pie(revenue_by_market, values='Revenue', names='Market', title="Revenue Distribution by Market",
                        hole=0.3, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Market radar chart
        market_metrics = df_filtered.groupby('recommended_market').agg({
            'profit_margin_pct': 'mean' if 'profit_margin_pct' in df_filtered.columns else 'count',
            'quality_score': 'mean',
            'current_value_zar': 'sum'
        }).reset_index()
        market_metrics = market_metrics.head(6)
        
        fig = go.Figure()
        for _, row in market_metrics.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['quality_score'], row['profit_margin_pct'] if 'profit_margin_pct' in row else 50, row['current_value_zar'] / 1e6],
                theta=['Quality', 'Profit Margin %', 'Value (M R)'],
                fill='toself', name=row['recommended_market']
            ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), 
                         title="Market Performance Comparison", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Market performance table
        market_perf = df_filtered.groupby('recommended_market').agg({
            'batch_id': 'count',
            'current_value_zar': 'sum',
            'quality_score': 'mean'
        }).round(2).reset_index()
        market_perf.columns = ['Market', 'Batches', 'Total Value', 'Avg Quality']
        market_perf['Total Value'] = market_perf['Total Value'].apply(lambda x: format_currency(x))
        st.dataframe(market_perf, use_container_width=True, hide_index=True)
    
    # ========== TAB 9: TRENDS (4 charts) ==========
    with tabs[9]:
        st.markdown("### 📉 Advanced Trend Analysis")
        
        if 'harvest_date' in df_filtered.columns:
            # Moving average crossover
            daily_data = df_filtered.groupby('harvest_date')['quality_score'].mean().reset_index()
            daily_data = daily_data.sort_values('harvest_date')
            daily_data['MA5'] = daily_data['quality_score'].rolling(5, min_periods=1).mean()
            daily_data['MA20'] = daily_data['quality_score'].rolling(20, min_periods=1).mean()
            
            daily_data['Crossover'] = np.where(daily_data['MA5'] > daily_data['MA20'], 'Bullish', 'Bearish')
            crossover_points = daily_data[daily_data['MA5'].shift(1) <= daily_data['MA20'].shift(1)][daily_data['MA5'] > daily_data['MA20']]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_data['harvest_date'], y=daily_data['quality_score'], 
                                    name='Daily', line=dict(color='lightblue', width=1)))
            fig.add_trace(go.Scatter(x=daily_data['harvest_date'], y=daily_data['MA5'], 
                                    name='5-day MA', line=dict(color='orange', width=2)))
            fig.add_trace(go.Scatter(x=daily_data['harvest_date'], y=daily_data['MA20'], 
                                    name='20-day MA', line=dict(color='red', width=2)))
            if not crossover_points.empty:
                fig.add_trace(go.Scatter(x=crossover_points['harvest_date'], y=crossover_points['MA5'], 
                                        mode='markers', name='Crossover', marker=dict(color='green', size=12, symbol='triangle-up')))
            fig.update_layout(title="Moving Average Crossover Analysis", height=450)
            st.plotly_chart(fig, use_container_width=True)
            
            # RSI (Relative Strength Index)
            delta = daily_data['quality_score'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_data['harvest_date'], y=rsi, name='RSI', line=dict(color='#9b59b6', width=2)))
            fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
            fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
            fig.add_hline(y=50, line_dash="dot", line_color="gray")
            fig.update_layout(title="Quality RSI (Relative Strength Index)", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Weekly pattern
            weekly_avg = df_filtered.groupby('weekday')['quality_score'].mean().reset_index()
            weekday_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            weekly_avg['Day'] = weekly_avg['weekday'].map(weekday_names)
            
            fig = px.bar(weekly_avg, x='Day', y='quality_score', title="Quality by Day of Week",
                        color='quality_score', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
            
            # Monthly trend
            monthly_data = df_filtered.groupby(df_filtered['harvest_date'].dt.to_period('M')).agg({
                'quality_score': 'mean',
                'current_value_zar': 'sum'
            }).reset_index()
            monthly_data['month'] = monthly_data['harvest_date'].astype(str)
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=monthly_data['month'], y=monthly_data['current_value_zar'], name="Revenue",
                                marker_color='#3498db'), secondary_y=False)
            fig.add_trace(go.Scatter(x=monthly_data['month'], y=monthly_data['quality_score'], name="Quality",
                                    line=dict(color='#e74c3c', width=2), marker=dict(size=10)), secondary_y=True)
            fig.update_layout(title="Monthly Revenue vs Quality", xaxis_title="Month", height=450)
            fig.update_yaxes(title_text="Revenue (R)", secondary_y=False)
            fig.update_yaxes(title_text="Quality Score (%)", secondary_y=True, range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 10: HEATMAPS (4 charts) ==========
    with tabs[10]:
        st.markdown("### 🔥 Advanced Analytics Heatmaps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Correlation matrix
            numeric_cols = ['quality_score', 'days_since_harvest', 'quantity_kg', 'value_loss_percent', 
                           'profit_margin_pct', 'remaining_shelf_life_days']
            available_cols = [c for c in numeric_cols if c in df_filtered.columns]
            if len(available_cols) > 1:
                corr_matrix = df_filtered[available_cols].corr()
                fig = px.imshow(corr_matrix, text_auto='.2f', title="Feature Correlation Matrix",
                               color_continuous_scale='RdBu', aspect='auto', height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Loss heatmap by category and product
            if 'value_loss_percent' in df_filtered.columns:
                loss_heat = df_filtered.groupby(['category', 'produce_type'])['value_loss_percent'].mean().reset_index()
                pivot_loss = loss_heat.pivot(index='category', columns='produce_type', values='value_loss_percent')
                fig = px.imshow(pivot_loss, title="Loss % Heatmap: Category vs Product", 
                               color_continuous_scale='Reds', aspect='auto', height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        # Product-month quality heatmap
        if 'harvest_date' in df_filtered.columns:
            df_heat = df_filtered.copy()
            df_heat['month'] = df_heat['harvest_date'].dt.strftime('%b')
            month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            heat_data = df_heat.groupby(['produce_type', 'month'])['quality_score'].mean().reset_index()
            pivot_heat = heat_data.pivot(index='produce_type', columns='month', values='quality_score')
            pivot_heat = pivot_heat.reindex(columns=[m for m in month_order if m in pivot_heat.columns], fill_value=0)
            fig = px.imshow(pivot_heat.head(20), title="Quality Heatmap: Product vs Month", 
                           color_continuous_scale='RdYlGn', aspect='auto', height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        # Weekday-hour heatmap (if hour data available)
        if 'hour' in df_filtered.columns:
            heat_data = df_filtered.groupby(['weekday', 'hour'])['quality_score'].mean().reset_index()
            pivot_heat = heat_data.pivot(index='weekday', columns='hour', values='quality_score')
            fig = px.imshow(pivot_heat, title="Quality by Day and Hour", color_continuous_scale='RdYlGn', aspect='auto')
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 11: STATS (4 charts) ==========
    with tabs[11]:
        st.markdown("### 📊 Statistical Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Q-Q plot for normality check
            from scipy import stats
            sorted_quality = np.sort(df_filtered['quality_score'])
            theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(sorted_quality)), 
                                                   loc=sorted_quality.mean(), scale=sorted_quality.std())
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=theoretical_quantiles, y=sorted_quality, mode='markers', name='Data',
                                    marker=dict(color='#3498db', size=6)))
            fig.add_trace(go.Scatter(x=[sorted_quality.min(), sorted_quality.max()], 
                                    y=[sorted_quality.min(), sorted_quality.max()],
                                    mode='lines', name='Reference', line=dict(color='red', dash='dash')))
            fig.update_layout(title="Q-Q Plot for Quality Scores", xaxis_title="Theoretical Quantiles", 
                             yaxis_title="Sample Quantiles", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot with outliers
            fig = px.box(df_filtered, y='quality_score', title="Quality Score Box Plot",
                        points="all", color_discrete_sequence=['#2E7D32'])
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistical summary
        st.markdown("#### Statistical Summary")
        stats_summary = df_filtered[['quality_score', 'days_since_harvest', 'quantity_kg', 'current_value_zar']].describe()
        st.dataframe(stats_summary, use_container_width=True)
        
        # ANOVA-style visualization
        category_means = df_filtered.groupby('category')['quality_score'].agg(['mean', 'std', 'count']).reset_index()
        fig = go.Figure()
        for _, row in category_means.iterrows():
            fig.add_trace(go.Scatter(x=[row['category']], y=[row['mean']], 
                                    error_y=dict(type='data', array=[row['std']]),
                                    mode='markers', marker=dict(size=20, color='#2E7D32'), name=row['category']))
        fig.update_layout(title="Category Means with Standard Deviation", xaxis_title="Category", 
                         yaxis_title="Quality Score", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 12: ADVANCED (4 charts) ==========
    with tabs[12]:
        st.markdown("### 🎨 Advanced Analytics")
        
        # 3D scatter plot
        if len(df_filtered) > 0:
            sample_3d = df_filtered.sample(min(500, len(df_filtered)))
            z_col = 'value_loss_percent' if 'value_loss_percent' in sample_3d.columns else 'profit_margin_pct'
            fig = px.scatter_3d(sample_3d, x='quality_score', y='days_since_harvest', z=z_col,
                               color='category', size='quantity_kg' if 'quantity_kg' in sample_3d.columns else None,
                               title="3D Analysis: Quality vs Days vs Loss",
                               labels={'quality_score': 'Quality', 'days_since_harvest': 'Days', z_col: 'Value'})
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        # Parallel coordinates
        cols_to_use = ['quality_score', 'days_since_harvest']
        if 'profit_margin_pct' in df_filtered.columns:
            cols_to_use.append('profit_margin_pct')
        if 'value_loss_percent' in df_filtered.columns:
            cols_to_use.append('value_loss_percent')
        
        parallel_data = df_filtered[cols_to_use].dropna()
        if len(parallel_data) > 0:
            fig = px.parallel_coordinates(parallel_data, color='quality_score',
                                         dimensions=cols_to_use,
                                         color_continuous_scale='RdYlGn', 
                                         title="Parallel Coordinates Analysis")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Sankey diagram for flow analysis
        flow_data = df_filtered.groupby(['category', 'recommended_market'])['current_value_zar'].sum().reset_index()
        flow_data = flow_data.nlargest(10, 'current_value_zar')
        
        all_nodes = list(set(flow_data['category'].tolist() + flow_data['recommended_market'].tolist()))
        node_indices = {node: i for i, node in enumerate(all_nodes)}
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5),
                     label=all_nodes, color="blue"),
            link=dict(source=[node_indices[c] for c in flow_data['category']],
                     target=[node_indices[m] for m in flow_data['recommended_market']],
                     value=flow_data['current_value_zar'].tolist()))])
        fig.update_layout(title="Value Flow: Category to Market", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Area chart for cumulative value
        cumulative_value = df_filtered.sort_values('harvest_date')['current_value_zar'].cumsum().reset_index(drop=True)
        fig = px.area(y=cumulative_value, title="Cumulative Value Over Time",
                     labels={'index': 'Batch Sequence', 'y': 'Cumulative Value (R)'},
                     color_discrete_sequence=['#2E7D32'])
        st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 13: DATA ==========
    with tabs[13]:
        st.markdown("### 📋 Data Explorer")
        
        search = st.text_input("🔍 Search (product/category)", "")
        rows = st.slider("Rows to display", 50, 500, 100)
        
        display_df = df_filtered.copy()
        if search:
            display_df = display_df[display_df['produce_type'].str.contains(search, case=False, na=False) |
                                    display_df['category'].str.contains(search, case=False, na=False)]
        
        cols_to_show = ['batch_id', 'harvest_date', 'produce_type', 'category', 'quality_score', 
                       'quality_grade', 'current_value_zar', 'value_loss_percent', 'sell_urgency', 'recommended_market']
        available_cols = [c for c in cols_to_show if c in display_df.columns]
        st.dataframe(display_df[available_cols].head(rows), use_container_width=True)
        
        # Data quality report
        st.markdown("#### Data Quality Report")
        missing_data = df_filtered.isnull().sum()
        missing_pct = (missing_data / len(df_filtered) * 100)
        quality_report = pd.DataFrame({'Missing Count': missing_data, 'Missing %': missing_pct})
        quality_report = quality_report[quality_report['Missing %'] > 0].sort_values('Missing %', ascending=False)
        if not quality_report.empty:
            st.dataframe(quality_report, use_container_width=True)
        else:
            st.success("✅ No missing data found!")
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <p>🌱 Nile.ag Farm Intelligence Platform | Data-Driven Decisions | Profit Optimization</p>
        <p style='font-size: 0.7rem;'>© 2024 Nile.ag - Empowering Agricultural Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()