from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from Auth.models import User
from extra_utils import db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    pending_users = User.query.filter_by(is_approved=False).all()
    approved_users = User.query.filter_by(is_approved=True).all()
    return render_template('admin.html', pending_users=pending_users, approved_users=approved_users)

@admin_bp.route('/approve/<int:user_id>')
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    user.approved_at = datetime.utcnow()
    user.approved_by = current_user.id
    db.session.commit()
    flash(f'User {user.username} has been approved.', 'success')
    return redirect('/admin')

@admin_bp.route('/reject/<int:user_id>')
@login_required
@admin_required
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been rejected and deleted.', 'info')
    return redirect('/admin')

@admin_bp.route('/revoke/<int:user_id>')
@login_required
@admin_required
def revoke_access(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot revoke access from admin users.', 'error')
    else:
        user.is_approved = False
        user.approved_at = None
        user.approved_by = None
        db.session.commit()
        flash(f'Access revoked for user {user.username}.', 'info')
    return redirect('/admin')
