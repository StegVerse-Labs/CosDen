from fastapi.testclient import TestClient

from CosDenOS.api import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["cosmetic_only"] is True


def test_plan_endpoint_for_adult_event():
    payload = {
        "user": {
            "age_years": 35,
            "tone_preference": "cool",
            "sensitivity_flag": True,
            "event_time_hours": 24,
            "notes": "Coffee drinker, wants gentle whitening before event."
        },
        "request_text": "Gentle cosmetic whitening and gloss for an important event tomorrow.",
    }

    resp = client.post("/plan", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["cosmetic_only"] is True
    assert data["interpreted_goal"]["goal_type"] in {
        "event_maximize",
        "gentle_start",
        "daily_maintenance",
        "mineral_support",
    }
    assert len(data["recommended_stack"]["codes"]) >= 1

    sim = data["simulation"]
    assert sim["cosmetic_only"] is True
    assert sim["aggregated_effect"]["brightness_delta"] >= 0.0


def test_simulate_endpoint_with_direct_codes():
    payload = {
        "user": {
            "age_years": 30,
            "tone_preference": None,
            "sensitivity_flag": False,
            "event_time_hours": None,
            "notes": None,
        },
        "codes": ["A1", "C1", "E1"],
    }

    resp = client.post("/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["cosmetic_only"] is True
    sim = data["simulation"]
    assert sim["stack_codes"] == ["A1", "C1", "E1"]
    assert sim["aggregated_effect"]["brightness_delta"] > 0.0
