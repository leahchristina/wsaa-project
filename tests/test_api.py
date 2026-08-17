import sys
import unittest
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER))

from app import app


class TestApi(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_all_machines(self):
        response = self.client.get("/api/machines")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_unknown_machine_returns_404(self):
        response = self.client.get("/api/machines/999999")

        self.assertEqual(response.status_code, 404)

        response_data = response.get_json()

        self.assertEqual(
            response_data["error"],
            "Machine not found"
        )

def test_invalid_machine_capacity_returns_400(self):
    invalid_machine = {
        "machine_code": "TEST-INVALID",
        "machine_name": "Invalid Test Machine",
        "production_area": "TEST",
        "daily_capacity": 0,
        "active": True
    }

    response = self.client.post(
        "/api/machines",
        json=invalid_machine
    )

    self.assertEqual(response.status_code, 400)

    response_data = response.get_json()

    self.assertEqual(
        response_data["error"],
        "Validation failed"
    )

    self.assertEqual(
        response_data["message"],
        "Daily capacity must be greater than zero."
    )


if __name__ == "__main__":
    unittest.main()