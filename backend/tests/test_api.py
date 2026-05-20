import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_consult_basic():
    request = {
        "user_input": "Дом из газобетона, 2 этажа",
        "city": "Москва"
    }
    response = client.post("/consult", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "foundation_type" in data
    assert "cost_estimate" in data
    assert "weather_recommendation" in data
    assert "stores" in data
    assert "answer" in data
    assert "sources" in data

def test_consult_with_address():
    request = {
        "user_input": "Дом из кирпича, 1 этаж",
        "city": "Сургут",
        "address": "ул. Тверская 15"
    }
    response = client.post("/consult", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["foundation_type"] is not None

def test_consult_with_month():
    request = {
        "user_input": "каркасный дом, 2 этажа",
        "city": "Краснодар",
        "desired_month": "январь"
    }
    response = client.post("/consult", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "weather_recommendation" in data

def test_consult_with_self_build():
    request = {
        "user_input": "дом из бруса, 1 этаж",
        "city": "Москва",
        "self_build": True
    }
    response = client.post("/consult", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["cost_estimate"].get("self_build") == True or data["cost_estimate"]["work"] == 0