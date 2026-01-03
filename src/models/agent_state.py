"""Agent state definition for LangGraph"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State maintained throughout the agent execution"""
    messages: List[BaseMessage]
    user_query: str
    symbol: str
    market_data: Optional[Dict[str, Any]]
    news_data: Optional[List[Dict[str, Any]]]
    model_prediction: Optional[Dict[str, Any]]
    rag_context: Optional[List[Dict[str, Any]]]
    final_response: Optional[str]

