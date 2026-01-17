from app.db.base_class import Base
from app.models.conflict import Conflict
from app.models.location import Location
from app.models.actor import Actor
from app.models.forecast import Forecast

# Import all models here to ensure they are registered with Base
__all__ = ["Conflict", "Location", "Actor", "Forecast"]
