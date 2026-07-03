import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import User

auth = Blueprint('auth', __name__)


def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


# ── ADMIN DECORATOR ──────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── REGISTER ─────────────────────────────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('parts.catalogue'))

    if request.method == 'POST':
        username         = request.form.get('username', '').strip()
        email            = request.form.get('email', '').strip().lower()
        password         = request.form.get('password', '')
        confirm          = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return redirect(url_for('auth.register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('auth.register'))
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'danger')
            return redirect(url_for('auth.register'))

        db.session.add(User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        ))
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('parts.catalogue'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('parts.catalogue'))
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


# ── LOGOUT ────────────────────────────────────────────────────────────────────
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ── PROFILE ───────────────────────────────────────────────────────────────────
@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return redirect(url_for('auth.profile'))
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != current_user.id:
            flash('That username is already taken.', 'danger')
            return redirect(url_for('auth.profile'))

        # ── Handle profile picture upload ──
        file = request.files.get('profile_picture')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Invalid file type. Use PNG, JPG, JPEG, GIF, or WEBP.', 'danger')
                return redirect(url_for('auth.profile'))

            ext = file.filename.rsplit('.', 1)[1].lower()
            new_filename = secure_filename(f'user_{current_user.id}.{ext}')
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)

            # Remove old picture if it had a different extension
            if current_user.profile_picture and current_user.profile_picture != new_filename:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.profile_picture)
                if os.path.exists(old_path):
                    os.remove(old_path)

            file.save(upload_path)
            current_user.profile_picture = new_filename

        current_user.username = username
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


# ── REMOVE PROFILE PICTURE ────────────────────────────────────────────────────
@auth.route('/profile/remove-picture', methods=['POST'])
@login_required
def remove_picture():
    if current_user.profile_picture:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.profile_picture)
        if os.path.exists(old_path):
            os.remove(old_path)
        current_user.profile_picture = None
        db.session.commit()
        flash('Profile picture removed.', 'info')
    return redirect(url_for('auth.profile'))


# ── FORGOT PASSWORD ───────────────────────────────────────────────────────────
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('parts.catalogue'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()

        if user:
            token      = user.generate_reset_token()
            db.session.commit()
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            return render_template(
                'auth/forgot_password.html',
                reset_link=reset_link,
                email=email,
                link_generated=True
            )

        flash('If that email is registered, a reset link has been generated.', 'info')
        return redirect(url_for('auth.forgot_password'))

    return render_template('auth/forgot_password.html', link_generated=False)


# ── RESET PASSWORD ────────────────────────────────────────────────────────────
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('parts.catalogue'))

    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.is_token_valid():
        flash('This reset link is invalid or has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        user.password = generate_password_hash(password)
        user.clear_reset_token()
        db.session.commit()

        flash('Password reset successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


# ── ERROR HANDLERS ────────────────────────────────────────────────────────────
@auth.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@auth.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
