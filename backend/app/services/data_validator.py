"""
Data Validation Service for Conflict Events
Validates incoming conflict data before insertion into the database
Implements quality checks and quarantine system for suspicious entries
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.models.conflict import ConflictEvent
from sqlalchemy import and_

logger = logging.getLogger(__name__)


class ConflictDataValidator:
    """Validates conflict event data before insertion"""
    
    # Nigerian states for validation
    NIGERIAN_STATES = {
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
        "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo",
        "Ekiti", "Enugu", "Federal Capital Territory", "Gombe", "Imo",
        "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara",
        "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo",
        "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"
    }
    
    # Valid conflict types
    VALID_CONFLICT_TYPES = {
        "Violence against civilians",
        "Battles",
        "Explosions/Remote violence",
        "Protests",
        "Protest",
        "Riot",
        "Riots",
        "Strategic developments",
        "Armed clash",
        "Armed violence",
        "Communal clash",
        "Ethnic clash",
        "Religious clash",
        "Cultism",
        "Kidnapping",
        "Terrorism",
        "Unknown"
    }
    
    # Valid actor types
    VALID_ACTOR_TYPES = {
        "State Forces",
        "Armed Group",
        "Armed Militia",
        "Religious Group",
        "Ethnic Group",
        "Criminal Group",
        "Unknown Actors"
    }
    
    # Maximum reasonable values for casualties
    MAX_FATALITIES_SINGLE_EVENT = 1000
    MAX_INJURIES_SINGLE_EVENT = 2000
    MAX_DISPLACED_PERSONS = 100000
    
    def __init__(self):
        self.validation_rules = [
            self.validate_required_fields,
            self.validate_date_format,
            self.validate_state,
            self.validate_casualties,
            self.validate_coordinates,
            self.validate_conflict_type,
            self.validate_actor_types,
            self.validate_no_duplicates,
        ]
    
    def validate(self, event_data: Dict[str, Any]) -> Tuple[bool, List[str], Optional[str]]:
        """
        Validate conflict event data
        
        Returns:
            (is_valid: bool, issues: List[str], severity: Optional[str])
            severity: 'warning', 'critical', or None if valid
        """
        issues = []
        severity = None
        
        for rule in self.validation_rules:
            rule_result = rule(event_data)
            if rule_result["has_issues"]:
                issues.extend(rule_result["issues"])
                if rule_result["severity"] == "critical":
                    severity = "critical"
                elif severity != "critical":
                    severity = "warning"
        
        is_valid = len(issues) == 0
        return is_valid, issues, severity
    
    def validate_required_fields(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check that all required fields are present"""
        required_fields = [
            "event_date",
            "state",
            "event_type",
            "fatalities"
        ]
        
        issues = []
        for field in required_fields:
            if field not in event_data or event_data[field] is None or event_data[field] == "":
                issues.append(f"Missing required field: {field}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "critical" if len(issues) > 0 else None
        }
    
    def validate_date_format(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event date is reasonable"""
        issues = []
        
        if "event_date" not in event_data:
            return {"has_issues": False, "issues": [], "severity": None}
        
        try:
            # Handle both datetime objects and date strings
            event_date_raw = event_data["event_date"]
            
            if isinstance(event_date_raw, str):
                # Try parsing as ISO format first (YYYY-MM-DD)
                event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()
            elif isinstance(event_date_raw, datetime):
                # If it's a datetime object, extract the date
                event_date = event_date_raw.date()
            else:
                # Assume it's already a date object
                event_date = event_date_raw
            
            # Check date is not in the future
            if event_date > datetime.now().date():
                issues.append(f"Event date is in the future: {event_date}")
            
            # Check date is not too old (before 2000)
            if event_date.year < 2000:
                issues.append(f"Event date is suspiciously old: {event_date}")
        
        except (ValueError, TypeError, AttributeError) as e:
            issues.append(f"Invalid date format: {event_data.get('event_date')}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "critical" if len(issues) > 0 else None
        }
    
    def validate_state(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate state is a valid Nigerian state"""
        issues = []
        
        if "state" not in event_data:
            return {"has_issues": False, "issues": [], "severity": None}
        
        state = event_data["state"]
        
        # Normalize state name
        state_normalized = state.strip().title() if isinstance(state, str) else state
        
        # Check exact match
        if state_normalized not in self.NIGERIAN_STATES:
            # Try case-insensitive match
            state_match = [s for s in self.NIGERIAN_STATES if s.lower() == state.lower()]
            if not state_match:
                issues.append(f"Invalid state: '{state}'. Not a recognized Nigerian state.")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "critical" if len(issues) > 0 else "warning"
        }
    
    def validate_casualties(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate casualty numbers are reasonable"""
        issues = []
        
        casualty_fields = ["fatalities", "injuries", "displaced_persons"]
        
        for field in casualty_fields:
            if field in event_data and event_data[field] is not None:
                try:
                    value = int(event_data[field])
                    
                    # Check for negative values
                    if value < 0:
                        issues.append(f"{field} cannot be negative: {value}")
                    
                    # Check for suspicious values
                    if field == "fatalities" and value > self.MAX_FATALITIES_SINGLE_EVENT:
                        issues.append(f"{field} exceeds maximum reasonable value ({self.MAX_FATALITIES_SINGLE_EVENT}): {value}")
                    elif field == "injuries" and value > self.MAX_INJURIES_SINGLE_EVENT:
                        issues.append(f"{field} exceeds maximum reasonable value ({self.MAX_INJURIES_SINGLE_EVENT}): {value}")
                    elif field == "displaced_persons" and value > self.MAX_DISPLACED_PERSONS:
                        issues.append(f"{field} exceeds maximum reasonable value ({self.MAX_DISPLACED_PERSONS}): {value}")
                
                except (ValueError, TypeError):
                    issues.append(f"{field} must be a number: {event_data[field]}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "warning"
        }
    
    def validate_coordinates(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate latitude/longitude if provided"""
        issues = []
        
        if "latitude" in event_data and event_data["latitude"] is not None:
            try:
                lat = float(event_data["latitude"])
                if not -90 <= lat <= 90:
                    issues.append(f"Latitude must be between -90 and 90: {lat}")
                # Nigeria is roughly between 4-14 degrees
                if not 4 <= lat <= 14:
                    issues.append(f"Latitude {lat} is outside Nigeria's range (4-14)")
            except (ValueError, TypeError):
                issues.append(f"Latitude must be a number: {event_data['latitude']}")
        
        if "longitude" in event_data and event_data["longitude"] is not None:
            try:
                lon = float(event_data["longitude"])
                if not -180 <= lon <= 180:
                    issues.append(f"Longitude must be between -180 and 180: {lon}")
                # Nigeria is roughly between 2-15 degrees
                if not 2 <= lon <= 15:
                    issues.append(f"Longitude {lon} is outside Nigeria's range (2-15)")
            except (ValueError, TypeError):
                issues.append(f"Longitude must be a number: {event_data['longitude']}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "warning"
        }
    
    def validate_conflict_type(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate conflict type is recognized"""
        issues = []
        
        if "event_type" not in event_data or not event_data["event_type"]:
            return {"has_issues": False, "issues": [], "severity": None}
        
        event_type = event_data["event_type"].strip()
        
        if event_type not in self.VALID_CONFLICT_TYPES:
            issues.append(f"Unknown conflict type: '{event_type}'")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "warning"
        }
    
    def validate_actor_types(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate actor types if provided"""
        issues = []
        
        for actor_field in ["actor1_type", "actor2_type"]:
            if actor_field in event_data and event_data[actor_field]:
                actor_type = event_data[actor_field].strip()
                if actor_type not in self.VALID_ACTOR_TYPES:
                    issues.append(f"Unknown actor type in {actor_field}: '{actor_type}'")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "warning"
        }
    
    def validate_no_duplicates(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for duplicate entries"""
        issues = []
        
        # Duplicate detection based on: location, date, actor
        if all(k in event_data for k in ["event_date", "state", "actor1", "fatalities"]):
            db = SessionLocal()
            try:
                # Look for similar events in the last 7 days
                if isinstance(event_data["event_date"], str):
                    event_date = datetime.strptime(event_data["event_date"], "%Y-%m-%d").date()
                else:
                    event_date = event_data["event_date"]
                
                similar_events = db.query(ConflictEvent).filter(
                    and_(
                        ConflictEvent.event_date >= event_date - timedelta(days=7),
                        ConflictEvent.event_date <= event_date + timedelta(days=1),
                        ConflictEvent.state == event_data["state"].strip().title(),
                        ConflictEvent.actor1 == event_data["actor1"],
                        ConflictEvent.fatalities == int(event_data["fatalities"])
                    )
                ).all()
                
                if similar_events:
                    issues.append(f"Potential duplicate: Found {len(similar_events)} similar events in database")
            
            except Exception as e:
                logger.warning(f"Could not check for duplicates: {e}")
            
            finally:
                db.close()
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "severity": "warning"
        }
    
    def get_validation_summary(self, results: List[Tuple[bool, List[str], Optional[str]]]) -> Dict[str, Any]:
        """Generate summary statistics from validation results"""
        total = len(results)
        passed = sum(1 for is_valid, _, _ in results if is_valid)
        failed = total - passed
        critical_issues = sum(1 for _, _, severity in results if severity == "critical")
        warning_issues = sum(1 for _, _, severity in results if severity == "warning")
        
        return {
            "total_records": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "timestamp": datetime.utcnow().isoformat()
        }
