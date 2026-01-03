"""FastAPI main application"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

from src.models.investment_agent import InvestmentAgent
from src.models.agent_tools import AgentTools
from src.data_ingestion.coingecko_client import CoinGeckoClient
from src.data_ingestion.alpha_vantage_client import AlphaVantageClient
from src.rag.vector_store import VectorStore
from src.models.random_forest_model import RandomForestStrategyModel
from src.rag.knowledge_base import initialize_knowledge_base
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global variables for services
agent: Optional[InvestmentAgent] = None
vector_store: Optional[VectorStore] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global agent, vector_store
    
    # Startup
    logger.info("Starting up services...")
    
    try:
        # Initialize Google AI (Gemini) LLM
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_AI_MODEL", "gemini-pro"),
            google_api_key=os.getenv("GOOGLE_AI_API_KEY"),
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Initialize data clients
        coingecko_client = CoinGeckoClient()
        alpha_vantage_client = AlphaVantageClient(
            api_key=os.getenv("ALPHA_VANTAGE_API_KEY", "")
        )
        
        # Initialize vector store
        vector_store = VectorStore(
            chroma_db_path=os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        )
        initialize_knowledge_base(vector_store)
        
        # Initialize ML model
        rf_model = RandomForestStrategyModel()
        model_path = os.getenv("MODEL_PATH", "./models/random_forest_model.pkl")
        if os.path.exists(model_path):
            rf_model.load(model_path)
        else:
            logger.warning(f"Model not found at {model_path}. Using untrained model.")
        
        # Initialize tools
        tools = AgentTools(
            coingecko_client=coingecko_client,
            alpha_vantage_client=alpha_vantage_client,
            vector_store=vector_store,
            rf_model=rf_model
        )
        
        # Initialize agent
        agent = InvestmentAgent(llm=llm, tools=tools)
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down services...")


# Create FastAPI app
app = FastAPI(
    title="Investment Assistant API",
    description="API for intelligent investment analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AnalyzeRequest(BaseModel):
    symbol: str
    query: str
    days: Optional[int] = 30


class AnalyzeResponse(BaseModel):
    symbol: str
    query: str
    analysis: str
    market_data: Optional[Dict[str, Any]] = None
    model_prediction: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PriceResponse(BaseModel):
    symbol: str
    price: float
    rsi: Optional[float] = None
    sma_10: Optional[float] = None
    sma_20: Optional[float] = None
    volatility: Optional[float] = None


# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Investment Assistant API",
        "version": "1.0.0"
    }


@app.post("/v1/chat/analyze", response_model=AnalyzeResponse)
async def analyze_asset(request: AnalyzeRequest):
    """
    Analyze an asset and provide investment recommendation
    
    Args:
        request: AnalyzeRequest with symbol and query
    
    Returns:
        AnalyzeResponse with analysis results
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = agent.analyze(symbol=request.symbol, query=request.query)
        
        return AnalyzeResponse(
            symbol=result.get("symbol", request.symbol),
            query=result.get("query", request.query),
            analysis=result.get("analysis", ""),
            market_data=result.get("market_data"),
            model_prediction=result.get("model_prediction"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/market/price/{symbol}", response_model=PriceResponse)
async def get_market_price(symbol: str, days: int = 30):
    """
    Get market price and technical indicators for a symbol
    
    Args:
        symbol: Asset symbol
        days: Number of days of historical data
    
    Returns:
        PriceResponse with price and indicators
    """
    if agent is None or agent.tools is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        market_data = agent.tools.get_market_data(symbol=symbol, days=days)
        
        if "error" in market_data:
            raise HTTPException(status_code=404, detail=market_data["error"])
        
        return PriceResponse(
            symbol=market_data.get("symbol", symbol),
            price=market_data.get("latest_price", 0),
            rsi=market_data.get("rsi"),
            sma_10=market_data.get("sma_10"),
            sma_20=market_data.get("sma_20"),
            volatility=market_data.get("volatility")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in price endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

