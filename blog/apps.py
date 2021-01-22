from django.apps import AppConfig

# Debug logging only
import logging
logger = logging.getLogger(__name__)

class BlogConfig(AppConfig):
    name = 'blog'
