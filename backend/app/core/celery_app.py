from celery import Celery
from celery.schedules import crontab
import os

# Create Celery instance
celery_app = Celery(
    'naija_conflict_tracker',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    include=[
        'app.tasks.scraping_tasks',
        'app.tasks.data_processing_tasks',
        'app.tasks.monitoring_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Lagos',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    beat_schedule={
        # Scrape news sources every 6 hours
        'scrape-news-sources': {
            'task': 'app.tasks.scraping_tasks.scrape_all_news_sources',
            'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours at minute 0
            'options': {'queue': 'scraping'}
        },
        # Clean and process scraped data
        'process-scraped-data': {
            'task': 'app.tasks.data_processing_tasks.process_scraped_data',
            'schedule': crontab(minute=30, hour='*/6'),  # 30 minutes after scraping
            'options': {'queue': 'processing'}
        },
        # Verify and deduplicate data
        'verify-conflict-data': {
            'task': 'app.tasks.data_processing_tasks.verify_conflict_data',
            'schedule': crontab(minute=15, hour='*/6'),  # Run 15 minutes past every 6th hour
            'options': {'queue': 'verification'}
        },
        # Monitor pipeline health
        'monitor-pipeline-health': {
            'task': 'app.tasks.monitoring_tasks.check_pipeline_health',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
            'options': {'queue': 'monitoring'}
        },
        # Generate daily reports
        'generate-daily-report': {
            'task': 'app.tasks.monitoring_tasks.generate_daily_report',
            'schedule': crontab(minute=0, hour=23),  # Daily at 11 PM
            'options': {'queue': 'monitoring'}
        }
    },
    # Queue routing
    task_routes={
        'app.tasks.scraping_tasks.*': {'queue': 'scraping'},
        'app.tasks.data_processing_tasks.*': {'queue': 'processing'},
        'app.tasks.monitoring_tasks.*': {'queue': 'monitoring'}
    },
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    worker_disable_rate_limits=False,
)

# Optional: Configure Redis connection pooling
celery_app.conf.update(
    broker_connection_pool_kwargs={
        'max_connections': 20,
        'retry_on_timeout': True
    }
)

# Health check task
@celery_app.task(bind=True)
def health_check(self):
    """Simple health check for Celery workers"""
    return {
        'status': 'healthy',
        'worker': str(self.request.id),
        'timestamp': self.request.now
    }

if __name__ == '__main__':
    celery_app.start()
