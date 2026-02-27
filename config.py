"""
Pipeline configuration. Uses environment variables with fallbacks for local dev.
"""
import os
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "olist_dw")
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "data", "olist"))


def get_connection_string():
    """SQLAlchemy-compatible connection string (password URL-encoded)."""
    pw = quote_plus(POSTGRES_PASSWORD) if POSTGRES_PASSWORD else ""
    return (
        f"postgresql+psycopg2://{POSTGRES_USER}:{pw}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


def get_psycopg2_connection_string():
    """For dbt and other tools that expect postgres:// style."""
    return get_connection_string().replace("postgresql+psycopg2://", "postgresql://")
