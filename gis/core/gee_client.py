from config.settings import SERVICE_ACCOUNT, KEY_PATH


def init_gee():
    """Initialize Google Earth Engine using central config."""
    import ee

    if not SERVICE_ACCOUNT or not KEY_PATH:
        raise RuntimeError(
            "Missing GEE_SERVICE_ACCOUNT or GEE_KEY_PATH in environment variables."
        )

    creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(creds)

    return True
