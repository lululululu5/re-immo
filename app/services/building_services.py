import sqlalchemy as sa

from app.models import Building, Settings
from app import db

class BuildingCalculations:
    
    # Import data on start of application. Figure out whether this should be a database table
    def get_building_data(building_id):
        building_data = db.session.scalar(sa.select(Building).where(Building.id == building_id))
        # Figure out how to call data from database via building_id. Should we use a model or just from here?
        # Figure out the architecture of this. How should I structure the formulas in the best way? Just go for it and figure it out later.
        
        
    
    