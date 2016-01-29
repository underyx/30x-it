import os
import urllib.parse

redis = urllib.parse.urlparse(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
