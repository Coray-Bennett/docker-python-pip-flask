from sqlalchemy import Enum
import enum
from .bird_data import db

class GroupCategory(enum.Enum):
    LOCATION = "location"
    GENUS = "genus"
    COLOR = "color"
    BEHAVIOR = "behavior"
    OTHER = "other"

class BirdGroup(db.Model):
    __tablename__ = 'bird_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(Enum(GroupCategory))
    description = db.Column(db.String(1024))

class BirdGroupEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bird_group_id = db.Column(db.Integer, db.ForeignKey('bird_group.id'))
    bird_data_id = db.Column(db.Integer, db.ForeignKey('bird_data.id'))