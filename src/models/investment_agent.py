"""LangGraph agent for investment analysis"""

from typing import Literal, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from src.models.agent_state import AgentState
from src.models.agent_tools import AgentTools
import logging
import json

logger = logging.getLogger(__name__)


class InvestmentAgent:
    """LangGraph agent for intelligent investment analysis"""
    
    def __init__(
        self,
        llm: ChatGoogleGenerativeAI,
        tools: AgentTools
    ):
        self.llm = llm
        self.tools = tools
        self.tools_list = self._create_tools()
        self.llm_with_tools = llm.bind_tools(self.tools_list)
        self.graph = self._build_graph()
    
    def _create_tools(self):
        """Create LangChain tools from AgentTools"""
        tools_instance = self.tools  # Capture reference
        
        @tool
        def get_market_data(symbol: str, days: int = 30) -> dict:
            """Get market data and technical indicators for a symbol. Returns price, RSI, SMAs, volatility."""
            return tools_instance.get_market_data(symbol, days)
        
        @tool
        def get_news_sentiment(symbol: str, query: str = "") -> list:
            """Get relevant news and sentiment analysis for a symbol from knowledge base."""
            return tools_instance.get_news_sentiment(symbol, query)
        
        @tool
        def predict_strategy(market_data: dict) -> dict:
            """Predict investment strategy (TOP for buy, BOTTOM for sell) using ML model. Requires market_data dict."""
            return tools_instance.predict_strategy(market_data)

        @tool
        def get_portfolio() -> dict:
            """Get the current user portfolio holdings."""
            return tools_instance.get_portfolio()
            
        @tool
        def add_to_portfolio(symbol: str, quantity: float, price: float) -> dict:
            """Add an asset to the portfolio. Requires symbol, quantity, and purchase price."""
            return tools_instance.add_to_portfolio(symbol, quantity, price)
            
        @tool
        def remove_from_portfolio(symbol: str, quantity: float) -> dict:
            """Remove an asset from the portfolio. Requires symbol and quantity."""
            return tools_instance.remove_from_portfolio(symbol, quantity)
            
        @tool
        def fetch_latest_news(category: str = "general") -> str:
            """Fetch latest news and add to knowledge base. Category can be 'general' or 'crypto'."""
            return tools_instance.fetch_latest_news(category)
        
        return [get_market_data, get_news_sentiment, predict_strategy, get_portfolio, add_to_portfolio, remove_from_portfolio, fetch_latest_news]
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph"""
        
        # Create tool node
        tool_node = ToolNode(self.tools_list)
        
        # Build graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("tools", tool_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add edges
        workflow.add_conditional_edges(
            "supervisor",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", "supervisor")
        
        return workflow.compile()
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor node that decides what to do next"""
        try:
            messages = state.get("messages", [])
            
            # Build system prompt
            system_prompt = """You are an intelligent investment assistant that analyzes financial assets.

Your capabilities:
1. get_market_data: Get market data and technical indicators (RSI, SMAs, volatility) for a symbol
2. get_news_sentiment: Search for relevant news and sentiment analysis from knowledge base
3. predict_strategy: Predict investment strategies (TOP for buy, BOTTOM for sell) using ML model
4. get_portfolio: Check current portfolio holdings
5. add_to_portfolio / remove_from_portfolio: Manage portfolio assets
6. fetch_latest_news: Refresh news database with latest market news

When a user asks about an asset:
1. First, call get_market_data to understand current technical indicators
2. If needed, check get_portfolio to see if user owns it
3. Call get_news_sentiment to get relevant context
4. Use predict_strategy with the market_data to get ML prediction
5. Synthesize all information into a comprehensive analysis

Provide clear, actionable insights combining technical analysis with market sentiment.
Always use the tools to gather data before providing analysis."""
            
            # Prepare messages for LLM (add system message if not present)
            llm_messages = messages
            if not any(isinstance(m, SystemMessage) for m in messages):
                llm_messages = [SystemMessage(content=system_prompt)] + messages
            
            # Get response from LLM with tools
            response = self.llm_with_tools.invoke(llm_messages)
            
            # Update state with market_data and predictions if present in tool calls
            if hasattr(response, "tool_calls") and response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call["name"] == "get_market_data":
                        # Store market data in state
                        state["market_data"] = None  # Will be updated by tool execution
                    elif tool_call["name"] == "predict_strategy":
                        state["model_prediction"] = None  # Will be updated by tool execution
            
            # Update state
            state["messages"] = messages + [response]
            
            return state
            
        except Exception as e:
            logger.error(f"Error in supervisor node: {e}")
            error_message = AIMessage(content=f"Error: {str(e)}")
            state["messages"] = state.get("messages", []) + [error_message]
            return state
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Decide whether to continue or end"""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        # Check if we have tool calls - continue to execute tools
        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        # Check if we have enough iterations (prevent infinite loops)
        ai_messages = [m for m in messages if isinstance(m, AIMessage)]
        if len(ai_messages) > 10:  # Max 10 AI responses
            return "end"
        
        # End if we have a final response without tool calls
        if last_message and isinstance(last_message, AIMessage):
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return "end"
        
        # Default: end if no tool calls
        return "end"
    
    def analyze(self, symbol: str, query: str) -> dict:
        """
        Analyze an asset and provide investment recommendation
        
        Args:
            symbol: Asset symbol
            query: User query about the asset
        
        Returns:
            Dictionary with analysis results
        """
        try:
            # Initialize state
            initial_state: AgentState = {
                "messages": [HumanMessage(content=f"Analyze {symbol}. {query}")],
                "user_query": query,
                "symbol": symbol,
                "market_data": None,
                "news_data": None,
                "model_prediction": None,
                "rag_context": None,
                "final_response": None
            }
            
            # Run graph
            final_state = self.graph.invoke(initial_state)
            
            # Extract final response and tool results
            messages = final_state.get("messages", [])
            final_response = ""
            market_data = None
            model_prediction = None
            rag_context = None
            
            # Extract data from tool messages
            for msg in messages:
                if isinstance(msg, ToolMessage):
                    try:
                        result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                        if isinstance(result, dict):
                            if "rsi" in result or "latest_price" in result:
                                market_data = result
                            elif "strategy" in result:
                                model_prediction = result
                            elif isinstance(result, list) and len(result) > 0:
                                rag_context = result
                    except:
                        pass
            
            # Get final AI response
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.content:
                    if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                        final_response = msg.content
                        break
            
            # If no final response, construct one from available data
            if not final_response:
                final_response = "Analysis completed. Check market_data and model_prediction for details."
            
            return {
                "symbol": symbol,
                "query": query,
                "analysis": final_response,
                "market_data": market_data or final_state.get("market_data"),
                "model_prediction": model_prediction or final_state.get("model_prediction"),
                "rag_context": rag_context or final_state.get("rag_context")
            }
            
        except Exception as e:
            logger.error(f"Error in agent analysis: {e}")
            return {
                "symbol": symbol,
                "query": query,
                "error": str(e),
                "analysis": f"Error analyzing {symbol}: {str(e)}"
            }

