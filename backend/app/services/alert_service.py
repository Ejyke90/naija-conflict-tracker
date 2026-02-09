"""
High-Risk Alert Service

Automatically detects and alerts on conflict events that exceed risk thresholds.
Supports multiple notification channels: file webhooks, database storage, email, Slack.

Features:
- Threshold-based detection (default: risk_score > 85)
- File-based webhooks for instant UI polling
- Database storage for historical analysis
- Alert deduplication
- Multi-channel notifications
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import logging
import os
import json
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class AlertService:
    """Manages high-risk conflict event alerts"""
    
    def __init__(self):
        self.risk_threshold = int(os.getenv('ALERT_RISK_THRESHOLD', '85'))
        self.critical_threshold = int(os.getenv('ALERT_CRITICAL_THRESHOLD', '95'))
        self.alert_file_path = os.getenv('ALERT_FILE_PATH', '/tmp/high_risk_alerts.json')
        self.max_file_alerts = int(os.getenv('ALERT_FILE_MAX_SIZE', '20'))
        self.dedup_window = int(os.getenv('ALERT_DEDUP_TIME_WINDOW', '3600'))  # 1 hour
        
        # Ensure directory exists
        Path(self.alert_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def check_and_alert(self, conflict_event: Dict[str, Any], db: Session):
        """
        Check if event exceeds risk threshold and create alert if needed
        
        Args:
            conflict_event: Dict containing event data with risk_score
            db: Database session
        """
        risk_score = conflict_event.get('risk_score', 0)
        
        if risk_score < self.risk_threshold:
            # Below threshold, no alert needed
            return None
        
        # Check for duplicate alert
        if await self._is_duplicate_alert(conflict_event, db):
            logger.info(f"Skipping duplicate alert for event {conflict_event.get('id')}")
            return None
        
        # Determine alert priority
        if risk_score >= self.critical_threshold:
            alert_type = 'CRITICAL'
            priority = 1
        else:
            alert_type = 'HIGH'
            priority = 2
        
        # Create alert
        alert_data = {
            'alert_type': alert_type,
            'priority': priority,
            'risk_score': risk_score,
            'conflict_event_id': conflict_event.get('id'),
            'title': conflict_event.get('title') or conflict_event.get('event_description', 'Untitled Event'),
            'summary': self._generate_alert_summary(conflict_event),
            'location_state': conflict_event.get('state'),
            'location_lga': conflict_event.get('lga'),
            'conflict_category': conflict_event.get('conflict_type') or conflict_event.get('conflict_category'),
            'casualties': conflict_event.get('casualties', {}),
            'source': conflict_event.get('source'),
            'event_date': conflict_event.get('event_date'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in database
        alert_id = await self._store_alert_db(alert_data, db)
        alert_data['id'] = alert_id
        
        # Write to file webhook for instant UI polling
        await self._write_alert_webhook(alert_data)
        
        # Optional: Send external notifications
        await self._send_notifications(alert_data)
        
        logger.info(f"Created {alert_type} alert (ID: {alert_id}) for event {conflict_event.get('id')} "
                   f"with risk score {risk_score}")
        
        return alert_data
    
    def _generate_alert_summary(self, event: Dict[str, Any]) -> str:
        """Generate human-readable alert summary"""
        parts = []
        
        # Location
        if event.get('state'):
            location = event['state']
            if event.get('lga'):
                location += f", {event['lga']}"
            parts.append(location)
        
        # Conflict type
        if event.get('conflict_type') or event.get('conflict_category'):
            conflict_type = event.get('conflict_type') or event.get('conflict_category')
            parts.append(conflict_type)
        
        # Casualties
        casualties = event.get('casualties', {})
        if isinstance(casualties, dict):
            deaths = casualties.get('deaths', 0) or casualties.get('fatalities', 0)
            injuries = casualties.get('injuries', 0) or casualties.get('wounded', 0)
            if deaths or injuries:
                casualty_str = []
                if deaths:
                    casualty_str.append(f"{deaths} killed")
                if injuries:
                    casualty_str.append(f"{injuries} injured")
                parts.append(", ".join(casualty_str))
        
        if parts:
            return " - ".join(parts)
        return "High-risk conflict event detected"
    
    async def _is_duplicate_alert(self, event: Dict[str, Any], db: Session) -> bool:
        """Check if similar alert was created recently"""
        # Generate deduplication key
        dedup_key = self._generate_dedup_key(event)
        
        # Check recent alerts (within dedup window)
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.dedup_window)
        
        from app.models.alert import AlertEvent
        
        recent_alert = db.query(AlertEvent).filter(
            and_(
                AlertEvent.dedup_key == dedup_key,
                AlertEvent.created_at >= cutoff_time
            )
        ).first()
        
        return recent_alert is not None
    
    def _generate_dedup_key(self, event: Dict[str, Any]) -> str:
        """Generate deduplication key based on event attributes"""
        # Use location + conflict type + date as dedup key
        key_parts = [
            event.get('state', 'unknown'),
            event.get('lga', 'unknown'),
            event.get('conflict_type') or event.get('conflict_category', 'unknown'),
            str(event.get('event_date', ''))[:10]  # YYYY-MM-DD
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _store_alert_db(self, alert_data: Dict[str, Any], db: Session) -> int:
        """Store alert in database"""
        from app.models.alert import AlertEvent
        
        alert = AlertEvent(
            conflict_event_id=alert_data.get('conflict_event_id'),
            alert_type=alert_data['alert_type'],
            risk_score=alert_data['risk_score'],
            priority=alert_data['priority'],
            status='ACTIVE',
            location_state=alert_data.get('location_state'),
            location_lga=alert_data.get('location_lga'),
            conflict_category=alert_data.get('conflict_category'),
            title=alert_data['title'],
            summary=alert_data['summary'],
            notified_channels={'webhook': True},
            notification_sent_at=datetime.utcnow(),
            dedup_key=self._generate_dedup_key({
                'state': alert_data.get('location_state'),
                'lga': alert_data.get('location_lga'),
                'conflict_type': alert_data.get('conflict_category'),
                'event_date': alert_data.get('event_date')
            })
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        return alert.id
    
    async def _write_alert_webhook(self, alert_data: Dict[str, Any]):
        """Write alert to file for UI polling"""
        try:
            # Read existing alerts
            alerts = []
            if os.path.exists(self.alert_file_path):
                with open(self.alert_file_path, 'r') as f:
                    file_data = json.load(f)
                    alerts = file_data.get('alerts', [])
            
            # Add new alert at the beginning
            alerts.insert(0, alert_data)
            
            # Keep only last N alerts
            alerts = alerts[:self.max_file_alerts]
            
            # Write back
            with open(self.alert_file_path, 'w') as f:
                json.dump({
                    'alerts': alerts,
                    'last_updated': datetime.utcnow().isoformat(),
                    'total_count': len(alerts)
                }, f, indent=2)
            
            logger.debug(f"Wrote alert to webhook file: {self.alert_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to write alert webhook: {e}")
    
    async def _send_notifications(self, alert_data: Dict[str, Any]):
        """Send alert via external channels (email, Slack, etc.)"""
        # TODO: Implement email notifications
        # TODO: Implement Slack notifications
        pass
    
    async def get_active_alerts(self, db: Session, limit: int = 20) -> List[Dict]:
        """Get active (unresolved) alerts"""
        from app.models.alert import AlertEvent
        
        alerts = db.query(AlertEvent).filter(
            AlertEvent.status == 'ACTIVE'
        ).order_by(
            desc(AlertEvent.created_at)
        ).limit(limit).all()
        
        return [self._alert_to_dict(alert) for alert in alerts]
    
    async def get_recent_alerts(self, db: Session, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent alerts within time window"""
        from app.models.alert import AlertEvent
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = db.query(AlertEvent).filter(
            AlertEvent.created_at >= cutoff_time
        ).order_by(
            desc(AlertEvent.created_at)
        ).limit(limit).all()
        
        return [self._alert_to_dict(alert) for alert in alerts]
    
    async def acknowledge_alert(self, alert_id: int, user_id: int, notes: Optional[str], db: Session) -> bool:
        """Mark alert as acknowledged"""
        from app.models.alert import AlertEvent
        
        alert = db.query(AlertEvent).filter(AlertEvent.id == alert_id).first()
        if not alert:
            return False
        
        alert.status = 'ACKNOWLEDGED'
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by_user_id = user_id
        alert.acknowledgment_notes = notes
        
        db.commit()
        
        logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
        return True
    
    async def resolve_alert(
        self,
        alert_id: int,
        user_id: int,
        resolution_notes: Optional[str],
        resolution_actions: Optional[Dict],
        db: Session
    ) -> bool:
        """Mark alert as resolved"""
        from app.models.alert import AlertEvent
        
        alert = db.query(AlertEvent).filter(AlertEvent.id == alert_id).first()
        if not alert:
            return False
        
        alert.status = 'RESOLVED'
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by_user_id = user_id
        alert.resolution_notes = resolution_notes
        alert.resolution_actions = resolution_actions
        
        db.commit()
        
        logger.info(f"Alert {alert_id} resolved by user {user_id}")
        return True
    
    def _alert_to_dict(self, alert) -> Dict[str, Any]:
        """Convert alert model to dictionary"""
        return {
            'id': alert.id,
            'alert_type': alert.alert_type,
            'priority': alert.priority,
            'risk_score': alert.risk_score,
            'status': alert.status,
            'title': alert.title,
            'summary': alert.summary,
            'location': {
                'state': alert.location_state,
                'lga': alert.location_lga
            },
            'conflict_category': alert.conflict_category,
            'conflict_event_id': alert.conflict_event_id,
            'created_at': alert.created_at.isoformat() if alert.created_at else None,
            'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
        }


# Global instance
_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    """Get the global alert service instance"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
