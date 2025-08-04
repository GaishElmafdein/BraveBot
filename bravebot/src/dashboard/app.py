import streamlit as st
import sys
from pathlib import Path

# Add project root path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

st.set_page_config(
    page_title="BraveBot Dashboard",
    page_icon="BraveBot",
    layout="wide"
)

st.title("BraveBot AI Commerce Empire")
st.markdown("---")

# Trend Analysis
st.header("📈 Trend Analysis")

col1, col2 = st.columns(2)

with col1:
    keyword = st.text_input("🔍 Search Keyword", value="gaming chair")
    if st.button("🔎 Analyze"):
        try:
            from ai.trends_engine import fetch_viral_trends
            
            with st.spinner("Analyzing..."):
                result = fetch_viral_trends(keyword, 5)
            
            st.success("✅ Analysis completed successfully!")
            
            # Display results
            for trend in result.get('top_keywords', []):
                st.metric(
                    f"🎯 Target: {trend['keyword']}", 
                    f"{trend['viral_score']}%",
                    f"Source: {trend.get('source', 'AI Analysis')}"
                )
                
        except Exception as e:
            st.error(f"❌ Error: {e}")

with col2:
    st.subheader("💵 Smart Pricing")
    
    base_price = st.number_input("💵 Base Price", value=29.99, min_value=0.01)
    viral_score = st.slider("📊 Viral Score", 0, 100, 75)
    
    if st.button("💡 Suggest Price"):
        try:
            from ai.trends_engine import dynamic_pricing_suggestion
            
            pricing = dynamic_pricing_suggestion(base_price, viral_score)
            
            st.success(f"💰 Suggested Price: ${pricing['suggested_price']:.2f}")
            st.info(f"📈 Profit Margin: {pricing['profit_margin']:.1f}%")
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# System Information
st.markdown("---")
st.subheader("ℹ️ System Information")

try:
    from core.ai_engine.ai_engine import get_engine_status
    status = get_engine_status()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🧠 AI Engine", "Active" if status['status'] == 'active' else "Inactive")
    
    with col2:
        st.metric("⚡ Version", "v2.0")
    
    with col3:
        st.metric("🔍 Status", "Ready")
        
except Exception as e:
    st.error(f"❌ Error in system status: {e}")