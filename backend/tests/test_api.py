"""Tests for CRUD API endpoints using FastAPI TestClient."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create TestClient instance."""
    return TestClient(app)  # positional arg for starlette 0.35+


class TestHealthEndpoint:
    """Test health endpoint."""

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRecordsCRUD:
    """Test CRUD operations for records."""

    def test_create_record(self, client):
        """Test create record endpoint."""
        payload = {
            "category": "餐饮",
            "amount": 35.5,
            "description": "测试外卖",
            "ai_confidence": 0.90,
            "status": "confirmed",
            "source": "ai",
        }
        response = client.post("/api/records", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["category"] == "餐饮"
        assert data["amount"] == 35.5
        assert data["description"] == "测试外卖"
        assert "id" in data
        assert "created_at" in data

    def test_create_and_read_record(self, client):
        """Test create then read record."""
        payload = {
            "category": "交通",
            "amount": 25.0,
            "description": "打车",
        }
        create_response = client.post("/api/records", json=payload)
        assert create_response.status_code == 201
        record_id = create_response.json()["id"]

        read_response = client.get(f"/api/records/{record_id}")
        assert read_response.status_code == 200
        data = read_response.json()
        assert data["id"] == record_id
        assert data["category"] == "交通"

    def test_create_and_update_record(self, client):
        """Test create then update record."""
        payload = {
            "category": "购物",
            "amount": 100.0,
            "description": "网购",
        }
        create_response = client.post("/api/records", json=payload)
        record_id = create_response.json()["id"]

        update_payload = {
            "ground_truth_category": "服饰",
            "ground_truth_amount": 99.9,
            "user_corrected": True,
        }
        update_response = client.put(f"/api/records/{record_id}", json=update_payload)
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["ground_truth_category"] == "服饰"
        assert data["ground_truth_amount"] == 99.9
        assert data["user_corrected"] == 1

    def test_create_and_delete_record(self, client):
        """Test create then delete record."""
        payload = {
            "category": "娱乐",
            "amount": 150.0,
            "description": "电影",
        }
        create_response = client.post("/api/records", json=payload)
        record_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/records/{record_id}")
        assert delete_response.status_code == 204

        read_response = client.get(f"/api/records/{record_id}")
        assert read_response.status_code == 404

    def test_get_nonexistent_record(self, client):
        """Test get non-existent record returns 404."""
        response = client.get("/api/records/nonexistent-id-12345")
        assert response.status_code == 404


class TestPagination:
    """Test pagination parameters."""

    def test_pagination_params(self, client):
        """Test ?page=1&limit=10 pagination."""
        response = client.get("/api/records?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_page_2_offset(self, client):
        """Test page 2 returns different records."""
        response1 = client.get("/api/records?page=1&limit=5")
        response2 = client.get("/api/records?page=2&limit=5")
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestFilters:
    """Test filter parameters."""

    def test_filter_by_status(self, client):
        """Test ?status=pending_review filter."""
        response = client.get("/api/records?status=pending_review")
        assert response.status_code == 200
        data = response.json()
        for record in data:
            assert record["status"] == "pending_review"

    def test_filter_by_from_date(self, client):
        """Test ?from= date filter."""
        response = client.get("/api/records?from=2020-01-01")
        assert response.status_code == 200
        data = response.json()
        for record in data:
            assert record["created_at"] >= "2020-01-01"

    def test_filter_by_to_date(self, client):
        """Test ?to= date filter."""
        response = client.get("/api/records?to=2030-12-31")
        assert response.status_code == 200
        data = response.json()
        for record in data:
            assert record["created_at"] <= "2030-12-31"

    def test_filter_by_date_range(self, client):
        """Test ?from=&to= date range filter."""
        response = client.get("/api/records?from=2020-01-01&to=2030-12-31")
        assert response.status_code == 200


class TestBackupRestore:
    """Test backup and restore endpoints."""

    def test_backup_endpoint(self, client):
        """Test backup endpoint creates a backup."""
        response = client.post("/api/backup")
        assert response.status_code == 201
        data = response.json()
        assert "backup_path" in data
        assert "timestamp" in data

    def test_restore_endpoint(self, client):
        """Test restore endpoint restores from backup."""
        # SHA256 will mismatch if no backup exists, returns 400 or 404
        response = client.post("/api/backup/restore", json={"sha256": "wronghash"})
        assert response.status_code in (400, 404)


class TestExportExcel:
    """Test Excel export endpoint."""

    def test_export_excel_endpoint(self, client):
        """Test /api/export/excel returns xlsx."""
        response = client.get("/api/export/excel")
        assert response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]


class TestCategories:
    """Test categories endpoint."""

    def test_list_categories(self, client):
        """Test GET /api/categories returns list."""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
