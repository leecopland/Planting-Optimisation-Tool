import os
from dotenv import load_dotenv

# Path to .env inside the gis folder
ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # go up from config/ to gis/
    ".env",
)

load_dotenv(ENV_PATH)

SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT")
KEY_PATH = os.getenv("GEE_KEY_PATH")
