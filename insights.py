# farm_intelligence.py - Complete Implementation

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

def load_farm_data(filepath):
    """Load and validate farm intelligence data"""
    df = pd.read_csv(filepath)
    
    # Convert date columns
    if 'harvest_date' in df.columns:
        df['harvest_date'] = pd.to_datetime(df['harvest_date'])
    
    # Add calculated fields if missing
    if 'value_efficiency' not in df.columns:
        df['value_efficiency'] = (df['current_value_zar'] / df['initial_value_zar'] * 100).round(1)
    
    if 'profit_margin_pct' not in df.columns:
        df['production_cost_estimate'] = df['quantity_kg'] * df['base_price_per_kg'] * 0.6
        df['estimated_profit'] = df['expected_revenue_at_recommended_market'] - df['production_cost_estimate']
        df['profit_margin_pct'] = (df['estimated_profit'] / df['production_cost_estimate'] * 100).round(1)
    
    print(f"✅ Loaded {len(df):,} batches with {len(df.columns)} features")
    print(f"   Date range: {df['harvest_date'].min().date()} to {df['harvest_date'].max().date()}")
    print(f"   Products: {df['produce_type'].nunique()}")
    
    return df


# ============================================================================
# 1. QUALITY DISTRIBUTION ANALYSIS
# ============================================================================

def get_quality_distribution(df):
    """Analyze quality score distribution across categories"""
    
    quality_stats = df.groupby('category').agg({
        'quality_score': ['mean', 'median', 'std', 'min', 'max'],
        'batch_id': 'count'
    }).round(1)
    quality_stats.columns = ['avg_quality', 'median_quality', 'std_quality', 'min_quality', 'max_quality', 'batch_count']
    quality_stats = quality_stats.sort_values('avg_quality', ascending=False)
    
    # Quality grade distribution
    grade_dist = df['quality_grade'].value_counts()
    grade_pct = (grade_dist / len(df) * 100).round(1)
    
    # Critical quality metrics
    critical_batches = df[df['quality_score'] < 60]
    premium_batches = df[df['quality_score'] >= 90]
    
    results = {
        'by_category': quality_stats,
        'grade_distribution': pd.DataFrame({'count': grade_dist, 'percentage': grade_pct}),
        'critical_batches': len(critical_batches),
        'critical_value_at_risk': critical_batches['current_value_zar'].sum(),
        'premium_batches': len(premium_batches),
        'premium_value': premium_batches['current_value_zar'].sum(),
        'overall_avg_quality': df['quality_score'].mean(),
        'quality_trend': df.groupby('harvest_date')['quality_score'].mean().tail(30)
    }
    
    print(f"\n📊 Quality Distribution:")
    print(f"   Average Quality: {results['overall_avg_quality']:.1f}")
    print(f"   Premium Batches: {results['premium_batches']:,} ({results['premium_value']/1e6:.1f}M ZAR)")
    print(f"   Critical Batches: {results['critical_batches']:,} ({results['critical_value_at_risk']/1e6:.1f}M ZAR at risk)")
    
    return results


# ============================================================================
# 2. DECLINING QUALITY PRODUCTS
# ============================================================================

def get_declining_quality_products(df, threshold_days=5):
    """Identify products with rapid quality deterioration"""
    
    # Calculate quality loss rate per day
    quality_loss = df.groupby('produce_type').agg({
        'quality_score': 'mean',
        'days_since_harvest': 'mean',
        'remaining_shelf_life_days': 'mean',
        'value_loss_percent': 'mean'
    }).round(1)
    
    # Estimate daily degradation rate
    quality_loss['est_daily_loss'] = ((100 - quality_loss['quality_score']) / quality_loss['days_since_harvest']).clip(0, 100)
    quality_loss['criticality_score'] = (
        quality_loss['est_daily_loss'] * 0.4 + 
        (100 - quality_loss['remaining_shelf_life_days']) * 0.3 +
        quality_loss['value_loss_percent'] * 0.3
    )
    
    declining_products = quality_loss.sort_values('criticality_score', ascending=False).head(20)
    
    # Add recommendations
    declining_products['recommendation'] = declining_products['est_daily_loss'].apply(
        lambda x: 'IMMEDIATE HARVEST' if x > 15 else 'URGENT SALE' if x > 10 else 'MONITOR CLOSELY'
    )
    
    print(f"\n⚠️ Top 5 Declining Products:")
    for idx, (product, row) in enumerate(declining_products.head(5).iterrows(), 1):
        print(f"   {idx}. {product}: {row['est_daily_loss']:.1f} quality points lost/day | {row['recommendation']}")
    
    return declining_products


# ============================================================================
# 3. MARKET COMPARISON & OPTIMIZATION
# ============================================================================

def get_market_comparison(df):
    """Compare market performance and identify best channels"""
    
    # Market performance metrics
    market_performance = df.groupby('recommended_market').agg({
        'batch_id': 'count',
        'expected_revenue_at_recommended_market': 'sum',
        'quantity_kg': 'sum',
        'profit_margin_pct': 'mean',
        'quality_score': 'mean'
    }).round(2)
    
    market_performance.columns = ['batches', 'total_revenue', 'total_kg', 'avg_margin_pct', 'avg_quality']
    market_performance['revenue_per_kg'] = market_performance['total_revenue'] / market_performance['total_kg']
    market_performance = market_performance.sort_values('total_revenue', ascending=False)
    
    # Market by product specialization
    market_specialization = df.groupby(['recommended_market', 'category']).size().unstack(fill_value=0)
    market_specialization_pct = market_specialization.div(market_specialization.sum(axis=1), axis=0) * 100
    
    # Transport efficiency
    df['transport_cost_per_kg'] = df.apply(
        lambda x: x['expected_revenue_at_recommended_market'] * 0.1 if 'expected_revenue_at_recommended_market' in x else 0,
        axis=1
    )
    
    transport_efficiency = df.groupby('recommended_market').agg({
        'expected_revenue_at_recommended_market': 'mean',
        'quantity_kg': 'mean'
    })
    transport_efficiency['revenue_per_kg'] = transport_efficiency['expected_revenue_at_recommended_market'] / transport_efficiency['quantity_kg']
    
    results = {
        'market_performance': market_performance,
        'market_specialization': market_specialization_pct,
        'best_market_overall': market_performance.index[0],
        'best_margin_market': market_performance.loc[market_performance['avg_margin_pct'].idxmax()].name if len(market_performance) > 0 else None,
        'market_rankings': market_performance[['total_revenue', 'avg_margin_pct', 'revenue_per_kg']]
    }
    
    print(f"\n📍 Market Performance:")
    print(f"   Best Overall: {results['best_market_overall']}")
    print(f"   Best Margin: {results['best_margin_market']}")
    print(f"   Top Market Revenue: R{market_performance.iloc[0]['total_revenue']/1e6:.1f}M")
    
    return results


# ============================================================================
# 4. URGENT BATCHES IDENTIFICATION
# ============================================================================

def get_urgent_batches(df, urgency_threshold=70):
    """Identify batches requiring immediate action"""
    
    urgent = df[df['urgency_score'] >= urgency_threshold].copy()
    urgent = urgent.sort_values('urgency_score', ascending=False)
    
    # Categorize urgency
    urgent['urgency_category'] = pd.cut(
        urgent['urgency_score'],
        bins=[0, 70, 85, 101],
        labels=['High', 'Critical', 'Emergency']
    )
    
    # Actionable insights
    urgent_by_product = urgent.groupby('produce_type').agg({
        'batch_id': 'count',
        'quantity_kg': 'sum',
        'current_value_zar': 'sum',
        'urgency_score': 'mean'
    }).round(2).sort_values('current_value_zar', ascending=False)
    
    # Value at risk calculation
    value_at_risk = urgent['current_value_zar'].sum()
    potential_loss = urgent['value_lost_zar'].sum()
    
    # Recommended actions
    urgent['recommended_action'] = urgent.apply(
        lambda x: f"Sell to {x['recommended_market']} within 24 hours" if x['sell_urgency'] == 'IMMEDIATE'
        else f"Process or discount {x['sell_price_adjustment_pct']}%" if x['remaining_shelf_life_days'] <= 2
        else "Expedite to nearest market",
        axis=1
    )
    
    results = {
        'urgent_batches': urgent,
        'total_urgent_batches': len(urgent),
        'value_at_risk': value_at_risk,
        'potential_loss': potential_loss,
        'urgent_by_product': urgent_by_product,
        'top_urgent_products': urgent_by_product.head(10),
        'avg_urgency_score': urgent['urgency_score'].mean()
    }
    
    print(f"\n🚨 Urgent Batches Analysis:")
    print(f"   {results['total_urgent_batches']:,} batches require immediate action")
    print(f"   Value at Risk: R{results['value_at_risk']/1e6:.2f}M")
    print(f"   Potential Loss if ignored: R{results['potential_loss']/1e6:.2f}M")
    
    return results


# ============================================================================
# 5. HARVEST RECOMMENDATIONS
# ============================================================================

def get_harvest_recommendations(df):
    """Generate optimal harvest timing recommendations"""
    
    # Group by produce type and season
    harvest_opt = df.groupby(['produce_type', 'season']).agg({
        'quality_score': 'mean',
        'current_market_price_estimate': 'mean',
        'forecast_price_in_3_days': 'mean',
        'value_efficiency': 'mean'
    }).round(2)
    
    # Calculate harvest window score
    harvest_opt['price_trend'] = (
        (harvest_opt['forecast_price_in_3_days'] - harvest_opt['current_market_price_estimate']) / 
        harvest_opt['current_market_price_estimate'] * 100
    )
    
    harvest_opt['harvest_priority'] = np.where(
        harvest_opt['price_trend'] > 5, 'WAIT - Prices Rising',
        np.where(harvest_opt['price_trend'] < -5, 'HARVEST NOW - Prices Falling',
                 'MONITOR - Stable Prices')
    )
    
    # Best harvest windows by month
    monthly_opt = df.groupby(['produce_type', 'month']).agg({
        'quality_score': 'mean',
        'current_market_price_estimate': 'mean'
    }).round(2)
    
    best_harvest_windows = monthly_opt.groupby('produce_type')['current_market_price_estimate'].idxmax()
    
    results = {
        'harvest_optimization': harvest_opt,
        'best_harvest_windows': best_harvest_windows,
        'products_to_harvest_now': harvest_opt[harvest_opt['harvest_priority'] == 'HARVEST NOW - Prices Falling'].index.tolist(),
        'products_to_monitor': harvest_opt[harvest_opt['harvest_priority'] == 'MONITOR - Stable Prices'].index.tolist(),
        'avg_price_trend': harvest_opt['price_trend'].mean()
    }
    
    print(f"\n🌾 Harvest Recommendations:")
    print(f"   Products to Harvest Now: {len(results['products_to_harvest_now'])}")
    print(f"   Products to Monitor: {len(results['products_to_monitor'])}")
    print(f"   Average Price Trend: {results['avg_price_trend']:.1f}%")
    
    return results


# ============================================================================
# 6. LOSS ANALYSIS
# ============================================================================

def get_loss_analysis(df):
    """Analyze value loss by category and product"""
    
    # Loss by category
    loss_by_category = df.groupby('category').agg({
        'initial_value_zar': 'sum',
        'current_value_zar': 'sum',
        'value_lost_zar': 'sum',
        'value_loss_percent': 'mean',
        'quantity_kg': 'sum'
    }).round(2)
    
    loss_by_category['loss_efficiency'] = loss_by_category['value_lost_zar'] / loss_by_category['initial_value_zar'] * 100
    loss_by_category = loss_by_category.sort_values('value_loss_percent', ascending=False)
    
    # Loss by product
    loss_by_product = df.groupby('produce_type').agg({
        'initial_value_zar': 'sum',
        'value_lost_zar': 'sum',
        'value_loss_percent': 'mean',
        'quality_score': 'mean',
        'batch_id': 'count'
    }).round(2)
    
    loss_by_product = loss_by_product.sort_values('value_loss_percent', ascending=False)
    
    # Top loss contributors
    top_loss_products = loss_by_product.head(10)
    
    # Loss by storage condition
    df['temp_zone'] = pd.cut(df['storage_temperature_c'], bins=[0, 4, 8, 12, 100], labels=['<4°C', '4-8°C', '8-12°C', '>12°C'])
    loss_by_temp = df.groupby('temp_zone').agg({
        'value_loss_percent': 'mean',
        'quality_score': 'mean',
        'batch_id': 'count'
    }).round(1)
    
    # Loss by humidity
    df['humidity_zone'] = pd.cut(df['storage_humidity_pct'], bins=[0, 75, 85, 95, 100], labels=['<75%', '75-85%', '85-95%', '>95%'])
    loss_by_humidity = df.groupby('humidity_zone').agg({
        'value_loss_percent': 'mean',
        'quality_score': 'mean',
        'batch_id': 'count'
    }).round(1)
    
    results = {
        'by_category': loss_by_category,
        'by_product': loss_by_product,
        'top_loss_products': top_loss_products,
        'by_temperature': loss_by_temp,
        'by_humidity': loss_by_humidity,
        'total_loss': df['value_lost_zar'].sum(),
        'avg_loss_percent': df['value_loss_percent'].mean(),
        'optimal_temp_zone': loss_by_temp[loss_by_temp['value_loss_percent'] == loss_by_temp['value_loss_percent'].min()].index[0] if len(loss_by_temp) > 0 else 'Unknown',
        'optimal_humidity_zone': loss_by_humidity[loss_by_humidity['value_loss_percent'] == loss_by_humidity['value_loss_percent'].min()].index[0] if len(loss_by_humidity) > 0 else 'Unknown'
    }
    
    print(f"\n💰 Loss Analysis:")
    print(f"   Total Value Lost: R{results['total_loss']/1e6:.2f}M")
    print(f"   Average Loss %: {results['avg_loss_percent']:.1f}%")
    print(f"   Optimal Temp Zone: {results['optimal_temp_zone']}")
    print(f"   Optimal Humidity Zone: {results['optimal_humidity_zone']}")
    
    return loss_by_category, loss_by_product


# ============================================================================
# 7. SEASONAL INSIGHTS
# ============================================================================

def get_seasonal_insights(df):
    """Extract seasonal patterns and predictions"""
    
    # Monthly aggregation
    monthly = df.groupby(['month', 'category']).agg({
        'quality_score': 'mean',
        'current_market_price_estimate': 'mean',
        'value_loss_percent': 'mean',
        'batch_id': 'count'
    }).round(2)
    
    # Peak season identification
    peak_season = df[df['is_peak_season'] == 1].groupby('category').agg({
        'quality_score': 'mean',
        'current_market_price_estimate': 'mean',
        'batch_id': 'count'
    })
    
    off_season = df[df['is_peak_season'] == 0].groupby('category').agg({
        'quality_score': 'mean',
        'current_market_price_estimate': 'mean'
    })
    
    price_premium = ((peak_season['current_market_price_estimate'] - off_season['current_market_price_estimate']) / 
                     off_season['current_market_price_estimate'] * 100).round(1)
    
    # Best months for each category
    best_months = df.groupby(['category', 'month'])['current_market_price_estimate'].mean().groupby('category').idxmax()
    
    # Seasonal quality variation
    seasonal_quality = df.groupby('season').agg({
        'quality_score': 'mean',
        'value_loss_percent': 'mean'
    }).round(1)
    
    results = {
        'monthly_trends': monthly,
        'peak_season_performance': peak_season,
        'off_season_performance': off_season,
        'price_premium_pct': price_premium,
        'best_months': best_months,
        'seasonal_quality': seasonal_quality,
        'highest_price_month': df.groupby('month')['current_market_price_estimate'].mean().idxmax(),
        'best_quality_season': seasonal_quality['quality_score'].idxmax()
    }
    
    print(f"\n📅 Seasonal Insights:")
    print(f"   Best Month for Prices: Month {results['highest_price_month']}")
    print(f"   Best Season for Quality: {results['best_quality_season']}")
    print(f"   Avg Peak Season Premium: {price_premium.mean():.1f}%")
    
    return results


# ============================================================================
# 8. ALERTS GENERATION
# ============================================================================

def generate_alerts(df):
    """Generate actionable alerts and notifications"""
    
    alerts = []
    
    # Critical quality alerts
    critical_quality = df[df['quality_score'] < 40]
    if len(critical_quality) > 0:
        alerts.append({
            'severity': 'CRITICAL',
            'type': 'Quality Failure',
            'message': f"{len(critical_quality)} batches have failed quality standards",
            'impact': f"R{critical_quality['current_value_zar'].sum():,.0f} at risk",
            'action': 'Immediate disposal or processing required'
        })
    
    # Urgent sell alerts
    urgent_sell = df[df['sell_urgency'] == 'IMMEDIATE']
    if len(urgent_sell) > 0:
        alerts.append({
            'severity': 'HIGH',
            'type': 'Urgent Sale Required',
            'message': f"{len(urgent_sell)} batches must be sold within 24 hours",
            'impact': f"R{urgent_sell['current_value_zar'].sum():,.0f} value at risk",
            'action': 'Contact buyers immediately, consider price discounts'
        })
    
    # Market opportunity alerts
    high_margin = df[df['profit_margin_pct'] > 40]
    if len(high_margin) > 0:
        best_market = high_margin.groupby('recommended_market')['profit_margin_pct'].mean().idxmax()
        alerts.append({
            'severity': 'INFO',
            'type': 'Market Opportunity',
            'message': f"High margin opportunities in {best_market}",
            'impact': f"{len(high_margin)} batches with >40% margin",
            'action': f'Prioritize shipments to {best_market}'
        })
    
    # Storage condition alerts
    poor_storage = df[(df['storage_temperature_c'] > 12) | (df['storage_humidity_pct'] > 95)]
    if len(poor_storage) > 0:
        alerts.append({
            'severity': 'HIGH',
            'type': 'Storage Conditions',
            'message': f"{len(poor_storage)} batches in suboptimal storage",
            'impact': f"Increased degradation rate by {poor_storage['value_loss_percent'].mean():.1f}%",
            'action': 'Review cooling systems and humidity controls'
        })
    
    # Seasonal harvesting alerts
    current_month = datetime.now().month
    peak_products = df[(df['is_peak_season'] == 1) & (df['harvest_date'].dt.month == current_month)]
    if len(peak_products) > 0:
        alerts.append({
            'severity': 'INFO',
            'type': 'Peak Season Harvest',
            'message': f"{peak_products['produce_type'].nunique()} products at peak season",
            'impact': "Maximum prices and quality expected",
            'action': 'Increase harvest frequency and secure market contracts'
        })
    
    # Loss prevention alert
    high_loss = df[df['value_loss_percent'] > 30]
    if len(high_loss) > 0:
        top_loss_product = high_loss.groupby('produce_type')['value_loss_percent'].mean().idxmax()
        alerts.append({
            'severity': 'MEDIUM',
            'type': 'Loss Prevention',
            'message': f"High loss rates detected for {top_loss_product}",
            'impact': f"Average {high_loss['value_loss_percent'].mean():.1f}% value loss",
            'action': f'Review handling and storage for {top_loss_product}'
        })
    
    alerts_df = pd.DataFrame(alerts)
    
    print(f"\n🔔 Generated {len(alerts)} Alerts:")
    for alert in alerts:
        print(f"   [{alert['severity']}] {alert['type']}: {alert['message']}")
    
    return alerts_df


# ============================================================================
# 9. PRICE TREND ANALYSIS
# ============================================================================

def get_price_trend_analysis(df):
    """Analyze price trends and generate forecasts"""
    
    # Daily average prices
    daily_prices = df.groupby('harvest_date').agg({
        'current_market_price_estimate': 'mean',
        'quality_score': 'mean'
    }).reset_index()
    
    # Calculate price momentum (7-day)
    daily_prices['price_ma7'] = daily_prices['current_market_price_estimate'].rolling(window=7, min_periods=1).mean()
    daily_prices['price_momentum'] = daily_prices['current_market_price_estimate'].pct_change(periods=3) * 100
    
    # Category trends
    category_trends = df.groupby(['harvest_date', 'category'])['current_market_price_estimate'].mean().unstack()
    
    # Product volatility
    price_volatility = df.groupby('produce_type')['current_market_price_estimate'].std() / df.groupby('produce_type')['current_market_price_estimate'].mean() * 100
    volatile_products = price_volatility.sort_values(ascending=False).head(10)
    
    # Price elasticity insights
    df['price_change'] = df.groupby('produce_type')['current_market_price_estimate'].pct_change()
    df['quantity_change'] = df.groupby('produce_type')['quantity_kg'].pct_change()
    elasticity = df.groupby('produce_type').apply(
        lambda x: (x['quantity_change'].mean() / x['price_change'].mean()) if x['price_change'].mean() != 0 else 0
    ).fillna(0)
    
    results = {
        'daily_prices': daily_prices,
        'category_trends': category_trends,
        'price_volatility': price_volatility,
        'volatile_products': volatile_products,
        'price_elasticity': elasticity,
        'current_avg_price': df['current_market_price_estimate'].mean(),
        'price_trend_direction': 'UP' if daily_prices['price_momentum'].iloc[-1] > 0 else 'DOWN',
        'momentum_strength': abs(daily_prices['price_momentum'].iloc[-1])
    }
    
    print(f"\n📈 Price Trend Analysis:")
    print(f"   Current Avg Price: R{results['current_avg_price']:.2f}/kg")
    print(f"   Trend Direction: {results['price_trend_direction']} ({results['momentum_strength']:.1f}% momentum)")
    print(f"   Most Volatile: {volatile_products.index[0]} ({volatile_products.iloc[0]:.1f}% volatility)")
    
    return results


# ============================================================================
# 10. EXECUTIVE SUMMARY
# ============================================================================

def get_executive_summary(df):
    """Generate comprehensive executive dashboard summary"""
    
    summary = {
        'overview': {
            'total_batches': len(df),
            'total_products': df['produce_type'].nunique(),
            'total_categories': df['category'].nunique(),
            'date_range': f"{df['harvest_date'].min().date()} to {df['harvest_date'].max().date()}",
            'total_quantity_kg': df['quantity_kg'].sum(),
            'total_value': df['current_value_zar'].sum(),
            'total_initial_value': df['initial_value_zar'].sum(),
            'total_loss': df['value_lost_zar'].sum(),
            'loss_percentage': (df['value_lost_zar'].sum() / df['initial_value_zar'].sum()) * 100
        },
        'quality_metrics': {
            'avg_quality_score': df['quality_score'].mean(),
            'premium_rate': (df['quality_score'] >= 90).mean() * 100,
            'rejection_rate': (df['quality_score'] < 40).mean() * 100,
            'best_category': df.groupby('category')['quality_score'].mean().idxmax(),
            'worst_category': df.groupby('category')['quality_score'].mean().idxmin()
        },
        'financial_metrics': {
            'avg_profit_margin': df['profit_margin_pct'].mean(),
            'total_profit': df['estimated_profit'].sum(),
            'roi_percentage': (df['estimated_profit'].sum() / df['production_cost_estimate'].sum()) * 100,
            'avg_revenue_per_kg': df['expected_revenue_at_recommended_market'].sum() / df['quantity_kg'].sum(),
            'top_market': df.groupby('recommended_market')['expected_revenue_at_recommended_market'].sum().idxmax()
        },
        'operational_metrics': {
            'urgent_batches_pct': (df['urgency_score'] > 70).mean() * 100,
            'avg_remaining_shelf_life': df['remaining_shelf_life_days'].mean(),
            'storage_compliance': ((df['storage_temperature_c'].between(4, 8)) & 
                                   (df['storage_humidity_pct'].between(85, 95))).mean() * 100,
            'harvest_efficiency': df['value_efficiency'].mean()
        },
        'strategic_recommendations': []
    }
    
    # Generate strategic recommendations
    if summary['quality_metrics']['rejection_rate'] > 5:
        summary['strategic_recommendations'].append(
            f"High rejection rate ({summary['quality_metrics']['rejection_rate']:.1f}%) - Review quality control processes"
        )
    
    if summary['financial_metrics']['roi_percentage'] < 20:
        summary['strategic_recommendations'].append(
            f"Low ROI ({summary['financial_metrics']['roi_percentage']:.1f}%) - Optimize market selection and pricing"
        )
    
    if summary['operational_metrics']['storage_compliance'] < 70:
        summary['strategic_recommendations'].append(
            f"Poor storage compliance ({summary['operational_metrics']['storage_compliance']:.1f}%) - Upgrade cold chain infrastructure"
        )
    
    if summary['overview']['loss_percentage'] > 15:
        summary['strategic_recommendations'].append(
            f"High value loss ({summary['overview']['loss_percentage']:.1f}%) - Implement real-time quality monitoring"
        )
    
    print(f"\n📊 EXECUTIVE SUMMARY")
    print(f"=" * 60)
    print(f"Total Value: R{summary['overview']['total_value']/1e6:.2f}M")
    print(f"Total Loss: R{summary['overview']['total_loss']/1e6:.2f}M ({summary['overview']['loss_percentage']:.1f}%)")
    print(f"Avg Quality: {summary['quality_metrics']['avg_quality_score']:.1f}/100")
    print(f"ROI: {summary['financial_metrics']['roi_percentage']:.1f}%")
    print(f"Urgent Batches: {summary['operational_metrics']['urgent_batches_pct']:.1f}% need immediate action")
    print(f"\nKey Recommendations:")
    for rec in summary['strategic_recommendations']:
        print(f"  • {rec}")
    
    return summary


# ============================================================================
# 11. MACHINE LEARNING MODELS
# ============================================================================

def train_quality_prediction_model(df):
    """Train Random Forest model to predict quality scores"""
    
    # Prepare features
    feature_cols = ['days_since_harvest', 'storage_temperature_c', 'storage_humidity_pct', 
                    'quantity_kg', 'is_peak_season', 'base_price_per_kg']
    
    # Create dummies for categorical
    produce_dummies = pd.get_dummies(df['produce_type'], prefix='product')
    category_dummies = pd.get_dummies(df['category'], prefix='cat')
    
    X = pd.concat([df[feature_cols], produce_dummies, category_dummies], axis=1)
    y = df['quality_score']
    
    # Handle missing values
    X = X.fillna(X.mean())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False).head(20)
    
    print(f"\n🤖 Quality Prediction Model:")
    print(f"   MAE: {mae:.2f} quality points")
    print(f"   R² Score: {r2:.3f}")
    print(f"   Top Feature: {feature_importance.iloc[0]['feature']} ({feature_importance.iloc[0]['importance']:.3f})")
    
    return model, feature_importance


def train_price_prediction_model(df):
    """Train Gradient Boosting model to predict prices"""
    
    # Prepare features
    feature_cols = ['quality_score', 'days_since_harvest', 'base_price_per_kg', 
                    'is_peak_season', 'quantity_kg']
    
    # Create dummies
    produce_dummies = pd.get_dummies(df['produce_type'], prefix='product')
    market_dummies = pd.get_dummies(df['recommended_market'], prefix='market')
    
    X = pd.concat([df[feature_cols], produce_dummies, market_dummies], axis=1)
    y = df['current_market_price_estimate']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.fillna(0))
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Train model
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n💰 Price Prediction Model:")
    print(f"   MAE: R{mae:.2f}/kg")
    print(f"   R² Score: {r2:.3f}")
    
    return model, scaler


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_all_insights(filepath):
    """Run complete intelligence pipeline"""
    
    print("\n" + "="*80)
    print("🌱 NILE.AG - Complete Farm Intelligence Pipeline")
    print("="*80)
    
    # Load data
    df = load_farm_data(filepath)
    
    # Core analytics
    quality_dist = get_quality_distribution(df)
    declining_products = get_declining_quality_products(df)
    market_comparison = get_market_comparison(df)
    urgent_batches = get_urgent_batches(df)
    harvest_recs = get_harvest_recommendations(df)
    loss_by_category, loss_by_product = get_loss_analysis(df)
    seasonal_insights = get_seasonal_insights(df)
    alerts = generate_alerts(df)
    price_trends = get_price_trend_analysis(df)
    executive_summary = get_executive_summary(df)
    
    # Train models
    quality_model, quality_features = train_quality_prediction_model(df)
    price_model, price_scaler = train_price_prediction_model(df)
    
    return {
        'df': df,
        'quality_distribution': quality_dist,
        'declining_products': declining_products,
        'market_comparison': market_comparison,
        'urgent_batches': urgent_batches,
        'harvest_recommendations': harvest_recs,
        'loss_by_category': loss_by_category,
        'loss_by_product': loss_by_product,
        'seasonal_insights': seasonal_insights,
        'alerts': alerts,
        'price_trends': price_trends,
        'executive_summary': executive_summary,
        'quality_model': quality_model,
        'quality_features': quality_features,
        'price_model': price_model,
        'price_scaler': price_scaler
    }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Run the complete pipeline
    insights = run_all_insights("nile_farm_intelligence.csv")
    
    # Access specific insights
    print("\n" + "="*80)
    print("🎯 Ready for Dashboard Integration")
    print("="*80)
    print("\nAvailable insights in returned dictionary:")
    for key in insights.keys():
        print(f"  • {key}")