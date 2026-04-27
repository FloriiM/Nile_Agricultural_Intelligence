# generate_images_enhanced.py - Additional Professional Visualizations (FIXED)

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.patheffects import withStroke
import numpy as np
import seaborn as sns
import matplotlib.gridspec as gridspec
import os
import pandas as pd
from datetime import datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0-8-darkgrid')
sns.set_palette("husl")
sns.set_context("talk", font_scale=0.8)

# Create output directories
os.makedirs("images", exist_ok=True)
os.makedirs("images/dashboard", exist_ok=True)
os.makedirs("images/charts", exist_ok=True)

print("=" * 70)
print("🌱 Generating Enhanced Farm Intelligence Visualizations")
print("=" * 70)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def ensure_dir(directory):
    """Ensure directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_figure(fig, filename, dpi=150, bbox_inches='tight'):
    """Save figure with consistent settings"""
    try:
        fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches, facecolor='white')
        print(f"  ✓ Saved: {filename}")
        return True
    except Exception as e:
        print(f"  ✗ Error saving {filename}: {e}")
        return False
    finally:
        plt.close(fig)

# ============================================================================
# IMAGE 9: Supply Chain Risk Heatmap
# ============================================================================
print("\n📊 Image 9: Supply Chain Risk Heatmap")

fig, ax = plt.subplots(1, 1, figsize=(14, 10))

# Create risk matrix
risk_factors = ['Harvest Delay', 'Poor Storage', 'Transport Issues', 'Market Volatility', 
                'Quality Degradation', 'Labor Shortage', 'Weather Events', 'Pest Infestation']
products = ['Strawberries', 'Herbs', 'Tomatoes', 'Avocados', 'Apples', 'Potatoes', 'Lettuce', 'Grapes']

np.random.seed(42)
risk_matrix = np.random.uniform(0.2, 0.95, size=(len(risk_factors), len(products)))

# Create custom colormap
colors_risk = ['#2ecc71', '#f39c12', '#e74c3c']
cmap_risk = LinearSegmentedColormap.from_list('risk', colors_risk, N=100)

im = ax.imshow(risk_matrix, cmap=cmap_risk, aspect='auto', vmin=0, vmax=1)

ax.set_xticks(range(len(products)))
ax.set_yticks(range(len(risk_factors)))
ax.set_xticklabels(products, fontsize=10, fontweight='bold', rotation=45, ha='right')
ax.set_yticklabels(risk_factors, fontsize=11, fontweight='bold')
ax.set_xlabel('Products', fontsize=13, fontweight='bold')
ax.set_ylabel('Risk Factors', fontsize=13, fontweight='bold')
ax.set_title('Supply Chain Risk Heatmap', fontsize=16, fontweight='bold')

# Add text annotations
for i in range(len(risk_factors)):
    for j in range(len(products)):
        if risk_matrix[i, j] > 0.7:
            text_color = 'white'
        else:
            text_color = 'black'
        ax.text(j, i, f'{risk_matrix[i, j]:.0%}', ha="center", va="center", 
                color=text_color, fontsize=8, fontweight='bold')

# Add colorbar
cbar = plt.colorbar(im, ax=ax, label='Risk Level', fraction=0.046, pad=0.04)
cbar.set_ticks([0, 0.5, 1])
cbar.set_ticklabels(['Low', 'Medium', 'High'])

plt.tight_layout()
save_figure(fig, 'images/09_supply_chain_risk_heatmap.png')

# ============================================================================
# IMAGE 10: Profit Optimization Curve
# ============================================================================
print("\n📊 Image 10: Profit Optimization Curve")

fig, axes = plt.subplots(1, 2, figsize=(15, 7))
fig.suptitle('Profit Optimization Analysis', fontsize=16, fontweight='bold')

# Subplot 1: Quality vs Price Curve
ax1 = axes[0]
quality = np.linspace(40, 100, 30)
price_multiplier = 0.3 + 0.007 * quality + 0.0001 * quality**2
ax1.plot(quality, price_multiplier, linewidth=3, color='#2ecc71')
ax1.fill_between(quality, price_multiplier, 0.3, alpha=0.3, color='#2ecc71')
ax1.set_xlabel('Quality Score (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Price Multiplier', fontsize=12, fontweight='bold')
ax1.set_title('Quality-Price Relationship', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Add optimal point
optimal_q = 85
optimal_p = 0.3 + 0.007 * optimal_q + 0.0001 * optimal_q**2
ax1.plot(optimal_q, optimal_p, 'ro', markersize=12)
ax1.annotate(f'Optimal: {optimal_q}%', xy=(optimal_q, optimal_p), 
             xytext=(70, 0.7), arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=10, fontweight='bold')

# Subplot 2: Profit vs Harvest Time
ax2 = axes[1]
days = np.arange(0, 30)
profit_curve = 100 * np.exp(-0.05 * days) * (1 + 0.1 * np.sin(days/5))
ax2.plot(days, profit_curve, linewidth=3, color='#3498db')
ax2.fill_between(days, profit_curve, 0, alpha=0.3, color='#3498db')
ax2.set_xlabel('Days After Harvest', fontsize=12, fontweight='bold')
ax2.set_ylabel('Profit Potential (%)', fontsize=12, fontweight='bold')
ax2.set_title('Profit Decay Curve', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Add optimal harvest window
ax2.axvspan(3, 7, alpha=0.3, color='green', label='Optimal Harvest Window')
ax2.legend(loc='upper right', fontsize=10)

plt.tight_layout()
save_figure(fig, 'images/10_profit_optimization_curve.png')

# ============================================================================
# IMAGE 11: Real-time Monitoring Dashboard
# ============================================================================
print("\n📊 Image 11: Real-time Monitoring Dashboard")

fig = plt.figure(figsize=(16, 10))
fig.suptitle('Real-time Farm Monitoring Dashboard', fontsize=18, fontweight='bold', y=0.98)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

# Temperature Monitor
ax1 = fig.add_subplot(gs[0, 0])
hours = np.arange(0, 24)
np.random.seed(42)
temp = 6 + 2 * np.sin(hours/24 * 2 * np.pi) + np.random.normal(0, 0.5, 24)
ax1.plot(hours, temp, 'o-', linewidth=2, color='#e74c3c', markersize=6)
ax1.fill_between(hours, temp, 4, alpha=0.3, color='#e74c3c')
ax1.axhline(y=8, color='orange', linestyle='--', linewidth=1.5, label='Max Ideal')
ax1.axhline(y=4, color='blue', linestyle='--', linewidth=1.5, label='Min Ideal')
ax1.set_xlabel('Hour', fontsize=10)
ax1.set_ylabel('Temperature (°C)', fontsize=10)
ax1.set_title('Cold Storage Temperature', fontsize=11, fontweight='bold')
ax1.legend(fontsize=8, loc='upper right')
ax1.grid(True, alpha=0.3)

# Humidity Monitor
ax2 = fig.add_subplot(gs[0, 1])
humidity = 85 + 5 * np.sin(hours/24 * 2 * np.pi) + np.random.normal(0, 2, 24)
ax2.plot(hours, humidity, 's-', linewidth=2, color='#3498db', markersize=6)
ax2.fill_between(hours, humidity, 80, alpha=0.3, color='#3498db')
ax2.axhline(y=95, color='red', linestyle='--', linewidth=1.5, label='Max Ideal')
ax2.axhline(y=85, color='green', linestyle='--', linewidth=1.5, label='Target')
ax2.set_xlabel('Hour', fontsize=10)
ax2.set_ylabel('Humidity (%)', fontsize=10)
ax2.set_title('Storage Humidity', fontsize=11, fontweight='bold')
ax2.legend(fontsize=8, loc='upper right')
ax2.grid(True, alpha=0.3)

# Quality Alert
ax3 = fig.add_subplot(gs[0, 2])
ax3.axis('off')
alerts = [
    ('⚠️ Temperature Spike', '3:15 AM', 'High'),
    ('⚠️ Humidity Drop', '5:30 AM', 'Medium'),
    ('✅ Quality Check', '8:00 AM', 'Low'),
    ('🚨 Urgent Sale', '10:45 AM', 'Critical')
]
y_pos = 0.85
for alert, time, severity in alerts:
    color = {'High': '#f39c12', 'Medium': '#e67e22', 'Low': '#3498db', 'Critical': '#e74c3c'}[severity]
    ax3.text(0.1, y_pos, alert, fontsize=10, fontweight='bold', color=color)
    ax3.text(0.65, y_pos, time, fontsize=9, color='#666')
    y_pos -= 0.2
ax3.set_title('Active Alerts', fontsize=11, fontweight='bold', y=0.95)

# Inventory Status
ax4 = fig.add_subplot(gs[1, 0:2])
products_list = ['Strawberries', 'Herbs', 'Tomatoes', 'Avocados', 'Apples']
current = [150, 200, 500, 300, 1000]
optimal = [100, 150, 400, 250, 800]
x = np.arange(len(products_list))
width = 0.35
ax4.bar(x - width/2, current, width, label='Current', color='#2ecc71', edgecolor='black', linewidth=0.5)
ax4.bar(x + width/2, optimal, width, label='Optimal', color='#3498db', alpha=0.7, edgecolor='black', linewidth=0.5)
ax4.set_xlabel('Product', fontsize=10)
ax4.set_ylabel('Quantity (kg)', fontsize=10)
ax4.set_title('Inventory vs Optimal Levels', fontsize=11, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(products_list, rotation=45, ha='right')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3, axis='y')

# Sales Velocity
ax5 = fig.add_subplot(gs[1, 2])
velocity = [2.5, 1.8, 3.2, 1.5, 0.8]
bars = ax5.barh(products_list, velocity, color=['#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6'])
ax5.set_xlabel('Sales (kg/day)', fontsize=10)
ax5.set_title('Sales Velocity', fontsize=11, fontweight='bold')
for bar, v in zip(bars, velocity):
    ax5.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, 
             f'{v:.1f}', va='center', fontsize=9)
ax5.grid(True, alpha=0.3, axis='x')

# Alert Summary
ax6 = fig.add_subplot(gs[2, :])
ax6.axis('off')
summary_text = """SUMMARY:
• 3 batches require immediate sale (strawberries, herbs, raspberries)
• Cold storage temperature above ideal in Zone B - check cooling system
• Quality degradation rate increased by 15% this week
• Market prices expected to rise for avocados (+8%) next week"""
ax6.text(0.05, 0.5, summary_text, fontsize=11, va='center',
         bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#3498db', linewidth=2))

plt.tight_layout()
save_figure(fig, 'images/11_realtime_monitoring_dashboard.png')

# ============================================================================
# IMAGE 12: Interactive Market Map Visualization
# ============================================================================
print("\n📊 Image 12: Interactive Market Map")

fig, ax = plt.subplots(1, 1, figsize=(14, 10))

# Market locations (simplified coordinates)
markets_data = {
    'Cape Town': {'x': 1, 'y': 3, 'premium': 1.25, 'revenue': 450000},
    'Johannesburg': {'x': 4, 'y': 2, 'premium': 1.15, 'revenue': 380000},
    'Durban': {'x': 5, 'y': 1, 'premium': 1.10, 'revenue': 320000},
    'Pretoria': {'x': 4.5, 'y': 2.5, 'premium': 1.12, 'revenue': 290000},
    'Port Elizabeth': {'x': 2, 'y': 1.5, 'premium': 1.05, 'revenue': 210000},
    'Bloemfontein': {'x': 3, 'y': 2, 'premium': 0.98, 'revenue': 150000},
}

# Plot connections (transport routes)
market_names = list(markets_data.keys())
for i in range(len(market_names)):
    for j in range(i + 1, len(market_names)):
        data1 = markets_data[market_names[i]]
        data2 = markets_data[market_names[j]]
        ax.plot([data1['x'], data2['x']], [data1['y'], data2['y']], 
               'gray', linewidth=1, alpha=0.3, linestyle='--')

# Plot market nodes
for market, data in markets_data.items():
    size = data['revenue'] / 15000
    if data['premium'] > 1.15:
        color = '#2ecc71'
    elif data['premium'] > 1.05:
        color = '#f39c12'
    else:
        color = '#e74c3c'
    ax.scatter(data['x'], data['y'], s=size, c=color, alpha=0.6, edgecolors='black', linewidth=2, zorder=5)
    ax.annotate(market, (data['x'], data['y']), xytext=(5, 5), textcoords='offset points',
                fontsize=10, fontweight='bold', color='#2c3e50')
    
    # Add premium label
    premium_text = f"+{int((data['premium']-1)*100)}%"
    ax.annotate(premium_text, (data['x'], data['y']), xytext=(0, 15), textcoords='offset points',
                fontsize=9, color=color, fontweight='bold', ha='center')

# Add farm location
ax.scatter(3.5, 1.8, s=300, c='red', marker='s', edgecolors='white', linewidth=3, zorder=6, label='Main Farm')
ax.annotate('🏠 Main Farm', (3.5, 1.8), xytext=(10, -15), textcoords='offset points',
            fontsize=11, fontweight='bold', color='red')

ax.set_xlim(0, 6.5)
ax.set_ylim(0, 4)
ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
ax.set_title('Market Map: Premiums & Transport Routes', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)

# Add legend
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ecc71', markersize=12, label='High Premium (>15%)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#f39c12', markersize=12, label='Medium Premium (5-15%)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', markersize=12, label='Low Premium (<5%)'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=12, label='Farm Location')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

plt.tight_layout()
save_figure(fig, 'images/12_interactive_market_map.png')

# ============================================================================
# IMAGE 13: Predictive Analytics Dashboard
# ============================================================================
print("\n📊 Image 13: Predictive Analytics Dashboard")

fig = plt.figure(figsize=(16, 10))
fig.suptitle('AI-Powered Predictive Analytics', fontsize=18, fontweight='bold', y=0.98)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

# Price Forecast
ax1 = fig.add_subplot(gs[0, 0])
dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
np.random.seed(42)
historical = 50 + 10 * np.sin(np.arange(90) * 2 * np.pi / 30) + np.random.normal(0, 2, 90)
forecast = 50 + 10 * np.sin(np.arange(90, 120) * 2 * np.pi / 30) + np.random.normal(0, 2, 30)
forecast_dates = pd.date_range(start='2024-04-01', periods=30, freq='D')

ax1.plot(dates, historical, linewidth=2, color='#3498db', label='Historical')
ax1.plot(forecast_dates, forecast, linewidth=2, color='#e74c3c', linestyle='--', label='Forecast')
ax1.fill_between(forecast_dates, forecast - 5, forecast + 5, alpha=0.3, color='#e74c3c')
ax1.set_xlabel('Date', fontsize=10)
ax1.set_ylabel('Price (R/kg)', fontsize=10)
ax1.set_title('Price Forecast - Next 30 Days', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, alpha=0.3)

# Demand Prediction
ax2 = fig.add_subplot(gs[0, 1])
products_pred = ['Strawberries', 'Herbs', 'Tomatoes', 'Avocados', 'Apples']
demand_current = [85, 72, 68, 75, 65]
demand_forecast = [78, 80, 72, 85, 70]
x = np.arange(len(products_pred))
width = 0.35
ax2.bar(x - width/2, demand_current, width, label='Current Demand', color='#3498db', edgecolor='black', linewidth=0.5)
ax2.bar(x + width/2, demand_forecast, width, label='Forecast Demand', color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=0.5)
ax2.set_xlabel('Product', fontsize=10)
ax2.set_ylabel('Demand Index', fontsize=10)
ax2.set_title('Demand Forecast', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(products_pred, rotation=45, ha='right')
ax2.legend(loc='upper right', fontsize=9)
ax2.grid(True, alpha=0.3, axis='y')

# Quality Prediction
ax3 = fig.add_subplot(gs[1, 0])
days = np.arange(0, 14)
current_quality = 85
degradation_rate = 0.12
predicted_quality = current_quality * np.exp(-degradation_rate * days)
confidence_lower = predicted_quality * 0.9
confidence_upper = predicted_quality * 1.1

ax3.plot(days, predicted_quality, linewidth=2, color='#2ecc71', label='Predicted')
ax3.fill_between(days, confidence_lower, confidence_upper, alpha=0.3, color='#2ecc71')
ax3.axhline(y=75, color='orange', linestyle='--', linewidth=1.5, label='Good Threshold')
ax3.axhline(y=60, color='red', linestyle='--', linewidth=1.5, label='Fair Threshold')
ax3.set_xlabel('Days', fontsize=10)
ax3.set_ylabel('Quality Score (%)', fontsize=10)
ax3.set_title('Quality Prediction - Next 14 Days', fontsize=12, fontweight='bold')
ax3.legend(loc='upper right', fontsize=9)
ax3.grid(True, alpha=0.3)

# Risk Assessment
ax4 = fig.add_subplot(gs[1, 1])
risks = ['Price Drop', 'Quality Loss', 'Supply Chain', 'Labor', 'Weather']
risk_prob = [0.35, 0.45, 0.25, 0.15, 0.55]
risk_impact = [0.8, 0.7, 0.6, 0.5, 0.9]
risk_score = [p * i * 100 for p, i in zip(risk_prob, risk_impact)]

bars = ax4.barh(risks, risk_score, color=['#e74c3c', '#f39c12', '#3498db', '#95a5a6', '#9b59b6'])
ax4.set_xlabel('Risk Score', fontsize=10)
ax4.set_title('Risk Assessment Matrix', fontsize=12, fontweight='bold')
for bar, score in zip(bars, risk_score):
    ax4.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
             f'{score:.0f}', va='center', fontsize=9, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
save_figure(fig, 'images/13_predictive_analytics_dashboard.png')

# ============================================================================
# IMAGE 14: ROI Calculator Dashboard
# ============================================================================
print("\n📊 Image 14: ROI Calculator Dashboard")

fig, axes = plt.subplots(1, 2, figsize=(15, 7))
fig.suptitle('ROI & Investment Analysis', fontsize=16, fontweight='bold')

# Subplot 1: ROI by Product
ax1 = axes[0]
products_roi = ['Avocados', 'Strawberries', 'Herbs', 'Tomatoes', 'Apples', 'Potatoes']
roi = [45, 38, 35, 28, 22, 18]
investment = [150000, 120000, 80000, 100000, 90000, 70000]

scatter = ax1.scatter(investment, roi, s=[i/500 for i in investment], c=roi, cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=1.5)
for i, product in enumerate(products_roi):
    ax1.annotate(product, (investment[i], roi[i]), fontsize=9, fontweight='bold')
ax1.set_xlabel('Investment (R)', fontsize=12, fontweight='bold')
ax1.set_ylabel('ROI (%)', fontsize=12, fontweight='bold')
ax1.set_title('Investment vs ROI', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax1, label='ROI %')
cbar.ax.tick_params(labelsize=9)

# Subplot 2: Break-even Analysis
ax2 = axes[1]
weeks = np.arange(0, 52)
cumulative_revenue = 50000 * (1 - np.exp(-weeks/10)) * weeks * 0.5
total_investment = 200000
ax2.plot(weeks, cumulative_revenue, linewidth=3, color='#2ecc71', label='Cumulative Revenue')
ax2.axhline(y=total_investment, color='#e74c3c', linestyle='--', linewidth=2, label='Total Investment')
break_even_mask = cumulative_revenue >= total_investment
if np.any(break_even_mask):
    break_even_week = np.where(break_even_mask)[0][0]
else:
    break_even_week = 0
ax2.axvline(x=break_even_week, color='#3498db', linestyle='--', linewidth=2, label=f'Break-even: Week {break_even_week}')
ax2.fill_between(weeks, cumulative_revenue, total_investment, where=(cumulative_revenue < total_investment), 
                 alpha=0.3, color='#e74c3c', label='Loss Zone')
ax2.fill_between(weeks, cumulative_revenue, total_investment, where=(cumulative_revenue >= total_investment), 
                 alpha=0.3, color='#2ecc71', label='Profit Zone')
ax2.set_xlabel('Weeks', fontsize=12, fontweight='bold')
ax2.set_ylabel('Amount (R)', fontsize=12, fontweight='bold')
ax2.set_title('Break-even Analysis', fontsize=13, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
save_figure(fig, 'images/14_roi_calculator_dashboard.png')

# ============================================================================
# IMAGE 15: Farm Operations Timeline
# ============================================================================
print("\n📊 Image 15: Farm Operations Timeline")

fig, ax = plt.subplots(1, 1, figsize=(16, 8))

# Create Gantt-like timeline
operations = [
    'Planning', 'Soil Prep', 'Planting', 'Irrigation', 'Fertilization',
    'Pest Control', 'Harvest Prep', 'Harvest', 'Post-Harvest', 'Packaging',
    'Transport', 'Market Sale'
]

start_times = [0, 10, 20, 25, 30, 35, 40, 45, 48, 52, 55, 58]
durations = [10, 10, 5, 5, 5, 5, 5, 3, 4, 3, 3, 7]

colors = ['#3498db', '#3498db', '#3498db', '#2ecc71', '#2ecc71', '#2ecc71', 
          '#f39c12', '#e74c3c', '#e74c3c', '#9b59b6', '#9b59b6', '#27ae60']

for i, (op, start, duration, color) in enumerate(zip(operations, start_times, durations, colors)):
    ax.barh(i, duration, left=start, height=0.6, color=color, edgecolor='black', linewidth=1, alpha=0.8)
    ax.text(start + duration/2, i, op, ha='center', va='center', fontsize=9, fontweight='bold', color='white')

# Add milestone markers
milestones = {
    'Critical Quality Window': 42,
    'Max Price Point': 46,
    'Last Sale Date': 58,
    'Break-even Point': 35
}

for milestone, day in milestones.items():
    ax.scatter(day, -0.5, marker='v', s=100, color='red', zorder=5)
    ax.annotate(milestone, (day, -0.5), xytext=(0, -30), textcoords='offset points',
                ha='center', fontsize=8, fontweight='bold', color='red')

ax.set_yticks(range(len(operations)))
ax.set_yticklabels(operations, fontsize=10)
ax.set_xlabel('Days', fontsize=12, fontweight='bold')
ax.set_title('Farm Operations Timeline with Critical Milestones', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
ax.set_xlim(0, 70)

plt.tight_layout()
save_figure(fig, 'images/15_farm_operations_timeline.png')

# ============================================================================
# CREATE INDEX FILE FOR ALL IMAGES
# ============================================================================
print("\n📄 Creating image index file...")

images = [
    ("01_farm_dashboard_overview.png", "Farm Intelligence Dashboard Overview"),
    ("02_quality_degradation_curves.png", "Quality Degradation Curves"),
    ("03_market_price_heatmap.png", "Market Price Comparison Heatmap"),
    ("04_harvest_timing_optimizer.png", "Harvest Timing Optimizer"),
    ("05_loss_analysis_dashboard.png", "Loss Analysis Dashboard"),
    ("06_seasonal_price_calendar.png", "Seasonal Price Calendar"),
    ("07_decision_engine.png", "Decision Engine - Actionable Insights"),
    ("08_executive_dashboard.png", "Executive Dashboard"),
    ("09_supply_chain_risk_heatmap.png", "Supply Chain Risk Heatmap"),
    ("10_profit_optimization_curve.png", "Profit Optimization Curve"),
    ("11_realtime_monitoring_dashboard.png", "Real-time Monitoring Dashboard"),
    ("12_interactive_market_map.png", "Interactive Market Map"),
    ("13_predictive_analytics_dashboard.png", "Predictive Analytics Dashboard"),
    ("14_roi_calculator_dashboard.png", "ROI Calculator Dashboard"),
    ("15_farm_operations_timeline.png", "Farm Operations Timeline")
]

with open('images/README.md', 'w') as f:
    f.write("# Farm Intelligence Platform - Image Gallery\n\n")
    f.write("## Generated Visualizations\n\n")
    f.write("| # | Image | Description |\n")
    f.write("|---|-------|-------------|\n")
    
    for idx, (img, desc) in enumerate(images, 1):
        f.write(f"| {idx} | ![{desc}]({img}) | {desc} |\n")
    
    f.write("\n\n## Usage\n\n")
    f.write("These images can be used for:\n")
    f.write("- Presentations and reports\n")
    f.write("- Dashboard assets\n")
    f.write("- Training materials\n")
    f.write("- Marketing collateral\n")

print("  ✓ Saved: images/README.md")

# Verify all images were created
print("\n" + "=" * 70)
print("📁 Generated Images Summary")
print("=" * 70)

for img, desc in images:
    img_path = f"images/{img}"
    if os.path.exists(img_path):
        size = os.path.getsize(img_path) / 1024
        print(f"  ✓ {img:35} ({size:6.1f} KB) - {desc}")
    else:
        print(f"  ✗ {img:35} (NOT FOUND) - {desc}")

print("\n" + "=" * 70)
print("✅ ENHANCED IMAGE GENERATION COMPLETE!")
print("=" * 70)
print(f"\n📁 Total Images Generated: {len(images)}")
print(f"   Location: 'images/' directory")
print("\n🎯 Image Categories:")
print("   • Dashboard Views: 5 images")
print("   • Analytics Charts: 4 images")
print("   • Decision Support: 3 images")
print("   • Predictive Models: 3 images")
print("   • Operations: 1 image")
print("\n🚀 Next Steps:")
print("   1. Use these images in presentations and reports")
print("   2. Embed in Streamlit dashboard as static assets")
print("   3. Create animated versions for interactive displays")
print("   4. Use as training material for farm staff")
print("=" * 70)
