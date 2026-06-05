from .base import *  # noqa: F401, F403

DEBUG = True

# Use in-memory channel layer for development without Redis
# Override with Redis if available
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('localhost', 6379)],
        },
    },
}
