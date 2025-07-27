#!/usr/bin/env python3
"""
🎯 AI Module - Main Interface
=============================
واجهة رئيسية لجميع وظائف الذكاء الاصطناعي في BraveBot
"""

from .trends_engine import (
    fetch_viral_trends,
    dynamic_pricing_suggestion, 
    generate_weekly_insights,
    trend_scanner,
    pricing_engine,
    insights_generator
)

__all__ = [
    'fetch_viral_trends',
    'dynamic_pricing_suggestion',
    'generate_weekly_insights',
    'trend_scanner',
    'pricing_engine',
    'insights_generator'
]

__version__ = "1.0.0"
__author__ = "BraveBot AI Team"
