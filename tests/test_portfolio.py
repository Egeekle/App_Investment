
import pytest
import os
import json
from src.portfolio.portfolio_manager import PortfolioManager

@pytest.fixture
def portfolio_file(tmp_path):
    f = tmp_path / "test_portfolio.json"
    return str(f)

def test_add_asset(portfolio_file):
    pm = PortfolioManager(storage_path=portfolio_file)
    pm.add_asset("BTC", 1.0, 50000.0)
    
    summary = pm.get_portfolio_summary()
    assert len(summary["assets"]) == 1
    assert summary["assets"][0]["symbol"] == "BTC"
    assert summary["assets"][0]["quantity"] == 1.0

def test_add_existing_asset_updates_avg_price(portfolio_file):
    pm = PortfolioManager(storage_path=portfolio_file)
    pm.add_asset("BTC", 1.0, 50000.0)
    pm.add_asset("BTC", 1.0, 60000.0)
    
    summary = pm.get_portfolio_summary()
    asset = summary["assets"][0]
    assert asset["quantity"] == 2.0
    assert asset["purchase_price"] == 55000.0

def test_remove_asset(portfolio_file):
    pm = PortfolioManager(storage_path=portfolio_file)
    pm.add_asset("ETH", 10.0, 2000.0)
    pm.remove_asset("ETH", 4.0)
    
    summary = pm.get_portfolio_summary()
    assert summary["assets"][0]["quantity"] == 6.0

def test_remove_more_than_owned_raises_error(portfolio_file):
    pm = PortfolioManager(storage_path=portfolio_file)
    pm.add_asset("ETH", 1.0, 2000.0)
    with pytest.raises(ValueError):
        pm.remove_asset("ETH", 2.0)
