"""Streamlit main application"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from typing import Dict, Any
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


def create_price_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """Create price chart with technical indicators"""
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["price"],
        mode="lines",
        name="Price",
        line=dict(color="blue", width=2)
    ))
    
    # SMAs if available
    if "sma_10" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["sma_10"],
            mode="lines",
            name="SMA 10",
            line=dict(color="orange", width=1, dash="dash")
        ))
    
    if "sma_20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["sma_20"],
            mode="lines",
            name="SMA 20",
            line=dict(color="red", width=1, dash="dash")
        ))
    
    fig.update_layout(
        title=f"{symbol} - Price Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        height=500
    )
    
    return fig


def create_rsi_chart(df: pd.DataFrame) -> go.Figure:
    """Create RSI chart"""
    if "rsi" not in df.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["rsi"],
        mode="lines",
        name="RSI",
        line=dict(color="purple", width=2)
    ))
    
    # Add overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
    
    fig.update_layout(
        title="RSI Indicator",
        xaxis_title="Date",
        yaxis_title="RSI",
        yaxis_range=[0, 100],
        height=300
    )
    
    return fig


# Main UI
st.title("📈 Asistente de Inversión Inteligente")
st.markdown("Sistema de análisis financiero con IA Generativa y análisis técnico")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    
    # Symbol selection
    symbol = st.selectbox(
        "Seleccionar Activo",
        options=["BTC", "ETH", "SPY", "QQQ", "VTI", "bitcoin", "ethereum"],
        index=0
    )
    
    # Days selection
    days = st.slider("Días de historial", min_value=7, max_value=90, value=30)
    
    # Query input
    query = st.text_area(
        "Consulta",
        value="¿Cuál es el análisis técnico y la recomendación de inversión?",
        height=100
    )
    
    # Analyze button
    analyze_button = st.button("🔍 Analizar", type="primary", use_container_width=True)

# Main content
if analyze_button:
    with st.spinner("Analizando activo..."):
        # Fetch market data
        market_data = fetch_market_data(symbol, days)
        
        # Analyze asset
        analysis_result = analyze_asset(symbol, query)
    
    if "error" not in analysis_result:
        # Display analysis
        st.header("📊 Análisis del Activo")
        
        # Market data metrics
        if market_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Precio Actual", f"${market_data.get('price', 0):.2f}")
            
            with col2:
                rsi = market_data.get("rsi", 0)
                rsi_color = "normal" if 30 <= rsi <= 70 else "inverse"
                st.metric("RSI", f"{rsi:.2f}", delta=None)
            
            with col3:
                st.metric("SMA 10", f"${market_data.get('sma_10', 0):.2f}")
            
            with col4:
                st.metric("Volatilidad", f"{market_data.get('volatility', 0):.2%}")
        
        # Model prediction
        if analysis_result.get("model_prediction"):
            prediction = analysis_result["model_prediction"]
            strategy = prediction.get("strategy", "UNKNOWN")
            confidence = prediction.get("confidence", 0)
            
            st.subheader("🤖 Predicción del Modelo")
            col1, col2 = st.columns(2)
            
            with col1:
                strategy_color = "🟢" if strategy == "TOP" else "🔴"
                st.markdown(f"**Estrategia:** {strategy_color} {strategy}")
            
            with col2:
                st.markdown(f"**Confianza:** {confidence:.2%}")
        
        # AI Analysis
        st.subheader("💡 Análisis con IA")
        st.markdown(analysis_result.get("analysis", "No hay análisis disponible"))
        
        # Charts (if we have dataframe data)
        # Note: In a real implementation, you'd fetch the full dataframe from the API
        st.subheader("📈 Gráficos")
        st.info("Los gráficos detallados se mostrarían aquí con datos históricos completos")
        
    else:
        st.error(f"Error: {analysis_result.get('error', 'Error desconocido')}")

else:
    # Welcome message
    st.info("👈 Selecciona un activo y configura los parámetros en la barra lateral, luego haz clic en 'Analizar'")
    
    # Example usage
    st.header("Cómo usar")
    st.markdown("""
    1. **Selecciona un activo** de la lista desplegable
    2. **Configura el horizonte temporal** (días de historial)
    3. **Escribe tu consulta** o usa la predeterminada
    4. **Haz clic en 'Analizar'** para obtener:
       - Análisis técnico con indicadores (RSI, SMAs, volatilidad)
       - Predicción del modelo ML (TOP/BOTTOM)
       - Análisis semántico con IA Generativa
       - Recomendaciones de inversión fundamentadas
    """)
    
    st.header("Activos Soportados")
    st.markdown("""
    - **Criptomonedas**: Bitcoin (BTC), Ethereum (ETH)
    - **ETFs**: SPY, QQQ, VTI
    """)

