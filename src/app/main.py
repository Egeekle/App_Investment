"""Streamlit main application"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Asistente de Inversión Inteligente",
    page_icon="📈",
    layout="wide"
)

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def fetch_market_data(symbol: str, days: int = 30) -> Dict[str, Any]:
    """Fetch market data from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/v1/market/price/{symbol}",
            params={"days": days},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return {}


def analyze_asset(symbol: str, query: str) -> Dict[str, Any]:
    """Analyze asset using API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/analyze",
            json={"symbol": symbol, "query": query},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error analyzing asset: {e}")
        return {"error": str(e)}

def fetch_portfolio() -> Dict[str, Any]:
    try:
        response = requests.get(f"{API_BASE_URL}/v1/portfolio", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def add_asset_to_portfolio(symbol: str, quantity: float, price: float):
    try:
        requests.post(
            f"{API_BASE_URL}/v1/portfolio/add", 
            json={"symbol": symbol, "quantity": quantity, "purchase_price": price},
            timeout=10
        )
        st.success(f"Added {quantity} {symbol} to portfolio.")
    except Exception as e:
        st.error(f"Error adding asset: {e}")

def get_drift_report() -> Dict[str, Any]:
    try:
        response = requests.get(f"{API_BASE_URL}/v1/drift", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def refresh_news():
    try:
        requests.post(f"{API_BASE_URL}/v1/news/fetch", timeout=30)
        st.success("News refreshed successfully!")
    except Exception as e:
        st.error(f"Error refreshing news: {e}")

# Main UI
st.title("📈 Asistente de Inversión Inteligente")
st.markdown("Sistema de análisis financiero con IA Generativa, gestión de portafolio y monitoreo.")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Análisis & Chat", "💼 Portafolio", "🛡️ Monitoreo Drift"])

with tab1:
    # Sidebar for Analysis
    with st.expander("Configuración de Análisis", expanded=True):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            symbol = st.selectbox(
                "Seleccionar Activo",
                options=["BTC", "ETH", "SPY", "QQQ", "VTI", "bitcoin", "ethereum"],
                index=0
            )
        with col_s2:
            days = st.slider("Días de historial", min_value=7, max_value=90, value=30)
        with col_s3:
            if st.button("🔄 Actualizar Noticias"):
                with st.spinner("Descargando noticias..."):
                    refresh_news()
    
    query = st.text_area(
        "Consulta al Asistente",
        value="¿Cuál es el análisis técnico y la recomendación de inversión? Ten en cuenta mi portafolio si aplica.",
        height=100
    )
    
    if st.button("🔍 Analizar", type="primary"):
        with st.spinner("Analizando activo..."):
            market_data = fetch_market_data(symbol, days)
            analysis_result = analyze_asset(symbol, query)
        
        if "error" not in analysis_result:
            st.header("📊 Resultado del Análisis")
            
            # Market Metrics
            if market_data:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Precio Actual", f"${market_data.get('price', 0):.2f}")
                rsi = market_data.get("rsi", 0)
                col2.metric("RSI", f"{rsi:.2f}")
                col3.metric("SMA 10", f"${market_data.get('sma_10', 0):.2f}")
                col4.metric("Volatilidad", f"{market_data.get('volatility', 0):.2%}")
            
            # Prediction
            if analysis_result.get("model_prediction"):
                pred = analysis_result["model_prediction"]
                st.subheader("🤖 Predicción ML")
                st.info(f"Estrategia: **{pred.get('strategy', 'UNKNOWN')}** | Confianza: **{pred.get('confidence', 0):.2%}**")
            
            # AI Analysis
            st.subheader("💡 Respuesta del Agente")
            st.markdown(analysis_result.get("analysis", "No hay análisis disponible"))
            
        else:
            st.error(f"Error: {analysis_result.get('error')}")

with tab2:
    st.header("Gestión de Portafolio")
    
    # Add Asset Form
    with st.form("add_asset_form"):
        c1, c2, c3 = st.columns(3)
        new_symbol = c1.text_input("Símbolo (e.g., BTC)")
        new_qty = c2.number_input("Cantidad", min_value=0.01, step=0.01)
        new_price = c3.number_input("Precio de Compra", min_value=0.1, step=0.1)
        submitted = st.form_submit_button("Añadir Activo")
        if submitted and new_symbol:
            add_asset_to_portfolio(new_symbol, new_qty, new_price)
            st.rerun()

    # View Portfolio
    portfolio = fetch_portfolio()
    if "assets" in portfolio and portfolio["assets"]:
        df_port = pd.DataFrame(portfolio["assets"])
        st.dataframe(df_port, use_container_width=True)
        
        # Simple Pie Chart
        if not df_port.empty:
            fig = px.pie(df_port, values='quantity', names='symbol', title='Distribución de Activos (por cantidad)')
            st.plotly_chart(fig)
    else:
        st.info("El portafolio está vacío. Añade activos arriba.")

with tab3:
    st.header("🛡️ Monitoreo de Data Drift")
    if st.button("Chequear Drift Ahora"):
        report = get_drift_report()
        st.json(report)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Predicciones del Modelo")
            p_drift = report.get("prediction_drift", {})
            if p_drift.get("drift_detected"):
                st.error("⚠️ Drift Detectado en Predicciones!")
            else:
                st.success("✅ Predicciones Estables")
            st.write(p_drift)
            
        with col2:
            st.subheader("Acciones del Agente")
            a_drift = report.get("action_drift", {})
            if a_drift.get("drift_detected"):
                st.warning("⚠️ Drift Detectado en Acciones!")
            else:
                st.success("✅ Acciones Estables")
            st.write(a_drift)

