#!/usr/bin/env python3
"""
Celery Worker for Nigeria Conflict Tracker
Start with: celery -A celery_worker worker --loglevel=info --concurrency=4
"""

import os
from app.core.celery_app import celery_app

# Set default configuration
if not os.getenv('CELERY_BROKER_URL'):
    os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

if not os.getenv('CELERY_RESULT_BACKEND'):
    os.environ['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Configure logging
import logging
from celery.signals import setup_logging

@setup_logging.connect
def config_loggers(*args, **kwargs):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'logs/celery_worker.log',
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'celery': {
                'handlers': ['default', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'app.tasks': {
                'handlers': ['default', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    })

if __name__ == '__main__':
    celery_app.start()
