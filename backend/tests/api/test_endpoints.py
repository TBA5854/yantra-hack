"""
Test FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


class TestRiskEndpoints:
    """Test risk-related endpoints."""
    
    def test_get_current_risk(self):
        """Test /risk/current endpoint."""
        response = client.get("/risk/current?coin=USDC&chain=ethereum")
        
        # May return 503 if models not loaded, or 200 with data
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert 'risk_score' in data
            assert 'tcs' in data
            assert 'coin' in data
    
    def test_get_risk_history(self):
        """Test /risk/history endpoint."""
        response = client.get(
            "/risk/history",
            params={
                "coin": "USDC",
                "from_": "2026-02-14T00:00:00Z",
                "to": "2026-02-14T12:00:00Z",
                "interval": "5m"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'snapshots' in data
        assert data['coin'] == 'USDC'


class TestAlertEndpoints:
    """Test alert endpoints."""
    
    def test_get_alerts(self):
        """Test /alerts endpoint."""
        response = client.get("/alerts")
        
        assert response.status_code == 200
        data = response.json()
        assert 'alerts' in data
        assert 'total' in data
    
    def test_get_alert_detail(self):
        """Test /alerts/{id} endpoint."""
        response = client.get("/alerts/test-id")
        
        # Should return 404 for non-existent alert
        assert response.status_code == 404


class TestConfigEndpoints:
    """Test configuration endpoints."""
    
    def test_get_coins(self):
        """Test /config/coins endpoint."""
        response = client.get("/config/coins")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]['ticker'] in ['USDC', 'USDT', 'DAI', 'BUSD']
    
    def test_get_chains(self):
        """Test /config/chains endpoint."""
        response = client.get("/config/chains")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]['name'] in ['ethereum', 'polygon', 'avalanche']


class TestHealthEndpoint:
    """Test health check."""
    
    def test_health(self):
        """Test /health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'ml_available' in data
