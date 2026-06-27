from dotenv import load_dotenv
import os
import json
import logging
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def _load_config_data():
    try:
        with open("local.settings.json", "r", encoding="utf-8") as config_file:
            raw_config = json.load(config_file)
        if isinstance(raw_config, dict):
            values = raw_config.get("Values")
            if isinstance(values, dict):
                return values
            return raw_config
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}


def _get_setting(name):
    return os.getenv(name) or config_data.get(name)


def _load_repository_configs():
    """Load multiple repository configurations from repository_path.json."""
    try:
        with open("repository_path.json", "r", encoding="utf-8") as repo_file:
            configs = json.load(repo_file)
        if isinstance(configs, list):
            logger.info("Loaded %d repository configuration(s) from repository_path.json", len(configs))
            return configs
        elif isinstance(configs, dict):
            # Single config as dict, wrap in list
            return [configs]
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.warning("Could not load repository_path.json: %s", e)
    return []


config_data = _load_config_data()

OPEN_AI_KEY = _get_setting("OPEN_AI_KEY")
OPEN_AI_ENDPOINT = _get_setting("OPEN_AI_ENDPOINT")
OPEN_AI_DEPLOYMENT_NAME = _get_setting("OPEN_AI_DEPLOYMENT_NAME")

GOOGLE_TYPE = _get_setting("GOOGLE_TYPE")
GOOGLE_PROJECT_ID = _get_setting("GOOGLE_PROJECT_ID")
GOOGLE_PRIVATE_KEY_ID = _get_setting("GOOGLE_PRIVATE_KEY_ID")
_google_private_key = _get_setting("GOOGLE_PRIVATE_KEY")
GOOGLE_PRIVATE_KEY = _google_private_key.replace("\\n", "\n") if _google_private_key else None
GOOGLE_CLIENT_EMAIL = _get_setting("GOOGLE_CLIENT_EMAIL")
GOOGLE_CLIENT_ID = _get_setting("GOOGLE_CLIENT_ID")
GOOGLE_AUTH_URI = _get_setting("GOOGLE_AUTH_URI")
GOOGLE_TOKEN_URI = _get_setting("GOOGLE_TOKEN_URI")
GOOGLE_AUTH_PROVIDER_X509_CERT_URL = _get_setting("GOOGLE_AUTH_PROVIDER_X509_CERT_URL")
GOOGLE_CLIENT_X509_CERT_URL = _get_setting("GOOGLE_CLIENT_X509_CERT_URL")
GOOGLE_UNIVERSE_DOMAIN = _get_setting("GOOGLE_UNIVERSE_DOMAIN")

# Load multiple repository configurations
REPOSITORY_CONFIGS = _load_repository_configs()

# Keep legacy single config support (from first config or env vars)
if REPOSITORY_CONFIGS:
    GOOGLE_DRIVE_FOLDER_ID = REPOSITORY_CONFIGS[0].get("GOOGLE_DRIVE_FOLDER_ID")
    GOOGLE_SHEET_NAME = REPOSITORY_CONFIGS[0].get("GOOGLE_SHEET_NAME")
    GOOGLE_WORKSHEET_ID = REPOSITORY_CONFIGS[0].get("GOOGLE_WORKSHEET_ID")
else:
    GOOGLE_DRIVE_FOLDER_ID = _get_setting("GOOGLE_DRIVE_FOLDER_ID")
    GOOGLE_SHEET_NAME = _get_setting("GOOGLE_SHEET_NAME")
    GOOGLE_WORKSHEET_ID = _get_setting("GOOGLE_WORKSHEET_ID")
