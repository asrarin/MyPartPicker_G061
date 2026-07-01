from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Part, User
from app.routes.auth import admin_required

admin = Blueprint('admin', __name__, url_prefix='/admin')

CATEGORIES   = ['CPU', 'GPU', 'RAM', 'Motherboard', 'Storage', 'PSU', 'Case']
RETAILERS    = ['CZone', 'Harvey Norman', 'Shopee MY', 'Lazada MY', 'Other']
SOCKETS      = ['AM4', 'AM5', 'LGA1700', 'LGA1200', 'LGA2066']
RAM_TYPES    = ['DDR4', 'DDR5']
FORM_FACTORS = ['ATX', 'mATX', 'ITX']


def _form_args():
    return dict(categories=CATEGORIES, retailers=RETAILERS,
                sockets=SOCKETS, ram_types=RAM_TYPES, form_factors=FORM_FACTORS)


def _part_from_form(form, part=None):
    p = part or Part()
    p.name        = form.get('name',   '').strip()
    p.brand       = form.get('brand',  '').strip()
    p.category    = form.get('category', '').strip()
    p.specs       = form.get('specs',  '').strip()
    p.retailer    = form.get('retailer', '').strip()
    p.buy_url     = form.get('buy_url', '').strip() or None

    try:
        p.price = float(form.get('price', 0))
    except ValueError:
        p.price = 0.0

    p.socket      = form.get('socket',      '') or None
    p.ram_type    = form.get('ram_type',    '') or None
    p.form_factor = form.get('form_factor', '') or None

    w  = form.get('wattage',    '').strip()
    pd = form.get('power_draw', '').strip()
    p.wattage    = int(w)  if w.isdigit()  else None
    p.power_draw = int(pd) if pd.isdigit() else None
    return p


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@admin.route('/')
@login_required
@admin_required
def dashboard():
    parts = Part.query.order_by(Part.category, Part.name).all()
    users = User.query.order_by(User.id).all()
    return render_template('admin/dashboard.html', parts=parts, users=users)


# ── ADD PART ──────────────────────────────────────────────────────────────────
@admin.route('/part/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_part():
    if request.method == 'POST':
        if not request.form.get('name') or not request.form.get('category'):
            flash('Name and category are required.', 'danger')
            return redirect(url_for('admin.add_part'))
        new_part = _part_from_form(request.form)
        db.session.add(new_part)
        db.session.commit()
        flash(f'"{new_part.name}" added!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/part_form.html', part=None, **_form_args())


# ── EDIT PART ─────────────────────────────────────────────────────────────────
@admin.route('/part/edit/<int:part_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_part(part_id):
    part = Part.query.get_or_404(part_id)
    if request.method == 'POST':
        _part_from_form(request.form, part=part)
        db.session.commit()
        flash(f'"{part.name}" updated!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/part_form.html', part=part, **_form_args())


# ── DELETE PART ───────────────────────────────────────────────────────────────
@admin.route('/part/delete/<int:part_id>', methods=['POST'])
@login_required
@admin_required
def delete_part(part_id):
    part = Part.query.get_or_404(part_id)
    name = part.name
    db.session.delete(part)
    db.session.commit()
    flash(f'"{name}" removed.', 'info')
    return redirect(url_for('admin.dashboard'))
