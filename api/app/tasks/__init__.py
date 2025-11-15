"""
Async tasks for FineData

Import all task modules to ensure Celery can discover and register them.
"""

# Import all task modules to register them with Celery
from . import benchmark, production, email
