from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Part(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    brand       = db.Column(db.String(80),  nullable=False)
    category    = db.Column(db.String(50),  nullable=False)
    price       = db.Column(db.Float,       nullable=False)
    retailer    = db.Column(db.String(100), nullable=False)
    specs       = db.Column(db.Text)
    socket      = db.Column(db.String(50))
    ram_type    = db.Column(db.String(20))
    wattage     = db.Column(db.Integer)
    power_draw  = db.Column(db.Integer)
    form_factor = db.Column(db.String(30))

class Build(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_compatible = db.Column(db.Boolean, default=False)
    total_cost    = db.Column(db.Float, default=0.0)
    cpu_id         = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=True)
    gpu_id         = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=True)
    ram_id         = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=True)
    motherboard_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=True)
    storage_id     = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=True)
    psu_id         = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=True)
    case_id        = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=True)
    cpu         = db.relationship('Part', foreign_keys=[cpu_id])
    gpu         = db.relationship('Part', foreign_keys=[gpu_id])
    ram         = db.relationship('Part', foreign_keys=[ram_id])
    motherboard = db.relationship('Part', foreign_keys=[motherboard_id])
    storage     = db.relationship('Part', foreign_keys=[storage_id])
    psu         = db.relationship('Part', foreign_keys=[psu_id])
    case        = db.relationship('Part', foreign_keys=[case_id])
