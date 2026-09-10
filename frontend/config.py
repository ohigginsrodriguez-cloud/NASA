import os

BASE_URL = os.environ.get("NASA_API_URL", "http://localhost:8000")

REQUEST_TIMEOUT = 30