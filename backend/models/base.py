"""
Shared SQLAlchemy Base for all models

This ensures all models use the same metadata and can reference each other.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create a single shared Base for all models
Base = declarative_base()
