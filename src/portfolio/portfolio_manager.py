"""
Portfolio Management Module
"""
import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Manages user investment portfolio with simple JSON persistence"""
    
    def __init__(self, storage_path: str = "./data/portfolio.json"):
        self.storage_path = storage_path
        self.portfolio = self._load_portfolio()
        
    def _load_portfolio(self) -> Dict[str, Any]:
        """Load portfolio from JSON file"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading portfolio: {e}")
                return {"assets": [], "history": []}
        return {"assets": [], "history": []}
        
    def _save_portfolio(self):
        """Save portfolio to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
            
    def add_asset(self, symbol: str, quantity: float, purchase_price: float) -> Dict[str, Any]:
        """Add an asset to the portfolio"""
        asset = {
            "symbol": symbol.upper(),
            "quantity": quantity,
            "purchase_price": purchase_price,
            "added_at": datetime.now().isoformat()
        }
        
        # Check if asset already exists, if so update quantity (avg price calculation omitted for simplicity, just adding new entry or simple append?)
        # For simplicity, we'll just append a new lot. Or maybe aggregate?
        # Let's aggregate by symbol for simpler display
        
        existing = next((a for a in self.portfolio["assets"] if a["symbol"] == symbol.upper()), None)
        if existing:
            # Weighted average price
            total_cost = (existing["quantity"] * existing["purchase_price"]) + (quantity * purchase_price)
            new_quantity = existing["quantity"] + quantity
            existing["purchase_price"] = total_cost / new_quantity
            existing["quantity"] = new_quantity
            existing["updated_at"] = datetime.now().isoformat()
        else:
            self.portfolio["assets"].append(asset)
            
        self._save_portfolio()
        logger.info(f"Added {quantity} of {symbol} to portfolio")
        return self.get_portfolio_summary()

    def remove_asset(self, symbol: str, quantity: float) -> Dict[str, Any]:
        """Remove (sell) an asset"""
        symbol = symbol.upper()
        existing = next((a for a in self.portfolio["assets"] if a["symbol"] == symbol), None)
        
        if not existing:
            raise ValueError(f"Asset {symbol} not found in portfolio")
            
        if existing["quantity"] < quantity:
            raise ValueError(f"Insufficient quantity of {symbol}. You have {existing['quantity']}")
            
        existing["quantity"] -= quantity
        if existing["quantity"] <= 0:
            self.portfolio["assets"].remove(existing)
            
        self._save_portfolio()
        logger.info(f"Removed {quantity} of {symbol} from portfolio")
        return self.get_portfolio_summary()
        
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary"""
        return self.portfolio
        
    def get_holdings(self) -> List[Dict[str, Any]]:
        """Get list of assets"""
        return self.portfolio["assets"]
        
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value given current prices
        current_prices: dict mapping symbol -> price
        """
        total = 0.0
        for asset in self.portfolio["assets"]:
            price = current_prices.get(asset["symbol"], asset["purchase_price"]) # Fallback to purchase price if current not found
            total += asset["quantity"] * price
        return total
