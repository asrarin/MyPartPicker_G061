<<<<<<< HEAD
def check_compatibility(cpu, gpu, ram, motherboard, storage, psu, case):
    errors = []
    total_power = 50  # Base system overhead

    # Rule 1: CPU socket vs Motherboard socket
    if cpu and motherboard:
        if cpu.socket != motherboard.socket:
            errors.append(
                f'CPU/Motherboard socket mismatch: {cpu.name} uses {cpu.socket} '
                f'but {motherboard.name} supports {motherboard.socket}.'
            )

    # Rule 2: RAM type vs Motherboard RAM support
    if ram and motherboard:
        if ram.ram_type != motherboard.ram_type:
            errors.append(
                f'RAM type mismatch: {ram.name} is {ram.ram_type} but '
                f'{motherboard.name} supports {motherboard.ram_type}.'
            )

    # Rule 3: PSU wattage vs total system power draw
    if cpu and cpu.power_draw:
        total_power += cpu.power_draw
    if gpu and gpu.power_draw:
        total_power += gpu.power_draw
    if psu:
        if psu.wattage < total_power:
            errors.append(
                f'PSU too weak: System needs ~{total_power}W but '
                f'{psu.name} only provides {psu.wattage}W.'
            )

    # Rule 4: Case form factor vs Motherboard form factor
    fits = {'ATX': ['ATX'], 'mATX': ['ATX', 'mATX'], 'ITX': ['ATX', 'mATX', 'ITX']}
    if case and motherboard and motherboard.form_factor and case.form_factor:
        if case.form_factor not in fits.get(motherboard.form_factor, []):
            errors.append(
                f'Form factor mismatch: {case.name} ({case.form_factor}) does not '
                f'fit {motherboard.name} ({motherboard.form_factor}).'
            )

    return {
        'is_compatible': len(errors) == 0,
        'errors': errors,
        'total_power': total_power
    }
=======
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
>>>>>>> 717a1d73ff0f9b04c8166eb1af232afb821243ee
