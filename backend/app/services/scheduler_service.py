"""
APScheduler Service for Autonomous Background Task Scheduling

This service provides self-contained scheduling within the FastAPI lifecycle,
eliminating the need for external process management (Celery Beat).

Features:
- Integrated with FastAPI startup/shutdown
- 15-minute automated scraping schedule
- Health checks and status monitoring
- Execution logging and audit trail
- Graceful shutdown handling
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import os
import json
import traceback
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


class SchedulerService:
    """Manages APScheduler for background task automation"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone='Africa/Lagos',
            job_defaults={
                'coalesce': True,  # Combine missed executions
                'max_instances': 1,  # Prevent concurrent executions
                'misfire_grace_time': 300  # 5 minutes grace period
            }
        )
        self.enabled = os.getenv('APSCHEDULER_ENABLED', 'false').lower() == 'true'
        self.automation_log_file = os.getenv('AUTOMATION_LOG_FILE', '/tmp/automation_logs.json')
        self.log_retention = int(os.getenv('AUTOMATION_LOG_RETENTION', '100'))
    
    @property
    def running(self) -> bool:
        """Check if the AsyncIOScheduler is running"""
        return self.scheduler.running if self.scheduler else False
        
    def start(self):
        """Start the scheduler during application startup"""
        if not self.enabled:
            logger.info("APScheduler disabled via configuration")
            return
        
        try:
            # Ensure log directory exists
            Path(self.automation_log_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Register scheduled jobs
            self._register_jobs()
            
            # Ensure there's an event loop available in this thread. When the
            # startup path runs in a thread without a current event loop (for
            # example when the service spawns its own init thread),
            # AsyncIOScheduler.start() will raise "There is no current event
            # loop in thread ...". Create and set a new loop if necessary.
            try:
                asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Start scheduler
            self.scheduler.start()
            logger.info("APScheduler started successfully")
            logger.info(f"Registered {len(self.scheduler.get_jobs())} jobs")
            
        except Exception as e:
            logger.error(f"Failed to start APScheduler: {e}")
            logger.error(traceback.format_exc())
    
    def shutdown(self):
        """Shutdown scheduler during application shutdown"""
        if not self.enabled or not self.running:
            return
        
        try:
            logger.info("Shutting down APScheduler...")
            self.scheduler.shutdown(wait=True)
            logger.info("APScheduler shutdown complete")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")
    
    def _register_jobs(self):
        """Register all scheduled jobs"""
        from app.tasks.scraping_tasks import scrape_all_news_sources
        
        # Get schedule from environment or use default (15 minutes)
        scraping_schedule = os.getenv('SCRAPING_SCHEDULE', '*/15 * * * *')
        
        # Add automated scraping job
        self.scheduler.add_job(
            func=self._run_scraping_job,
            trigger=CronTrigger.from_crontab(scraping_schedule),
            id='automated_scrape',
            name='Automated News Scraping',
            replace_existing=True
        )
        
        logger.info(f"Registered automated scraping job with schedule: {scraping_schedule}")
    
    async def _run_scraping_job(self):
        """Execute scraping job with logging"""
        job_id = 'automated_scrape'
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting scheduled scraping job: {job_id}")
            
            # Import here to avoid circular dependencies
            from app.tasks.scraping_tasks import scrape_all_news_sources
            from app.core.celery_app import celery_app
            
            # Trigger Celery task (async execution)
            result = celery_app.send_task(
                'app.tasks.scraping_tasks.scrape_all_news_sources',
                queue='scraping'
            )
            
            # Wait for result (with timeout)
            task_result = result.get(timeout=1800)  # 30 minute timeout
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Log successful execution
            await self._log_execution(
                job_id=job_id,
                job_name='Automated News Scraping',
                status='success',
                duration=duration,
                details=task_result
            )
            
            logger.info(f"Scraping job completed successfully in {duration:.2f} seconds")
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Log failed execution
            await self._log_execution(
                job_id=job_id,
                job_name='Automated News Scraping',
                status='failure',
                duration=duration,
                error=str(e),
                traceback=traceback.format_exc()
            )
            
            logger.error(f"Scraping job failed after {duration:.2f} seconds: {e}")
            logger.error(traceback.format_exc())
    
    async def _log_execution(
        self,
        job_id: str,
        job_name: str,
        status: str,
        duration: float,
        details: Optional[Dict] = None,
        error: Optional[str] = None,
        traceback: Optional[str] = None
    ):
        """Log job execution to file and database"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'job_id': job_id,
            'job_name': job_name,
            'status': status,
            'duration_seconds': round(duration, 2),
            'details': details or {},
            'error': error,
            'traceback': traceback
        }
        
        # Log to file for real-time monitoring
        try:
            logs = []
            if os.path.exists(self.automation_log_file):
                with open(self.automation_log_file, 'r') as f:
                    logs = json.load(f).get('logs', [])
            
            # Add new log
            logs.insert(0, log_entry)
            
            # Keep only last N entries
            logs = logs[:self.log_retention]
            
            # Write back
            with open(self.automation_log_file, 'w') as f:
                json.dump({
                    'logs': logs,
                    'last_updated': datetime.utcnow().isoformat()
                }, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to write automation log to file: {e}")
        
        # TODO: Log to database for historical analysis
        # from app.db.database import get_db
        # db = next(get_db())
        # db.execute(insert_automation_execution_log)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        if not self.enabled:
            return {
                'enabled': False,
                'status': 'disabled',
                'message': 'APScheduler is disabled via configuration'
            }
        
        if not self.scheduler.running:
            return {
                'enabled': True,
                'status': 'stopped',
                'message': 'Scheduler is not running'
            }
        
        # Get job info
        jobs = self.scheduler.get_jobs()
        status_info = {
            'enabled': True,
            'status': 'running',
            'active_jobs': len(jobs),
            'jobs': []
        }
        
        for job in jobs:
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            
            # Calculate countdown to next run
            if job.next_run_time:
                now = datetime.now(job.next_run_time.tzinfo)
                delta = job.next_run_time - now
                job_info['next_run_in_seconds'] = int(delta.total_seconds())
            
            status_info['jobs'].append(job_info)
        
        # Get last execution from logs
        try:
            if os.path.exists(self.automation_log_file):
                with open(self.automation_log_file, 'r') as f:
                    log_data = json.load(f)
                    logs = log_data.get('logs', [])
                    if logs:
                        last_log = logs[0]
                        status_info['last_execution'] = {
                            'timestamp': last_log['timestamp'],
                            'status': last_log['status'],
                            'duration': last_log['duration_seconds']
                        }
        except Exception as e:
            logger.error(f"Failed to read last execution from logs: {e}")
        
        return status_info
    
    def trigger_job(self, job_id: str):
        """Manually trigger a job immediately"""
        if not self.scheduler.running:
            raise RuntimeError("Scheduler is not running")
        
        job = self.scheduler.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Modify job to run immediately (one-time)
        job.modify(next_run_time=datetime.now())
        logger.info(f"Manually triggered job: {job_id}")
    
    def pause(self):
        """Pause all scheduled jobs"""
        if not self.scheduler.running:
            raise RuntimeError("Scheduler is not running")
        
        self.scheduler.pause()
        logger.info("Scheduler paused")
    
    def resume(self):
        """Resume scheduled jobs"""
        if not self.scheduler.running:
            raise RuntimeError("Scheduler is not running")
        
        self.scheduler.resume()
        logger.info("Scheduler resumed")
    
    def get_logs(self, limit: int = 100, status_filter: Optional[str] = None) -> List[Dict]:
        """Get automation execution logs"""
        try:
            if not os.path.exists(self.automation_log_file):
                return []
            
            with open(self.automation_log_file, 'r') as f:
                log_data = json.load(f)
                logs = log_data.get('logs', [])
            
            # Apply filters
            if status_filter:
                logs = [log for log in logs if log['status'] == status_filter]
            
            # Apply limit
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"Failed to read automation logs: {e}")
            return []


# Global instance
def get_scheduler() -> SchedulerService:
    """Get the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerService()
    return _scheduler
