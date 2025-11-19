import importlib.util
import os
from fastapi.testclient import TestClient


def _load_app_from_path():
    # Load the FastAPI app from src/app.py by file path so tests don't depend on package import
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(root, "src", "app.py")
    spec = importlib.util.spec_from_file_location("app_module", app_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def client():
    mod = _load_app_from_path()
    return TestClient(mod.app)


def test_get_activities():
    c = client()
    r = c.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    c = client()
    activity = "Chess Club"
    email = "test.user@mergington.edu"

    # Sign up
    r = c.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert email in r.json().get("message", "")

    # Verify participant was added
    r = c.get("/activities")
    data = r.json()
    assert email in data[activity]["participants"]

    # Duplicate signup should fail
    r = c.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 400

    # Unregister
    r = c.delete(f"/activities/{activity}/participants?email={email}")
    assert r.status_code == 200

    # Verify removal
    r = c.get("/activities")
    data = r.json()
    assert email not in data[activity]["participants"]
