from flask import Blueprint, render_template, request
from app.models import Part

parts = Blueprint('parts', __name__)

CATEGORIES = ['CPU', 'GPU', 'RAM', 'Motherboard', 'Storage', 'PSU', 'Case']


@parts.route('/')
@parts.route('/catalogue')
def catalogue():
    search    = request.args.get('search',    '').strip()
    category  = request.args.get('category',  '').strip()
    max_price = request.args.get('max_price', '').strip()

    query = Part.query

    if search:
        query = query.filter(
            (Part.name.ilike(f'%{search}%')) |
            (Part.brand.ilike(f'%{search}%'))
        )
    if category and category in CATEGORIES:
        query = query.filter_by(category=category)
    if max_price:
        try:
            query = query.filter(Part.price <= float(max_price))
        except ValueError:
            pass

    all_parts = query.order_by(Part.category, Part.price).all()

    return render_template(
        'parts/catalogue.html',
        parts=all_parts,
        categories=CATEGORIES,
        search=search,
        category=category,
        max_price=max_price,
    )


@parts.route('/part/<int:part_id>')
def detail(part_id):
    part = Part.query.get_or_404(part_id)
    return render_template('parts/detail.html', part=part)
