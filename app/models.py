import secrets
from datetime import datetime

from flask_login import UserMixin

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True, unique=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)

    builds = db.relationship(
        "Build", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def generate_reset_token(self):
        from datetime import timedelta

        self.reset_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.utcnow() + timedelta(minutes=30)
        return self.reset_token

    def is_token_valid(self):
        if not self.reset_token or not self.token_expiry:
            return False
        return datetime.utcnow() < self.token_expiry

    def clear_reset_token(self):
        self.reset_token = None
        self.token_expiry = None

    def avatar_path(self):
        """Returns the static-relative path to the avatar, or None if not set."""
        if self.profile_picture:
            return f"uploads/profile_pics/{self.profile_picture}"
        return None


class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    retailer = db.Column(db.String(100), nullable=False)
    buy_url = db.Column(db.String(500), nullable=True)
    specs = db.Column(db.Text)
    socket = db.Column(db.String(50))
    ram_type = db.Column(db.String(20))
    wattage = db.Column(db.Integer)
    power_draw = db.Column(db.Integer)
    form_factor = db.Column(db.String(30))


class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_compatible = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    total_cost = db.Column(db.Float, default=0.0)
    cpu_id = db.Column(db.Integer, db.ForeignKey("part.id"), nullable=True)
    gpu_id = db.Column(db.Integer, db.ForeignKey("part.id"), nullable=True)
    ram_id = db.Column(db.Integer, db.ForeignKey("part.id"), nullable=True)
    motherboard_id = db.Column(db.Integer, db.ForeignKey("part.id"), nullable=True)
    storage_id = db.Column(db.Integer, db.ForeignKey("part.id"), nullable=True)
    psu_id = db.Column(db.Integer, db.ForeignKey("part.id"), nullable=True)
    case_id = db.Column(db.Integer, db.ForeignKey("part.id"), nullable=True)
    cpu = db.relationship("Part", foreign_keys=[cpu_id])
    gpu = db.relationship("Part", foreign_keys=[gpu_id])
    ram = db.relationship("Part", foreign_keys=[ram_id])
    motherboard = db.relationship("Part", foreign_keys=[motherboard_id])
    storage = db.relationship("Part", foreign_keys=[storage_id])
    psu = db.relationship("Part", foreign_keys=[psu_id])
    case = db.relationship("Part", foreign_keys=[case_id])

    def parts_list(self):
        return [
            ("CPU", self.cpu),
            ("GPU", self.gpu),
            ("RAM", self.ram),
            ("Motherboard", self.motherboard),
            ("Storage", self.storage),
            ("PSU", self.psu),
            ("Case", self.case),
        ]
