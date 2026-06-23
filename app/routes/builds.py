from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Part, Build
from app.compatibility import check_compatibility

builds = Blueprint('builds', __name__)

CATEGORIES = ['CPU', 'GPU', 'RAM', 'Motherboard', 'Storage', 'PSU', 'Case']


def _parts_by_category():
    return {cat: Part.query.filter_by(category=cat).order_by(Part.price).all()
            for cat in CATEGORIES}


def _selected_from_form(form):
    return {
        'cpu':         Part.query.get(form.get('cpu_id')),
        'gpu':         Part.query.get(form.get('gpu_id')),
        'ram':         Part.query.get(form.get('ram_id')),
        'motherboard': Part.query.get(form.get('motherboard_id')),
        'storage':     Part.query.get(form.get('storage_id')),
        'psu':         Part.query.get(form.get('psu_id')),
        'case':        Part.query.get(form.get('case_id')),
    }


# ── BUILDER ───────────────────────────────────────────────────────────────────
@builds.route('/builder', methods=['GET', 'POST'])
@login_required
def builder():
    pbc = _parts_by_category()

    if request.method == 'POST':
        sel        = _selected_from_form(request.form)
        result     = check_compatibility(
            sel['cpu'], sel['gpu'], sel['ram'],
            sel['motherboard'], sel['storage'],
            sel['psu'], sel['case']
        )
        total_cost = sum(p.price for p in sel.values() if p)

        if 'save' in request.form:
            build_name = request.form.get('build_name', '').strip() or 'My Build'
            new_build  = Build(
                name          = build_name,
                user_id       = current_user.id,
                is_compatible = result['is_compatible'],
                total_cost    = total_cost,
                cpu_id         = sel['cpu'].id         if sel['cpu']         else None,
                gpu_id         = sel['gpu'].id         if sel['gpu']         else None,
                ram_id         = sel['ram'].id         if sel['ram']         else None,
                motherboard_id = sel['motherboard'].id if sel['motherboard'] else None,
                storage_id     = sel['storage'].id     if sel['storage']     else None,
                psu_id         = sel['psu'].id         if sel['psu']         else None,
                case_id        = sel['case'].id        if sel['case']        else None,
            )
            db.session.add(new_build)
            db.session.commit()
            flash(f'Build "{build_name}" saved!', 'success')
            return redirect(url_for('builds.saved_builds'))

        return render_template(
            'builds/builder.html',
            parts_by_category=pbc,
            result=result,
            total_cost=total_cost,
            selections=sel,
        )

    return render_template('builds/builder.html', parts_by_category=pbc)


# ── SAVED BUILDS ──────────────────────────────────────────────────────────────
@builds.route('/builds')
@login_required
def saved_builds():
    user_builds = (Build.query
                   .filter_by(user_id=current_user.id)
                   .order_by(Build.created_at.desc())
                   .all())
    return render_template('builds/saved.html', builds=user_builds)


# ── EDIT BUILD ────────────────────────────────────────────────────────────────
@builds.route('/builds/edit/<int:build_id>', methods=['GET', 'POST'])
@login_required
def edit_build(build_id):
    build = Build.query.get_or_404(build_id)
    if build.user_id != current_user.id:
        flash('You do not have permission to edit this build.', 'danger')
        return redirect(url_for('builds.saved_builds'))

    pbc = _parts_by_category()

    if request.method == 'POST':
        sel        = _selected_from_form(request.form)
        result     = check_compatibility(
            sel['cpu'], sel['gpu'], sel['ram'],
            sel['motherboard'], sel['storage'],
            sel['psu'], sel['case']
        )
        total_cost = sum(p.price for p in sel.values() if p)

        build.name          = request.form.get('build_name', '').strip() or build.name
        build.is_compatible = result['is_compatible']
        build.total_cost    = total_cost
        build.cpu_id         = sel['cpu'].id         if sel['cpu']         else None
        build.gpu_id         = sel['gpu'].id         if sel['gpu']         else None
        build.ram_id         = sel['ram'].id         if sel['ram']         else None
        build.motherboard_id = sel['motherboard'].id if sel['motherboard'] else None
        build.storage_id     = sel['storage'].id     if sel['storage']     else None
        build.psu_id         = sel['psu'].id         if sel['psu']         else None
        build.case_id        = sel['case'].id        if sel['case']        else None

        db.session.commit()
        flash('Build updated!', 'success')
        return redirect(url_for('builds.saved_builds'))

    selections = {
        'cpu': build.cpu, 'gpu': build.gpu, 'ram': build.ram,
        'motherboard': build.motherboard, 'storage': build.storage,
        'psu': build.psu, 'case': build.case,
    }
    return render_template(
        'builds/builder.html',
        parts_by_category=pbc,
        selections=selections,
        build=build,
        editing=True,
    )


# ── DELETE BUILD ──────────────────────────────────────────────────────────────
@builds.route('/builds/delete/<int:build_id>', methods=['POST'])
@login_required
def delete_build(build_id):
    build = Build.query.get_or_404(build_id)
    if build.user_id != current_user.id:
        flash('You do not have permission to delete this build.', 'danger')
        return redirect(url_for('builds.saved_builds'))
    db.session.delete(build)
    db.session.commit()
    flash('Build deleted.', 'info')
    return redirect(url_for('builds.saved_builds'))
