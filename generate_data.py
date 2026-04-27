# generate_data.py - Fresh Produce Quality & Market Intelligence Data Generator


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json

np.random.seed(42)
random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================
N_BATCHES = 20000                       # 20,000 harvest batches
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)
DAYS_RANGE = (END_DATE - START_DATE).days

# ============================================================================
# COMPLETE PRODUCE DATABASE - 100+ PRODUCTS
# ============================================================================
PRODUCE_TYPES = {
    # ===== VEGETABLES =====
    "Tomatoes": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 12,
        "shelf_life_days": 7, "degradation_rate": 0.15, "peak_months": [1,2,3],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 0.8, "color_indicators": ["red", "firmness"]
    },
    "Cherry Tomatoes": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 18,
        "shelf_life_days": 6, "degradation_rate": 0.18, "peak_months": [1,2,3],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 0.8, "color_indicators": ["red", "firmness"]
    },
    "Roma Tomatoes": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 14,
        "shelf_life_days": 8, "degradation_rate": 0.12, "peak_months": [2,3,4],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["red", "firmness"]
    },
    "Lettuce (Iceberg)": {
        "category": "Leafy Green", "subcategory": "Lettuce", "base_price_kg": 9,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [1,2,11,12],
        "temp_sensitivity": 1.5, "humidity_sensitivity": 1.2, "color_indicators": ["green", "crispness"]
    },
    "Lettuce (Romaine)": {
        "category": "Leafy Green", "subcategory": "Lettuce", "base_price_kg": 11,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [1,2,11,12],
        "temp_sensitivity": 1.5, "humidity_sensitivity": 1.2, "color_indicators": ["green", "crispness"]
    },
    "Butter Lettuce": {
        "category": "Leafy Green", "subcategory": "Lettuce", "base_price_kg": 13,
        "shelf_life_days": 4, "degradation_rate": 0.25, "peak_months": [1,2,11,12],
        "temp_sensitivity": 1.6, "humidity_sensitivity": 1.3, "color_indicators": ["green", "crispness"]
    },
    "Spinach": {
        "category": "Leafy Green", "subcategory": "Greens", "base_price_kg": 15,
        "shelf_life_days": 5, "degradation_rate": 0.2, "peak_months": [4,5,6],
        "temp_sensitivity": 1.4, "humidity_sensitivity": 1.1, "color_indicators": ["green", "wilting"]
    },
    "Kale": {
        "category": "Leafy Green", "subcategory": "Greens", "base_price_kg": 18,
        "shelf_life_days": 7, "degradation_rate": 0.15, "peak_months": [4,5,6],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 1.0, "color_indicators": ["green", "crispness"]
    },
    "Swiss Chard": {
        "category": "Leafy Green", "subcategory": "Greens", "base_price_kg": 16,
        "shelf_life_days": 5, "degradation_rate": 0.2, "peak_months": [5,6,7],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.1, "color_indicators": ["green", "wilting"]
    },
    "Arugula": {
        "category": "Leafy Green", "subcategory": "Herbs", "base_price_kg": 22,
        "shelf_life_days": 4, "degradation_rate": 0.25, "peak_months": [4,5,6],
        "temp_sensitivity": 1.5, "humidity_sensitivity": 1.2, "color_indicators": ["green", "freshness"]
    },
    "Cabbage (Green)": {
        "category": "Vegetable", "subcategory": "Brassica", "base_price_kg": 8,
        "shelf_life_days": 21, "degradation_rate": 0.08, "peak_months": [5,6,7],
        "temp_sensitivity": 0.8, "humidity_sensitivity": 0.6, "color_indicators": ["green", "firmness"]
    },
    "Cabbage (Red)": {
        "category": "Vegetable", "subcategory": "Brassica", "base_price_kg": 10,
        "shelf_life_days": 21, "degradation_rate": 0.08, "peak_months": [5,6,7],
        "temp_sensitivity": 0.8, "humidity_sensitivity": 0.6, "color_indicators": ["purple", "firmness"]
    },
    "Broccoli": {
        "category": "Vegetable", "subcategory": "Brassica", "base_price_kg": 16,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [4,5,6],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 1.0, "color_indicators": ["green", "firmness"]
    },
    "Cauliflower": {
        "category": "Vegetable", "subcategory": "Brassica", "base_price_kg": 15,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [7,8,9],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 1.0, "color_indicators": ["white", "firmness"]
    },
    "Brussels Sprouts": {
        "category": "Vegetable", "subcategory": "Brassica", "base_price_kg": 22,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [9,10,11],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.9, "color_indicators": ["green", "firmness"]
    },
    "Bell Peppers (Green)": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 18,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [8,9,10],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["green", "firmness"]
    },
    "Bell Peppers (Red)": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 22,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [8,9,10],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["red", "firmness"]
    },
    "Bell Peppers (Yellow)": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 24,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [8,9,10],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["yellow", "firmness"]
    },
    "Cucumbers": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 14,
        "shelf_life_days": 8, "degradation_rate": 0.14, "peak_months": [10,11,12],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 0.9, "color_indicators": ["green", "firmness"]
    },
    "Zucchini": {
        "category": "Vegetable", "subcategory": "Squash", "base_price_kg": 13,
        "shelf_life_days": 7, "degradation_rate": 0.15, "peak_months": [6,7,8],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 0.9, "color_indicators": ["green", "firmness"]
    },
    "Yellow Squash": {
        "category": "Vegetable", "subcategory": "Squash", "base_price_kg": 15,
        "shelf_life_days": 7, "degradation_rate": 0.15, "peak_months": [6,7,8],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 0.9, "color_indicators": ["yellow", "firmness"]
    },
    "Eggplant": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 17,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [7,8,9],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["purple", "firmness"]
    },
    "Celery": {
        "category": "Vegetable", "subcategory": "Stalk", "base_price_kg": 11,
        "shelf_life_days": 14, "degradation_rate": 0.1, "peak_months": [9,10,11],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 1.0, "color_indicators": ["green", "crispness"]
    },
    "Asparagus": {
        "category": "Vegetable", "subcategory": "Stalk", "base_price_kg": 28,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [4,5,6],
        "temp_sensitivity": 1.4, "humidity_sensitivity": 1.1, "color_indicators": ["green", "firmness"]
    },
    "Green Beans": {
        "category": "Vegetable", "subcategory": "Legume", "base_price_kg": 19,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [5,6,7],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 0.9, "color_indicators": ["green", "firmness"]
    },
    "Snow Peas": {
        "category": "Vegetable", "subcategory": "Legume", "base_price_kg": 25,
        "shelf_life_days": 5, "degradation_rate": 0.2, "peak_months": [3,4,5],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["green", "crispness"]
    },
    "Sugar Snap Peas": {
        "category": "Vegetable", "subcategory": "Legume", "base_price_kg": 27,
        "shelf_life_days": 5, "degradation_rate": 0.2, "peak_months": [3,4,5],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["green", "crispness"]
    },
    "Artichokes": {
        "category": "Vegetable", "subcategory": "Flower", "base_price_kg": 32,
        "shelf_life_days": 7, "degradation_rate": 0.15, "peak_months": [3,4,5],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["green", "firmness"]
    },
    "Okra": {
        "category": "Vegetable", "subcategory": "Fruiting", "base_price_kg": 21,
        "shelf_life_days": 4, "degradation_rate": 0.25, "peak_months": [7,8,9],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["green", "firmness"]
    },
    "Radicchio": {
        "category": "Leafy Green", "subcategory": "Greens", "base_price_kg": 20,
        "shelf_life_days": 7, "degradation_rate": 0.14, "peak_months": [1,2,11,12],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 1.1, "color_indicators": ["red", "crispness"]
    },
    "Endive": {
        "category": "Leafy Green", "subcategory": "Greens", "base_price_kg": 19,
        "shelf_life_days": 7, "degradation_rate": 0.14, "peak_months": [1,2,11,12],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 1.1, "color_indicators": ["green", "crispness"]
    },
    "Fennel": {
        "category": "Vegetable", "subcategory": "Bulb", "base_price_kg": 24,
        "shelf_life_days": 10, "degradation_rate": 0.1, "peak_months": [1,2,11,12],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.9, "color_indicators": ["white", "firmness"]
    },
    "Leeks": {
        "category": "Vegetable", "subcategory": "Bulb", "base_price_kg": 18,
        "shelf_life_days": 10, "degradation_rate": 0.1, "peak_months": [1,2,3,11,12],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.9, "color_indicators": ["green", "firmness"]
    },
    "Rhubarb": {
        "category": "Vegetable", "subcategory": "Stalk", "base_price_kg": 26,
        "shelf_life_days": 7, "degradation_rate": 0.15, "peak_months": [4,5,6],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.9, "color_indicators": ["red", "firmness"]
    },

    # ===== ROOT VEGETABLES =====
    "Potatoes (White)": {
        "category": "Root", "subcategory": "Tuber", "base_price_kg": 7,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [5,6,7],
        "temp_sensitivity": 0.5, "humidity_sensitivity": 0.6, "color_indicators": ["firmness", "sprouting"]
    },
    "Potatoes (Red)": {
        "category": "Root", "subcategory": "Tuber", "base_price_kg": 8,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [5,6,7],
        "temp_sensitivity": 0.5, "humidity_sensitivity": 0.6, "color_indicators": ["firmness", "sprouting"]
    },
    "Potatoes (Sweet)": {
        "category": "Root", "subcategory": "Tuber", "base_price_kg": 13,
        "shelf_life_days": 45, "degradation_rate": 0.04, "peak_months": [4,5,6],
        "temp_sensitivity": 0.6, "humidity_sensitivity": 0.7, "color_indicators": ["firmness", "sprouting"]
    },
    "Potatoes (Purple)": {
        "category": "Root", "subcategory": "Tuber", "base_price_kg": 15,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [5,6,7],
        "temp_sensitivity": 0.5, "humidity_sensitivity": 0.6, "color_indicators": ["firmness", "sprouting"]
    },
    "Onions (Red)": {
        "category": "Root", "subcategory": "Bulb", "base_price_kg": 9,
        "shelf_life_days": 90, "degradation_rate": 0.02, "peak_months": [8,9,10],
        "temp_sensitivity": 0.4, "humidity_sensitivity": 0.5, "color_indicators": ["firmness", "sprouting"]
    },
    "Onions (Brown)": {
        "category": "Root", "subcategory": "Bulb", "base_price_kg": 8,
        "shelf_life_days": 90, "degradation_rate": 0.02, "peak_months": [8,9,10],
        "temp_sensitivity": 0.4, "humidity_sensitivity": 0.5, "color_indicators": ["firmness", "sprouting"]
    },
    "Onions (White)": {
        "category": "Root", "subcategory": "Bulb", "base_price_kg": 10,
        "shelf_life_days": 90, "degradation_rate": 0.02, "peak_months": [8,9,10],
        "temp_sensitivity": 0.4, "humidity_sensitivity": 0.5, "color_indicators": ["firmness", "sprouting"]
    },
    "Shallots": {
        "category": "Root", "subcategory": "Bulb", "base_price_kg": 22,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [5,6,7],
        "temp_sensitivity": 0.5, "humidity_sensitivity": 0.6, "color_indicators": ["firmness", "sprouting"]
    },
    "Carrots (Orange)": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 9,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [6,7,8],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.7, "color_indicators": ["orange", "firmness"]
    },
    "Carrots (Purple)": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 12,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [6,7,8],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.7, "color_indicators": ["purple", "firmness"]
    },
    "Carrots (Yellow)": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 11,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [6,7,8],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.7, "color_indicators": ["yellow", "firmness"]
    },
    "Beetroot": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 11,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [5,6,7],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.7, "color_indicators": ["red", "firmness"]
    },
    "Radishes": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 8,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [3,4,5],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.9, "color_indicators": ["red", "firmness"]
    },
    "Turnips": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 7,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [9,10,11],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.7, "color_indicators": ["white", "firmness"]
    },
    "Parsnips": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 15,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [9,10,11],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.7, "color_indicators": ["white", "firmness"]
    },
    "Celery Root": {
        "category": "Root", "subcategory": "Tuber", "base_price_kg": 16,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [10,11,12],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.7, "color_indicators": ["brown", "firmness"]
    },
    "Horseradish": {
        "category": "Root", "subcategory": "Taproot", "base_price_kg": 28,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [10,11,12],
        "temp_sensitivity": 0.6, "humidity_sensitivity": 0.6, "color_indicators": ["brown", "firmness"]
    },
    "Ginger": {
        "category": "Root", "subcategory": "Rhizome", "base_price_kg": 45,
        "shelf_life_days": 60, "degradation_rate": 0.04, "peak_months": [11,12,1],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.8, "color_indicators": ["brown", "firmness"]
    },
    "Turmeric": {
        "category": "Root", "subcategory": "Rhizome", "base_price_kg": 42,
        "shelf_life_days": 60, "degradation_rate": 0.04, "peak_months": [11,12,1],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.8, "color_indicators": ["orange", "firmness"]
    },
    "Garlic": {
        "category": "Root", "subcategory": "Bulb", "base_price_kg": 50,
        "shelf_life_days": 180, "degradation_rate": 0.01, "peak_months": [10,11,12],
        "temp_sensitivity": 0.3, "humidity_sensitivity": 0.4, "color_indicators": ["white", "firmness"]
    },

    # ===== FRUITS =====
    "Apples (Red Delicious)": {
        "category": "Fruit", "subcategory": "Pome", "base_price_kg": 20,
        "shelf_life_days": 90, "degradation_rate": 0.02, "peak_months": [3,4,5],
        "temp_sensitivity": 0.6, "humidity_sensitivity": 0.5, "color_indicators": ["red", "firmness"]
    },
    "Apples (Granny Smith)": {
        "category": "Fruit", "subcategory": "Pome", "base_price_kg": 22,
        "shelf_life_days": 90, "degradation_rate": 0.02, "peak_months": [3,4,5],
        "temp_sensitivity": 0.6, "humidity_sensitivity": 0.5, "color_indicators": ["green", "firmness"]
    },
    "Apples (Golden)": {
        "category": "Fruit", "subcategory": "Pome", "base_price_kg": 21,
        "shelf_life_days": 90, "degradation_rate": 0.02, "peak_months": [3,4,5],
        "temp_sensitivity": 0.6, "humidity_sensitivity": 0.5, "color_indicators": ["yellow", "firmness"]
    },
    "Apples (Pink Lady)": {
        "category": "Fruit", "subcategory": "Pome", "base_price_kg": 26,
        "shelf_life_days": 90, "degradation_rate": 0.02, "peak_months": [3,4,5],
        "temp_sensitivity": 0.6, "humidity_sensitivity": 0.5, "color_indicators": ["pink", "firmness"]
    },
    "Pears (Williams)": {
        "category": "Fruit", "subcategory": "Pome", "base_price_kg": 18,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [2,3,4],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["yellow", "firmness"]
    },
    "Pears (Packham)": {
        "category": "Fruit", "subcategory": "Pome", "base_price_kg": 19,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [2,3,4],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["green", "firmness"]
    },
    "Pears (Forelle)": {
        "category": "Fruit", "subcategory": "Pome", "base_price_kg": 24,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [2,3,4],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["red", "firmness"]
    },
    "Bananas (Cavendish)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 10,
        "shelf_life_days": 7, "degradation_rate": 0.18, "peak_months": [1,2,3,4,5],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 0.9, "color_indicators": ["yellow", "brown_spots"]
    },
    "Bananas (Baby)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 18,
        "shelf_life_days": 6, "degradation_rate": 0.2, "peak_months": [1,2,3,4,5],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 0.9, "color_indicators": ["yellow", "brown_spots"]
    },
    "Bananas (Red)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 22,
        "shelf_life_days": 6, "degradation_rate": 0.2, "peak_months": [1,2,3,4,5],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 0.9, "color_indicators": ["red", "brown_spots"]
    },
    "Oranges (Navel)": {
        "category": "Citrus", "subcategory": "Orange", "base_price_kg": 18,
        "shelf_life_days": 45, "degradation_rate": 0.04, "peak_months": [6,7,8],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["orange", "firmness"]
    },
    "Oranges (Valencia)": {
        "category": "Citrus", "subcategory": "Orange", "base_price_kg": 16,
        "shelf_life_days": 45, "degradation_rate": 0.04, "peak_months": [9,10,11],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["orange", "firmness"]
    },
    "Oranges (Blood)": {
        "category": "Citrus", "subcategory": "Orange", "base_price_kg": 24,
        "shelf_life_days": 45, "degradation_rate": 0.04, "peak_months": [12,1,2],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["red", "firmness"]
    },
    "Lemons": {
        "category": "Citrus", "subcategory": "Lemon", "base_price_kg": 15,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [4,5,6],
        "temp_sensitivity": 0.6, "humidity_sensitivity": 0.6, "color_indicators": ["yellow", "firmness"]
    },
    "Limes": {
        "category": "Citrus", "subcategory": "Lime", "base_price_kg": 22,
        "shelf_life_days": 21, "degradation_rate": 0.06, "peak_months": [5,6,7],
        "temp_sensitivity": 0.8, "humidity_sensitivity": 0.7, "color_indicators": ["green", "firmness"]
    },
    "Grapefruit": {
        "category": "Citrus", "subcategory": "Grapefruit", "base_price_kg": 14,
        "shelf_life_days": 45, "degradation_rate": 0.04, "peak_months": [6,7,8],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["pink", "firmness"]
    },
    "Avocados (Hass)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 35,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [2,3,4],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.7, "color_indicators": ["green", "firmness"]
    },
    "Avocados (Fuerte)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 32,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [5,6,7],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.7, "color_indicators": ["green", "firmness"]
    },
    "Avocados (Reed)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 38,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [7,8,9],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.7, "color_indicators": ["green", "firmness"]
    },
    "Mangoes (Tommy Atkins)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 22,
        "shelf_life_days": 10, "degradation_rate": 0.14, "peak_months": [11,12,1],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["red", "firmness"]
    },
    "Mangoes (Kent)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 24,
        "shelf_life_days": 10, "degradation_rate": 0.14, "peak_months": [1,2,3],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["green", "firmness"]
    },
    "Mangoes (Keitt)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 26,
        "shelf_life_days": 10, "degradation_rate": 0.14, "peak_months": [2,3,4],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["green", "firmness"]
    },
    "Pineapples": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 28,
        "shelf_life_days": 21, "degradation_rate": 0.07, "peak_months": [1,2,12],
        "temp_sensitivity": 0.9, "humidity_sensitivity": 0.7, "color_indicators": ["yellow", "firmness"]
    },
    "Papayas": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 30,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [9,10,11],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 0.9, "color_indicators": ["orange", "firmness"]
    },
    "Grapes (Red Seedless)": {
        "category": "Fruit", "subcategory": "Berry", "base_price_kg": 35,
        "shelf_life_days": 14, "degradation_rate": 0.1, "peak_months": [1,2,3],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.8, "color_indicators": ["red", "firmness"]
    },
    "Grapes (Green Seedless)": {
        "category": "Fruit", "subcategory": "Berry", "base_price_kg": 32,
        "shelf_life_days": 14, "degradation_rate": 0.1, "peak_months": [1,2,3],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.8, "color_indicators": ["green", "firmness"]
    },
    "Grapes (Black)": {
        "category": "Fruit", "subcategory": "Berry", "base_price_kg": 38,
        "shelf_life_days": 14, "degradation_rate": 0.1, "peak_months": [1,2,3],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.8, "color_indicators": ["black", "firmness"]
    },
    "Strawberries": {
        "category": "Berry", "subcategory": "Soft Fruit", "base_price_kg": 45,
        "shelf_life_days": 3, "degradation_rate": 0.35, "peak_months": [8,9,10],
        "temp_sensitivity": 1.5, "humidity_sensitivity": 1.1, "color_indicators": ["red", "firmness"]
    },
    "Blueberries": {
        "category": "Berry", "subcategory": "Soft Fruit", "base_price_kg": 60,
        "shelf_life_days": 7, "degradation_rate": 0.2, "peak_months": [11,12,1],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["blue", "firmness"]
    },
    "Raspberries": {
        "category": "Berry", "subcategory": "Soft Fruit", "base_price_kg": 65,
        "shelf_life_days": 3, "degradation_rate": 0.38, "peak_months": [7,8,9],
        "temp_sensitivity": 1.6, "humidity_sensitivity": 1.2, "color_indicators": ["red", "firmness"]
    },
    "Blackberries": {
        "category": "Berry", "subcategory": "Soft Fruit", "base_price_kg": 58,
        "shelf_life_days": 4, "degradation_rate": 0.32, "peak_months": [7,8,9],
        "temp_sensitivity": 1.5, "humidity_sensitivity": 1.1, "color_indicators": ["black", "firmness"]
    },
    "Cranberries": {
        "category": "Berry", "subcategory": "Hard Fruit", "base_price_kg": 48,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [10,11,12],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["red", "firmness"]
    },
    "Kiwi": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 25,
        "shelf_life_days": 30, "degradation_rate": 0.05, "peak_months": [4,5,6],
        "temp_sensitivity": 0.8, "humidity_sensitivity": 0.7, "color_indicators": ["brown", "firmness"]
    },
    "Figs": {
        "category": "Fruit", "subcategory": "Soft Fruit", "base_price_kg": 42,
        "shelf_life_days": 5, "degradation_rate": 0.25, "peak_months": [1,2,3,12],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["purple", "firmness"]
    },
    "Dates (Fresh)": {
        "category": "Fruit", "subcategory": "Tropical", "base_price_kg": 55,
        "shelf_life_days": 14, "degradation_rate": 0.1, "peak_months": [9,10,11],
        "temp_sensitivity": 0.9, "humidity_sensitivity": 0.7, "color_indicators": ["brown", "firmness"]
    },
    "Pomegranates": {
        "category": "Fruit", "subcategory": "Berry", "base_price_kg": 38,
        "shelf_life_days": 60, "degradation_rate": 0.03, "peak_months": [3,4,5],
        "temp_sensitivity": 0.7, "humidity_sensitivity": 0.6, "color_indicators": ["red", "firmness"]
    },
    "Nectarines": {
        "category": "Fruit", "subcategory": "Stone Fruit", "base_price_kg": 28,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [11,12,1],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["orange", "firmness"]
    },
    "Peaches": {
        "category": "Fruit", "subcategory": "Stone Fruit", "base_price_kg": 26,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [11,12,1],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["orange", "firmness"]
    },
    "Plums": {
        "category": "Fruit", "subcategory": "Stone Fruit", "base_price_kg": 24,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [12,1,2],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["purple", "firmness"]
    },
    "Apricots": {
        "category": "Fruit", "subcategory": "Stone Fruit", "base_price_kg": 23,
        "shelf_life_days": 7, "degradation_rate": 0.16, "peak_months": [11,12,1],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.8, "color_indicators": ["orange", "firmness"]
    },
    "Watermelon": {
        "category": "Fruit", "subcategory": "Melon", "base_price_kg": 15,
        "shelf_life_days": 21, "degradation_rate": 0.07, "peak_months": [12,1,2],
        "temp_sensitivity": 0.9, "humidity_sensitivity": 0.7, "color_indicators": ["green", "firmness"]
    },
    "Cantaloupe": {
        "category": "Fruit", "subcategory": "Melon", "base_price_kg": 18,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [12,1,2],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.8, "color_indicators": ["orange", "firmness"]
    },
    "Honeydew": {
        "category": "Fruit", "subcategory": "Melon", "base_price_kg": 19,
        "shelf_life_days": 10, "degradation_rate": 0.12, "peak_months": [12,1,2],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.8, "color_indicators": ["green", "firmness"]
    },

    # ===== HERBS =====
    "Fresh Basil": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 48,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [2,3,4],
        "temp_sensitivity": 1.4, "humidity_sensitivity": 1.1, "color_indicators": ["green", "wilting"]
    },
    "Fresh Cilantro": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 45,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [3,4,5],
        "temp_sensitivity": 1.4, "humidity_sensitivity": 1.1, "color_indicators": ["green", "wilting"]
    },
    "Fresh Parsley (Flat)": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 38,
        "shelf_life_days": 7, "degradation_rate": 0.18, "peak_months": [3,4,5],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["green", "wilting"]
    },
    "Fresh Parsley (Curly)": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 36,
        "shelf_life_days": 7, "degradation_rate": 0.18, "peak_months": [3,4,5],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["green", "wilting"]
    },
    "Rosemary": {
        "category": "Herb", "subcategory": "Woody", "base_price_kg": 35,
        "shelf_life_days": 10, "degradation_rate": 0.14, "peak_months": [4,5,6],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.9, "color_indicators": ["green", "freshness"]
    },
    "Thyme": {
        "category": "Herb", "subcategory": "Woody", "base_price_kg": 36,
        "shelf_life_days": 10, "degradation_rate": 0.14, "peak_months": [4,5,6],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.9, "color_indicators": ["green", "freshness"]
    },
    "Mint": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 32,
        "shelf_life_days": 7, "degradation_rate": 0.18, "peak_months": [5,6,7],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.1, "color_indicators": ["green", "wilting"]
    },
    "Dill": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 34,
        "shelf_life_days": 6, "degradation_rate": 0.2, "peak_months": [5,6,7],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["green", "wilting"]
    },
    "Oregano": {
        "category": "Herb", "subcategory": "Woody", "base_price_kg": 33,
        "shelf_life_days": 10, "degradation_rate": 0.14, "peak_months": [5,6,7],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.9, "color_indicators": ["green", "freshness"]
    },
    "Sage": {
        "category": "Herb", "subcategory": "Woody", "base_price_kg": 37,
        "shelf_life_days": 10, "degradation_rate": 0.14, "peak_months": [5,6,7],
        "temp_sensitivity": 1.1, "humidity_sensitivity": 0.9, "color_indicators": ["green", "freshness"]
    },
    "Chives": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 30,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [5,6,7],
        "temp_sensitivity": 1.4, "humidity_sensitivity": 1.1, "color_indicators": ["green", "wilting"]
    },
    "Tarragon": {
        "category": "Herb", "subcategory": "Leafy", "base_price_kg": 40,
        "shelf_life_days": 7, "degradation_rate": 0.18, "peak_months": [4,5,6],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.0, "color_indicators": ["green", "wilting"]
    },
    "Lemongrass": {
        "category": "Herb", "subcategory": "Stalk", "base_price_kg": 25,
        "shelf_life_days": 14, "degradation_rate": 0.1, "peak_months": [6,7,8],
        "temp_sensitivity": 1.0, "humidity_sensitivity": 0.8, "color_indicators": ["green", "freshness"]
    },

    # ===== MUSHROOMS =====
    "Button Mushrooms": {
        "category": "Mushroom", "subcategory": "Fresh", "base_price_kg": 55,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [1,2,3,4,5,6,7,8,9,10,11,12],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.2, "color_indicators": ["white", "firmness"]
    },
    "Cremini Mushrooms": {
        "category": "Mushroom", "subcategory": "Fresh", "base_price_kg": 62,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [1,2,3,4,5,6,7,8,9,10,11,12],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.2, "color_indicators": ["brown", "firmness"]
    },
    "Portobello Mushrooms": {
        "category": "Mushroom", "subcategory": "Fresh", "base_price_kg": 75,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [1,2,3,4,5,6,7,8,9,10,11,12],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.2, "color_indicators": ["brown", "firmness"]
    },
    "Shiitake Mushrooms": {
        "category": "Mushroom", "subcategory": "Specialty", "base_price_kg": 95,
        "shelf_life_days": 7, "degradation_rate": 0.18, "peak_months": [1,2,3,4,5,6,7,8,9,10,11,12],
        "temp_sensitivity": 1.2, "humidity_sensitivity": 1.1, "color_indicators": ["brown", "firmness"]
    },
    "Oyster Mushrooms": {
        "category": "Mushroom", "subcategory": "Specialty", "base_price_kg": 88,
        "shelf_life_days": 5, "degradation_rate": 0.22, "peak_months": [1,2,3,4,5,6,7,8,9,10,11,12],
        "temp_sensitivity": 1.3, "humidity_sensitivity": 1.2, "color_indicators": ["gray", "firmness"]
    }
}

produce_names = list(PRODUCE_TYPES.keys())

# ============================================================================
# MARKETS WITH LOCATION AND PRICE PREMIUMS
# ============================================================================
MARKETS = {
    "Johannesburg Market": {
        "region": "Gauteng", "premium": 1.15, "transport_cost_per_kg_km": 0.5,
        "distance_from_farm_km": 150, "demand_factor": 1.2,
        "buyers": ["Wholesale", "Retail", "Export"]
    },
    "Cape Town Market": {
        "region": "Western Cape", "premium": 1.25, "transport_cost_per_kg_km": 0.6,
        "distance_from_farm_km": 50, "demand_factor": 1.3,
        "buyers": ["Wholesale", "Retail", "Export", "Processing"]
    },
    "Durban Market": {
        "region": "KwaZulu-Natal", "premium": 1.10, "transport_cost_per_kg_km": 0.55,
        "distance_from_farm_km": 200, "demand_factor": 1.1,
        "buyers": ["Wholesale", "Retail", "Export"]
    },
    "Pretoria Market": {
        "region": "Gauteng", "premium": 1.12, "transport_cost_per_kg_km": 0.5,
        "distance_from_farm_km": 160, "demand_factor": 1.15,
        "buyers": ["Wholesale", "Retail"]
    },
    "Port Elizabeth Market": {
        "region": "Eastern Cape", "premium": 1.05, "transport_cost_per_kg_km":0.54,
        "distance_from_farm_km": 250, "demand_factor": 0.95,
        "buyers": ["Wholesale", "Retail"]
    },
    "Bloemfontein Market": {
        "region": "Free State", "premium": 0.98, "transport_cost_per_kg_km": 0.48,
        "distance_from_farm_km": 180, "demand_factor": 0.9,
        "buyers": ["Wholesale"]
    },
    "Nelspruit Market": {
        "region": "Mpumalanga", "premium": 1.08, "transport_cost_per_kg_km": 0.52,
        "distance_from_farm_km": 100, "demand_factor": 1.05,
        "buyers": ["Wholesale", "Retail"]
    },
    "Polokwane Market": {
        "region": "Limpopo", "premium": 1.02, "transport_cost_per_kg_km": 0.53,
        "distance_from_farm_km": 120, "demand_factor": 0.98,
        "buyers": ["Wholesale"]
    },
    "Kimberley Market": {
        "region": "Northern Cape", "premium": 0.95, "transport_cost_per_kg_km": 0.55,
        "distance_from_farm_km": 300, "demand_factor": 0.85,
        "buyers": ["Wholesale"]
    },
    "East London Market": {
        "region": "Eastern Cape", "premium": 1.03, "transport_cost_per_kg_km": 0.54,
        "distance_from_farm_km": 280, "demand_factor": 0.92,
        "buyers": ["Wholesale", "Retail"]
    }
}

# ============================================================================
# QUALITY ASSESSMENT FUNCTIONS
# ============================================================================

def calculate_quality_score(produce_type, days_since_harvest, storage_temp, storage_humidity):
    """Calculate current quality score (0-100) based on degradation factors"""
    produce_data = PRODUCE_TYPES[produce_type]
    
    # Base quality (perfect at harvest)
    base_quality = 100
    
    # Time degradation
    time_decay = (days_since_harvest / produce_data["shelf_life_days"]) * 100 * produce_data["degradation_rate"]
    
    # Temperature impact (ideal temp 4-8°C)
    if storage_temp < 2:
        temp_impact = (2 - storage_temp) * produce_data["temp_sensitivity"] * 3
    elif storage_temp > 10:
        temp_impact = (storage_temp - 10) * produce_data["temp_sensitivity"] * 2
    else:
        temp_impact = 0
    
    # Humidity impact (ideal 85-95%)
    if storage_humidity < 75:
        humidity_impact = (75 - storage_humidity) * produce_data["humidity_sensitivity"] * 0.5
    elif storage_humidity > 95:
        humidity_impact = (storage_humidity - 95) * produce_data["humidity_sensitivity"] * 0.8
    else:
        humidity_impact = 0
    
    # Combined quality
    quality = base_quality - time_decay - temp_impact - humidity_impact
    
    # Add random variation
    quality += np.random.normal(0, 3)
    
    return max(0, min(100, round(quality, 1)))


def get_quality_grade(quality_score):
    """Convert quality score to grade with action recommendation"""
    if quality_score >= 90:
        return "Premium (Grade A)", "Export / High-end retail", "#27ae60", "Maximum value"
    elif quality_score >= 75:
        return "Good (Grade B)", "Local retail / Wholesale", "#2ecc71", "Good selling opportunity"
    elif quality_score >= 60:
        return "Fair (Grade C)", "Processing / Secondary market", "#f39c12", "Sell within 3 days"
    elif quality_score >= 40:
        return "Poor (Grade D)", "Juice / Processing only", "#e67e22", "Urgent sale needed"
    else:
        return "Reject", "Waste / Animal feed", "#e74c3c", "Not suitable for human consumption"


def predict_remaining_shelf_life(produce_type, quality_score):
    """Predict remaining days before produce becomes unsellable"""
    produce_data = PRODUCE_TYPES[produce_type]
    max_shelf = produce_data["shelf_life_days"]
    remaining = (quality_score / 100) * max_shelf
    return max(0, round(remaining, 1))


def calculate_value_loss(produce_type, days_since_harvest, qty_kg, base_price, quality_score):
    """Calculate current value and loss due to degradation"""
    # Value at harvest (100% quality)
    initial_value = qty_kg * base_price
    
    # Value multiplier based on quality
    value_multiplier = quality_score / 100
    
    current_value = initial_value * value_multiplier
    
    # Value lost
    value_lost = initial_value - current_value
    
    return {
        "initial_value": round(initial_value, 2),
        "current_value": round(current_value, 2),
        "value_lost": round(value_lost, 2),
        "loss_percentage": round((value_lost / initial_value) * 100, 1)
    }


# ============================================================================
# MARKET PRICE PREDICTION FUNCTIONS
# ============================================================================

def predict_market_price(produce_type, market_name, date, quality_score):
    """Predict selling price at a specific market"""
    produce_data = PRODUCE_TYPES[produce_type]
    market_data = MARKETS[market_name]
    
    # Base price
    base_price = produce_data["base_price_kg"]
    
    # Seasonal factor
    if date.month in produce_data["peak_months"]:
        seasonal_factor = 0.85  # Lower prices during peak season (more supply)
    else:
        seasonal_factor = 1.25  # Higher prices off-season
    
    # Market premium
    premium = market_data["premium"]
    
    # Demand factor
    demand = market_data["demand_factor"]
    
    # Quality impact
    quality_factor = quality_score / 100
    
    # Random market fluctuation
    fluctuation = np.random.normal(1, 0.1)
    
    # Final price
    price = base_price * seasonal_factor * premium * demand * quality_factor * fluctuation
    
    return round(price, 2)


def get_best_market(produce_type, date, quality_score, qty_kg):
    """Find the most profitable market to sell"""
    best_market = None
    best_net_value = 0
    market_insights = []
    
    for market_name, market_data in MARKETS.items():
        # Price at this market
        price = predict_market_price(produce_type, market_name, date, quality_score)
        
        # Gross revenue
        gross_revenue = qty_kg * price
        
        # Transport cost
        transport_cost = market_data["distance_from_farm_km"] * market_data["transport_cost_per_kg_km"] * qty_kg
        
        # Net revenue
        net_revenue = gross_revenue - transport_cost
        
        # ROI percentage
        roi_pct = ((net_revenue - (qty_kg * PRODUCE_TYPES[produce_type]["base_price_kg"])) / (qty_kg * PRODUCE_TYPES[produce_type]["base_price_kg"])) * 100
        
        market_insights.append({
            "market": market_name,
            "region": market_data["region"],
            "price_per_kg": price,
            "gross_revenue": round(gross_revenue, 2),
            "transport_cost": round(transport_cost, 2),
            "net_revenue": round(net_revenue, 2),
            "roi_percentage": round(roi_pct, 1)
        })
        
        if net_revenue > best_net_value:
            best_net_value = net_revenue
            best_market = market_name
    
    return best_market, best_net_value, market_insights


# ============================================================================
# HARVEST RECOMMENDATION FUNCTIONS
# ============================================================================

def get_harvest_recommendation(produce_type, date, current_quality):
    """Recommend whether to harvest now or wait"""
    produce_data = PRODUCE_TYPES[produce_type]
    
    # Check if in peak season
    is_peak = date.month in produce_data["peak_months"]
    
    # Estimate price trend (simple logic based on seasonality)
    if is_peak:
        price_trend = "declining"
        trend_factor = -0.05
    else:
        price_trend = "rising"
        trend_factor = 0.08
    
    # Quality degradation rate
    daily_quality_loss = produce_data["degradation_rate"] * 10
    
    # Estimated quality in 3 days
    future_quality = max(0, current_quality - daily_quality_loss * 3)
    
    # Estimated price in 3 days (based on trend)
    future_price_factor = 1 + trend_factor * 3
    current_price_estimate = produce_data["base_price_kg"] * (1.2 if is_peak else 1.0)
    future_price_estimate = current_price_estimate * future_price_factor
    
    # Decision logic
    urgency_score = (100 - current_quality) * 0.5 + (1 if is_peak else 0) * 20
    
    if urgency_score > 60:
        recommendation = "HARVEST NOW - Quality declining rapidly"
        urgency = "CRITICAL"
        reason = f"Quality at {current_quality:.0f}%. Daily loss of {daily_quality_loss:.1f} points"
    elif is_peak and current_quality > 75:
        recommendation = "HARVEST NOW - Peak season prices good"
        urgency = "HIGH"
        reason = f"Peak season prices favorable. Quality {current_quality:.0f}%"
    elif future_price_estimate > current_price_estimate * 1.1 and current_quality > 70:
        recommendation = "WAIT 3-5 DAYS - Prices expected to rise"
        urgency = "LOW"
        reason = f"Expected price increase of {((future_price_estimate - current_price_estimate)/current_price_estimate*100):.0f}%"
    elif current_quality < 60:
        recommendation = "HARVEST URGENTLY - Quality at risk"
        urgency = "HIGH"
        reason = f"Quality below 60%. Further delay risks downgrade"
    else:
        recommendation = "MONITOR - Optimal harvest window approaching"
        urgency = "MEDIUM"
        reason = "Current conditions stable. Monitor quality daily"
    
    return recommendation, urgency, round(current_price_estimate, 2), round(future_price_estimate, 2)


# ============================================================================
# MAIN DATA GENERATION
# ============================================================================

def main():
    print("=" * 80)
    print("🌱 NILE.AG - Fresh Produce Quality & Market Intelligence")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   Harvest Batches: {N_BATCHES:,}")
    print(f"   Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"   Produce types: {len(PRODUCE_TYPES)}")
    print(f"   Categories: 8 (Vegetables, Leafy Greens, Roots, Fruits, Citrus, Berries, Herbs, Mushrooms)")
    print(f"   Markets: {len(MARKETS)}")
    print()
    
    # Generate all dates
    all_dates = [START_DATE + timedelta(days=i) for i in range(DAYS_RANGE)]
    harvest_dates = np.random.choice(all_dates, N_BATCHES, replace=True)
    
    batches = []
    progress_step = max(1, N_BATCHES // 10)
    
    for i in range(N_BATCHES):
        if i % progress_step == 0:
            print(f"   Generating: {i/N_BATCHES*100:.0f}% complete ({i:,}/{N_BATCHES:,} batches)")
        
        harvest_date = harvest_dates[i]
        produce = random.choice(produce_names)
        produce_data = PRODUCE_TYPES[produce]
        
        # Harvest quantity (kg) - varies by produce type
        base_qty = int(np.random.gamma(2, 300)) + 100
        if produce_data["category"] in ["Root", "Vegetable"]:
            qty_kg = min(base_qty, 5000)
        elif produce_data["category"] in ["Fruit", "Citrus"]:
            qty_kg = min(base_qty, 3000)
        else:
            qty_kg = min(base_qty, 1000)
        
        # Storage conditions (variation)
        storage_temp = np.random.normal(6, 3)  # Celsius, ideally 4-8°C
        storage_humidity = np.random.normal(75, 12)  # Percentage
        
        # Days since harvest (for this batch)
        max_days = max(1, int(produce_data["shelf_life_days"] * 0.9))
        days_since_harvest = np.random.randint(0, max_days)
        
        # Calculate quality
        quality_score = calculate_quality_score(produce, days_since_harvest, storage_temp, storage_humidity)
        quality_grade, grade_description, grade_color, grade_action = get_quality_grade(quality_score)
        
        # Predicted remaining shelf life
        remaining_days = predict_remaining_shelf_life(produce, quality_score)
        
        # Value analysis
        value_analysis = calculate_value_loss(produce, days_since_harvest, qty_kg, produce_data["base_price_kg"], quality_score)
        
        # Best market recommendation
        best_market, best_net_value, market_insights = get_best_market(produce, harvest_date, quality_score, qty_kg)
        
        # Get top 3 markets summary
        top_markets = sorted(market_insights, key=lambda x: x["net_revenue"], reverse=True)[:3]
        top_markets_str = " | ".join([f"{m['market']}: R{m['net_revenue']:,.0f}" for m in top_markets])
        
        # Harvest recommendation
        harvest_rec, harvest_urgency, price_now, price_future = get_harvest_recommendation(produce, harvest_date, quality_score)
        
        # Determine urgency of selling
        if remaining_days <= 2:
            sell_urgency = "IMMEDIATE"
            sell_action = "Sell within 24 hours"
            sell_price_adjustment = -20
        elif remaining_days <= 5:
            sell_urgency = "HIGH"
            sell_action = "Sell within 3 days"
            sell_price_adjustment = -10
        elif remaining_days <= 10:
            sell_urgency = "MEDIUM"
            sell_action = "Sell within 7 days"
            sell_price_adjustment = -5
        else:
            sell_urgency = "LOW"
            sell_action = "Can store longer, wait for better price"
            sell_price_adjustment = 0
        
        # Calculate urgency score (0-100)
        urgency_score = min(100, (100 - quality_score) * 1.2 + (remaining_days < 5) * 20)
        
        batches.append({
            "batch_id": f"BATCH-{10000 + i}",
            "harvest_date": harvest_date,
            "produce_type": produce,
            "category": produce_data["category"],
            "subcategory": produce_data["subcategory"],
            "quantity_kg": qty_kg,
            "storage_temperature_c": round(storage_temp, 1),
            "storage_humidity_pct": round(storage_humidity, 1),
            "days_since_harvest": days_since_harvest,
            "quality_score": quality_score,
            "quality_grade": quality_grade,
            "grade_description": grade_description,
            "grade_action": grade_action,
            "remaining_shelf_life_days": remaining_days,
            "sell_urgency": sell_urgency,
            "sell_action": sell_action,
            "sell_price_adjustment_pct": sell_price_adjustment,
            "urgency_score": round(urgency_score, 1),
            "initial_value_zar": value_analysis["initial_value"],
            "current_value_zar": value_analysis["current_value"],
            "value_lost_zar": value_analysis["value_lost"],
            "value_loss_percent": value_analysis["loss_percentage"],
            "recommended_market": best_market,
            "expected_revenue_at_recommended_market": round(best_net_value, 2),
            "top_markets_summary": top_markets_str,
            "harvest_recommendation": harvest_rec,
            "harvest_urgency": harvest_urgency,
            "current_market_price_estimate": price_now,
            "forecast_price_in_3_days": price_future,
            "base_price_per_kg": produce_data["base_price_kg"],
            "is_peak_season": 1 if harvest_date.month in produce_data["peak_months"] else 0,
            "season": "Summer" if harvest_date.month in [12,1,2] else "Autumn" if harvest_date.month in [3,4,5] else "Winter" if harvest_date.month in [6,7,8] else "Spring"
        })
    
    print(f"   Generating: 100% complete")
    print()
    
    # Create DataFrame
    print("📊 Processing data...")
    df = pd.DataFrame(batches)
    
    # Add derived columns
    df["year"] = df["harvest_date"].dt.year
    df["month"] = df["harvest_date"].dt.month
    df["quarter"] = df["harvest_date"].dt.quarter
    df["weekday"] = df["harvest_date"].dt.dayofweek
    df["weekday_name"] = df["weekday"].map({0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"})
    
    # Add profit margin calculation
    df["production_cost_estimate"] = (df["quantity_kg"] * df["base_price_per_kg"] * 0.6).round(2)
    df["estimated_profit"] = (df["expected_revenue_at_recommended_market"] - df["production_cost_estimate"]).round(2)
    df["profit_margin_pct"] = ((df["estimated_profit"] / df["production_cost_estimate"]) * 100).round(1)
    
    # Add value efficiency ratio
    df["value_efficiency"] = (df["current_value_zar"] / df["initial_value_zar"] * 100).round(1)
    
    # Sort by date
    df = df.sort_values("harvest_date").reset_index(drop=True)
    
    # ============================================================================
    # SAVE TO CSV
    # ============================================================================
    output_file = "nile_farm_intelligence.csv"
    df.to_csv(output_file, index=False)
    
    # ============================================================================
    # CREATE MARKET PRICE HISTORY FILE
    # ============================================================================
    print("\n📊 Creating market price history...")
    market_history = []
    
    for date in all_dates[::3]:  # Every 3 days
        for produce in produce_names[:20]:  # Top 20 products for market history
            produce_data = PRODUCE_TYPES[produce]
            for market in MARKETS.keys():
                base_quality = 85  # Assume good quality for price tracking
                price = predict_market_price(produce, market, date, base_quality)
                market_history.append({
                    "date": date,
                    "produce_type": produce,
                    "category": produce_data["category"],
                    "market": market,
                    "price_per_kg": price,
                    "is_peak_season": 1 if date.month in produce_data["peak_months"] else 0
                })
    
    market_df = pd.DataFrame(market_history)
    market_df.to_csv("nile_market_prices.csv", index=False)
    
    # ============================================================================
    # CREATE QUALITY DEGRADATION PROFILES
    # ============================================================================
    print("\n📊 Creating quality degradation profiles...")
    degradation_profiles = []
    
    for produce in produce_names:
        produce_data = PRODUCE_TYPES[produce]
        for day in range(0, produce_data["shelf_life_days"] + 1, 2):
            quality = 100 - (day / produce_data["shelf_life_days"]) * 100 * produce_data["degradation_rate"]
            quality = max(0, quality)
            degradation_profiles.append({
                "produce_type": produce,
                "category": produce_data["category"],
                "days_after_harvest": day,
                "expected_quality": round(quality, 1),
                "shelf_life_days": produce_data["shelf_life_days"],
                "degradation_rate": produce_data["degradation_rate"]
            })
    
    degradation_df = pd.DataFrame(degradation_profiles)
    degradation_df.to_csv("nile_quality_degradation.csv", index=False)
    
    # ============================================================================
    # STATISTICS
    # ============================================================================
    print("\n" + "=" * 80)
    print("✅ DATA GENERATION COMPLETE!")
    print("=" * 80)
    
    print(f"\n📁 Files Created:")
    print(f"   1. {output_file} - Main farm intelligence data ({len(df):,} batches)")
    print(f"   2. nile_market_prices.csv - Market price history ({len(market_df):,} records)")
    print(f"   3. nile_quality_degradation.csv - Quality profiles ({len(degradation_df)} records)")
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total batches: {len(df):,}")
    print(f"   Unique produce types: {df['produce_type'].nunique()}")
    print(f"   Categories: {df['category'].nunique()}")
    print(f"   Date range: {df['harvest_date'].min().date()} to {df['harvest_date'].max().date()}")
    
    print(f"\n💰 Financial Summary:")
    print(f"   Total initial value: R{df['initial_value_zar'].sum():,.2f}")
    print(f"   Total current value: R{df['current_value_zar'].sum():,.2f}")
    print(f"   Total value lost: R{df['value_lost_zar'].sum():,.2f}")
    print(f"   Average quality score: {df['quality_score'].mean():.1f}")
    print(f"   Average profit margin: {df['profit_margin_pct'].mean():.1f}%")
    
    print(f"\n📈 Quality Distribution:")
    quality_dist = df['quality_grade'].value_counts()
    for grade, count in quality_dist.items():
        pct = count / len(df) * 100
        print(f"   {grade}: {count:,} batches ({pct:.1f}%)")
    
    print(f"\n🚨 Urgency Distribution:")
    urgency_dist = df['sell_urgency'].value_counts()
    for urgency, count in urgency_dist.items():
        pct = count / len(df) * 100
        print(f"   {urgency}: {count:,} batches ({pct:.1f}%)")
    
    print(f"\n🏆 Top 10 Produce by Value:")
    top_produce = df.groupby('produce_type')['current_value_zar'].sum().sort_values(ascending=False).head(10)
    for idx, (produce, value) in enumerate(top_produce.items(), 1):
        print(f"   {idx}. {produce}: R{value/1_000_000:.2f}M")
    
    print(f"\n📍 Market Performance:")
    market_perf = df.groupby('recommended_market').agg({
        'batch_id': 'count',
        'expected_revenue_at_recommended_market': 'sum'
    }).round(2)
    market_perf.columns = ['batches', 'total_revenue']
    market_perf = market_perf.sort_values('total_revenue', ascending=False)
    for market, row in market_perf.head(5).iterrows():
        print(f"   {market}: {int(row['batches'])} batches, R{row['total_revenue']/1_000_000:.2f}M revenue")
    
    print("\n" + "=" * 80)
    print("🎯 NEXT STEPS:")
    print("   1. Run: streamlit run app.py")
    print("   2. Upload 'nile_farm_intelligence.csv' to the Farm Intelligence Platform")
    print("   3. Analyze quality degradation patterns")
    print("   4. Get harvest and market recommendations")
    print("=" * 80)
    
    # Create sample files for quick testing
    sample_sizes = {"tiny": 100, "small": 1000, "medium": 5000}
    for name, size in sample_sizes.items():
        if size < len(df):
            df.head(size).to_csv(f"nile_farm_sample_{name}.csv", index=False)
            print(f"\n💡 {name.capitalize()} sample: nile_farm_sample_{name}.csv ({size:,} rows)")


if __name__ == "__main__":
    main()
