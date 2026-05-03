# app/routes/auth.py
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from functools import wraps
from flask import abort

auth = Blueprint('auth', __name__)

# ── ADMIN DECORATOR (used by admin routes) ──
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ── REGISTER ──
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
        hashed = generate_password_hash(password)
        db.session.add(User(username=username, email=email, password=hashed))
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

# ── LOGIN ──
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('parts.catalogue'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

# ── LOGOUT ──
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# ── PROFILE ──
@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        db.session.commit()
        flash('Profile updated.', 'success')
    return render_template('auth/profile.html')
