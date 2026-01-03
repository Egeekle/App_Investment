"""Financial knowledge base initialization"""

from typing import List, Dict
from src.rag.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)


# Financial knowledge base content
FINANCIAL_KNOWLEDGE = [
    {
        "content": """
        Estrategia TOP (Técnica de Oportunidad de Precio):
        Esta estrategia identifica activos que están en una posición favorable para compra.
        Indicadores clave:
        - RSI por debajo de 30 (sobreventa)
        - Precio por debajo de la media móvil de 20 días
        - Volatilidad alta pero con tendencia alcista
        - Sentimiento de mercado negativo pero con fundamentos sólidos
        """,
        "metadata": {"type": "strategy", "name": "TOP", "category": "buy_signal"}
    },
    {
        "content": """
        Estrategia BOTTOM (Técnica de Oportunidad de Precio):
        Esta estrategia identifica activos que están en una posición favorable para venta.
        Indicadores clave:
        - RSI por encima de 70 (sobrecompra)
        - Precio por encima de la media móvil de 20 días
        - Volatilidad alta pero con tendencia bajista
        - Sentimiento de mercado positivo pero con sobrevaluación
        """,
        "metadata": {"type": "strategy", "name": "BOTTOM", "category": "sell_signal"}
    },
    {
        "content": """
        RSI (Relative Strength Index):
        El RSI es un indicador técnico que mide la velocidad y magnitud de los cambios de precio.
        - RSI < 30: Indica sobreventa, posible señal de compra
        - RSI > 70: Indica sobrecompra, posible señal de venta
        - RSI entre 30-70: Rango neutral
        """,
        "metadata": {"type": "indicator", "name": "RSI", "category": "technical_analysis"}
    },
    {
        "content": """
        Medias Móviles (SMA):
        Las medias móviles suavizan los datos de precio para identificar tendencias.
        - Cuando el precio cruza por encima de la SMA: Señal alcista
        - Cuando el precio cruza por debajo de la SMA: Señal bajista
        - SMA corta (10 días) vs SMA larga (20 días): Golden Cross (alcista) o Death Cross (bajista)
        """,
        "metadata": {"type": "indicator", "name": "SMA", "category": "technical_analysis"}
    },
    {
        "content": """
        Análisis de Sentimiento:
        El análisis de sentimiento combina noticias y datos cualitativos con análisis técnico.
        - Sentimiento negativo + Indicadores técnicos favorables: Oportunidad de compra
        - Sentimiento positivo + Indicadores técnicos desfavorables: Señal de venta
        - El sentimiento puede preceder movimientos de precio
        """,
        "metadata": {"type": "concept", "name": "sentiment_analysis", "category": "analysis"}
    },
    {
        "content": """
        Volatilidad:
        La volatilidad mide la variabilidad de los precios.
        - Alta volatilidad: Mayor riesgo pero también mayor oportunidad
        - Baja volatilidad: Mercado estable pero con menos oportunidades
        - La volatilidad anualizada se calcula usando la desviación estándar de retornos
        """,
        "metadata": {"type": "concept", "name": "volatility", "category": "risk_management"}
    }
]


def initialize_knowledge_base(vector_store: VectorStore):
    """
    Initialize the financial knowledge base with default content
    
    Args:
        vector_store: VectorStore instance
    """
    try:
        # Check if collection is empty
        count = vector_store.collection.count()
        
        if count == 0:
            texts = [item["content"] for item in FINANCIAL_KNOWLEDGE]
            metadatas = [item["metadata"] for item in FINANCIAL_KNOWLEDGE]
            ids = [f"doc_{i}" for i in range(len(texts))]
            
            vector_store.add_documents(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info("Initialized knowledge base with default content")
        else:
            logger.info(f"Knowledge base already contains {count} documents")
            
    except Exception as e:
        logger.error(f"Error initializing knowledge base: {e}")
        raise


def add_news_to_knowledge_base(
    vector_store: VectorStore,
    news_items: List[Dict]
):
    """
    Add news items to the knowledge base
    
    Args:
        vector_store: VectorStore instance
        news_items: List of news dicts with 'content', 'symbol', 'date', 'sentiment'
    """
    try:
        texts = []
        metadatas = []
        ids = []
        
        for i, news in enumerate(news_items):
            texts.append(news.get("content", ""))
            metadatas.append({
                "type": "news",
                "symbol": news.get("symbol", ""),
                "date": news.get("date", ""),
                "sentiment": news.get("sentiment", "neutral")
            })
            ids.append(f"news_{news.get('symbol', 'unknown')}_{i}")
        
        vector_store.add_documents(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(news_items)} news items to knowledge base")
        
    except Exception as e:
        logger.error(f"Error adding news to knowledge base: {e}")
        raise

