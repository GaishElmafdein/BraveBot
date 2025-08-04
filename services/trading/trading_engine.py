#!/usr/bin/env python3
"""
📈 Trading Intelligence Engine
==============================
محرك التداول الذكي للعملات والأسهم
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import yfinance as yf
from decimal import Decimal

class AssetType(Enum):
    CRYPTO = "crypto"
    STOCK = "stock"
    FOREX = "forex"
    COMMODITY = "commodity"

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

@dataclass
class TradingSignal:
    symbol: str
    asset_type: AssetType
    signal: SignalType
    confidence: float  # 0-100
    current_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    reasons: List[str]
    timestamp: datetime
    timeframe: str  # 1h, 4h, 1d, etc.

@dataclass
class MarketData:
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    market_cap: Optional[float]
    high_24h: float
    low_24h: float
    timestamp: datetime

class TradingEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # API Keys من environment variables
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.coinbase_key = os.getenv('COINBASE_API_KEY')
        
    async def get_crypto_price(self, symbol: str) -> Optional[MarketData]:
        """جلب سعر العملة المشفرة"""
        
        try:
            # استخدام CoinGecko API (مجاني)
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': self._symbol_to_coingecko_id(symbol),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            coin_id = self._symbol_to_coingecko_id(symbol)
            
            if coin_id not in data:
                return None
            
            coin_data = data[coin_id]
            
            return MarketData(
                symbol=symbol.upper(),
                price=float(coin_data['usd']),
                change_24h=float(coin_data.get('usd_24h_change', 0)),
                change_percent_24h=float(coin_data.get('usd_24h_change', 0)),
                volume_24h=float(coin_data.get('usd_24h_vol', 0)),
                market_cap=float(coin_data.get('usd_market_cap', 0)),
                high_24h=0,  # نحتاج API call إضافي لهذا
                low_24h=0,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching crypto price for {symbol}: {e}")
            return None
    
    async def get_stock_price(self, symbol: str) -> Optional[MarketData]:
        """جلب سعر السهم"""
        
        try:
            # استخدام yfinance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d")
            
            if history.empty:
                return None
            
            current_price = float(history['Close'].iloc[-1])
            
            return MarketData(
                symbol=symbol.upper(),
                price=current_price,
                change_24h=float(info.get('regularMarketChange', 0)),
                change_percent_24h=float(info.get('regularMarketChangePercent', 0)),
                volume_24h=float(info.get('volume', 0)),
                market_cap=float(info.get('marketCap', 0)),
                high_24h=float(info.get('dayHigh', current_price)),
                low_24h=float(info.get('dayLow', current_price)),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None
    
    async def analyze_asset(self, symbol: str, asset_type: AssetType) -> Optional[TradingSignal]:
        """تحليل الأصل وإنتاج إشارة تداول"""
        
        try:
            # جلب البيانات
            if asset_type == AssetType.CRYPTO:
                market_data = await self.get_crypto_price(symbol)
            elif asset_type == AssetType.STOCK:
                market_data = await self.get_stock_price(symbol)
            else:
                return None
            
            if not market_data:
                return None
            
            # تحليل تقني بسيط
            technical_analysis = await self._perform_technical_analysis(symbol, asset_type)
            
            # تحليل المشاعر
            sentiment_analysis = await self._analyze_market_sentiment(symbol)
            
            # دمج التحليلات
            signal, confidence, reasons = self._combine_analyses(
                market_data, technical_analysis, sentiment_analysis
            )
            
            # حساب الأهداف
            target_price, stop_loss = self._calculate_targets(
                market_data.price, signal, confidence
            )
            
            return TradingSignal(
                symbol=symbol.upper(),
                asset_type=asset_type,
                signal=signal,
                confidence=confidence,
                current_price=market_data.price,
                target_price=target_price,
                stop_loss=stop_loss,
                reasons=reasons,
                timestamp=datetime.now(),
                timeframe="4h"
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    async def _perform_technical_analysis(
        self, 
        symbol: str, 
        asset_type: AssetType
    ) -> Dict[str, Any]:
        """تحليل تقني بسيط"""
        
        try:
            if asset_type == AssetType.STOCK:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="30d")
                
                if len(history) < 20:
                    return {"error": "Insufficient data"}
                
                # حساب المتوسطات المتحركة
                sma_20 = history['Close'].rolling(window=20).mean().iloc[-1]
                sma_50 = history['Close'].rolling(window=min(50, len(history))).mean().iloc[-1]
                
                current_price = history['Close'].iloc[-1]
                
                # RSI بسيط
                delta = history['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                return {
                    "sma_20": float(sma_20),
                    "sma_50": float(sma_50),
                    "current_price": float(current_price),
                    "rsi": float(rsi),
                    "trend": "bullish" if current_price > sma_20 > sma_50 else "bearish"
                }
            
            # للعملات المشفرة - تحليل مبسط
            return {
                "trend": "neutral",
                "rsi": 50,
                "volume_trend": "normal"
            }
            
        except Exception as e:
            self.logger.error(f"Technical analysis error: {e}")
            return {"error": str(e)}
    
    async def _analyze_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """تحليل مشاعر السوق"""
        
        try:
            # تحليل بسيط - في الواقع نستخدم APIs متخصصة
            # مثل Fear & Greed Index, social sentiment, news analysis
            
            # محاكاة بيانات المشاعر
            import random
            
            sentiment_score = random.uniform(20, 80)  # 0-100
            
            if sentiment_score > 70:
                sentiment = "very_positive"
            elif sentiment_score > 55:
                sentiment = "positive"
            elif sentiment_score > 45:
                sentiment = "neutral"
            elif sentiment_score > 30:
                sentiment = "negative"
            else:
                sentiment = "very_negative"
            
            return {
                "sentiment": sentiment,
                "score": sentiment_score,
                "social_mentions": random.randint(100, 1000),
                "news_sentiment": sentiment
            }
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "score": 50}
    
    def _combine_analyses(
        self,
        market_data: MarketData,
        technical: Dict[str, Any],
        sentiment: Dict[str, Any]
    ) -> Tuple[SignalType, float, List[str]]:
        """دمج التحليلات لإنتاج إشارة"""
        
        reasons = []
        buy_signals = 0
        sell_signals = 0
        confidence_factors = []
        
        # تحليل السعر والتغيير
        if market_data.change_percent_24h > 5:
            buy_signals += 1
            reasons.append(f"Strong 24h gain: +{market_data.change_percent_24h:.1f}%")
            confidence_factors.append(20)
        elif market_data.change_percent_24h < -5:
            sell_signals += 1
            reasons.append(f"Strong 24h loss: {market_data.change_percent_24h:.1f}%")
            confidence_factors.append(20)
        
        # التحليل التقني
        if technical.get("trend") == "bullish":
            buy_signals += 1
            reasons.append("Technical trend is bullish")
            confidence_factors.append(15)
        elif technical.get("trend") == "bearish":
            sell_signals += 1
            reasons.append("Technical trend is bearish")
            confidence_factors.append(15)
        
        # مؤشر RSI
        rsi = technical.get("rsi", 50)
        if rsi < 30:
            buy_signals += 1
            reasons.append(f"RSI oversold: {rsi:.1f}")
            confidence_factors.append(25)
        elif rsi > 70:
            sell_signals += 1
            reasons.append(f"RSI overbought: {rsi:.1f}")
            confidence_factors.append(25)
        
        # تحليل المشاعر
        sentiment_score = sentiment.get("score", 50)
        if sentiment_score > 70:
            buy_signals += 1
            reasons.append("Very positive market sentiment")
            confidence_factors.append(10)
        elif sentiment_score < 30:
            sell_signals += 1
            reasons.append("Very negative market sentiment")
            confidence_factors.append(10)
        
        # تحديد الإشարة
        if buy_signals > sell_signals + 1:
            if buy_signals >= 3:
                signal = SignalType.STRONG_BUY
            else:
                signal = SignalType.BUY
        elif sell_signals > buy_signals + 1:
            if sell_signals >= 3:
                signal = SignalType.STRONG_SELL
            else:
                signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        # حساب الثقة
        confidence = min(sum(confidence_factors), 95)
        
        if not reasons:
            reasons.append("Mixed signals - recommend holding")
        
        return signal, confidence, reasons
    
    def _calculate_targets(
        self,
        current_price: float,
        signal: SignalType,
        confidence: float
    ) -> Tuple[Optional[float], Optional[float]]:
        """حساب أهداف السعر ووقف الخسارة"""
        
        if signal in [SignalType.BUY, SignalType.STRONG_BUY]:
            # هدف الربح
            target_multiplier = 1.05 + (confidence / 1000)  # 5-15% target
            target_price = current_price * target_multiplier
            
            # وقف الخسارة
            stop_loss_multiplier = 0.97 - (confidence / 2000)  # 2-5% stop loss
            stop_loss = current_price * stop_loss_multiplier
            
            return round(target_price, 4), round(stop_loss, 4)
        
        elif signal in [SignalType.SELL, SignalType.STRONG_SELL]:
            # للبيع على المكشوف
            target_multiplier = 0.95 - (confidence / 1000)
            target_price = current_price * target_multiplier
            
            stop_loss_multiplier = 1.03 + (confidence / 2000)
            stop_loss = current_price * stop_loss_multiplier
            
            return round(target_price, 4), round(stop_loss, 4)
        
        return None, None
    
    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """تحويل رمز العملة إلى CoinGecko ID"""
        
        mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'XLM': 'stellar',
            'DOGE': 'dogecoin'
        }
        
        return mapping.get(symbol.upper(), symbol.lower())
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """نظرة عامة على السوق"""
        
        try:
            # أهم العملات المشفرة
            crypto_symbols = ['BTC', 'ETH', 'BNB', 'ADA']
            crypto_data = []
            
            for symbol in crypto_symbols:
                data = await self.get_crypto_price(symbol)
                if data:
                    crypto_data.append({
                        'symbol': symbol,
                        'price': data.price,
                        'change_24h': data.change_percent_24h
                    })
            
            # أهم الأسهم
            stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
            stock_data = []
            
            for symbol in stock_symbols:
                data = await self.get_stock_price(symbol)
                if data:
                    stock_data.append({
                        'symbol': symbol,
                        'price': data.price,
                        'change_24h': data.change_percent_24h
                    })
            
            return {
                'crypto': crypto_data,
                'stocks': stock_data,
                'market_sentiment': 'neutral',  # يمكن تطويرها
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Market overview error: {e}")
            return {'error': str(e)}
    
    async def get_portfolio_analysis(self, positions: List[Dict]) -> Dict[str, Any]:
        """تحليل المحفظة"""
        
        try:
            total_value = 0
            total_change = 0
            asset_allocation = {}
            
            for position in positions:
                symbol = position['symbol']
                quantity = float(position['quantity'])
                asset_type = AssetType(position['asset_type'])
                
                # جلب السعر الحالي
                if asset_type == AssetType.CRYPTO:
                    market_data = await self.get_crypto_price(symbol)
                else:
                    market_data = await self.get_stock_price(symbol)
                
                if market_data:
                    position_value = quantity * market_data.price
                    position_change = quantity * market_data.price * (market_data.change_percent_24h / 100)
                    
                    total_value += position_value
                    total_change += position_change
                    
                    asset_allocation[asset_type.value] = asset_allocation.get(asset_type.value, 0) + position_value
            
            # حساب التوزيع كنسب مئوية
            allocation_percentages = {}
            for asset_type, value in asset_allocation.items():
                allocation_percentages[asset_type] = (value / total_value * 100) if total_value > 0 else 0
            
            return {
                'total_value': round(total_value, 2),
                'total_change_24h': round(total_change, 2),
                'change_percent_24h': (total_change / total_value * 100) if total_value > 0 else 0,
                'asset_allocation': allocation_percentages,
                'risk_level': self._calculate_portfolio_risk(positions),
                'recommendations': self._get_portfolio_recommendations(allocation_percentages)
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio analysis error: {e}")
            return {'error': str(e)}
    
    def _calculate_portfolio_risk(self, positions: List[Dict]) -> str:
        """حساب مستوى المخاطر"""
        
        crypto_weight = 0
        stock_weight = 0
        total_positions = len(positions)
        
        for position in positions:
            if position['asset_type'] == 'crypto':
                crypto_weight += 1
            else:
                stock_weight += 1
        
        crypto_percentage = (crypto_weight / total_positions * 100) if total_positions > 0 else 0
        
        if crypto_percentage > 70:
            return "high"
        elif crypto_percentage > 40:
            return "medium"
        else:
            return "low"
    
    def _get_portfolio_recommendations(self, allocation: Dict[str, float]) -> List[str]:
        """توصيات تحسين المحفظة"""
        
        recommendations = []
        
        crypto_percentage = allocation.get('crypto', 0)
        stock_percentage = allocation.get('stock', 0)
        
        if crypto_percentage > 80:
            recommendations.append("Consider reducing crypto exposure and diversifying into stocks")
        elif crypto_percentage < 10:
            recommendations.append("Consider adding some crypto exposure for growth potential")
        
        if stock_percentage < 20:
            recommendations.append("Consider increasing stock allocation for stability")
        
        if len(allocation) < 2:
            recommendations.append("Diversify across different asset types")
        
        return recommendations if recommendations else ["Portfolio allocation looks balanced"]

# تصدير الفئة
__all__ = ['TradingEngine', 'TradingSignal', 'MarketData', 'AssetType', 'SignalType']