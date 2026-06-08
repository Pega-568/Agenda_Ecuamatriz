"""
Rutas web para administradores
"""
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

web_admin_bp = Blueprint("web_admin", __name__, url_prefix="/admin")

@web_admin_bp.before_request
@login_required
def require_admin():
    if current_user.role_slug != 'admin':
        abort(403)

@web_admin_bp.route("/dashboard")
def dashboard():
    return render_template("admin/dashboard.html")

@web_admin_bp.route("/users", methods=["GET", "POST"])
def users():
    from app.users.models import User
    from app.roles.models import Role
    from app.areas.models import Area
    from app import db
    from flask import request, flash, redirect, url_for
    import werkzeug.security as ws
    
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        role_id = request.form.get("role_id")
        area_id = request.form.get("area_id")
        
        try:
            new_user = User(
                full_name=full_name,
                email=email,
                password_hash=ws.generate_password_hash(password) if password else "",
                role_id=role_id,
                area_id=area_id,
                is_active=True
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Usuario creado exitosamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear usuario: {str(e)}", "danger")
        return redirect(url_for("web_admin.users"))
        
    users_list = db.session.query(User).all()
    roles_list = db.session.query(Role).all()
    areas_list = db.session.query(Area).all()
    return render_template("admin/users.html", users=users_list, roles=roles_list, areas=areas_list)

@web_admin_bp.route("/areas", methods=["GET", "POST"])
def areas():
    from app.areas.models import Area
    from app import db
    from flask import request, flash, redirect, url_for
    
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        try:
            new_area = Area(name=name, description=description, is_active=True)
            db.session.add(new_area)
            db.session.commit()
            flash("Área creada exitosamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")
        return redirect(url_for("web_admin.areas"))
        
    areas_list = db.session.query(Area).all()
    return render_template("admin/areas.html", areas=areas_list)

@web_admin_bp.route("/rooms", methods=["GET", "POST"])
def rooms():
    from app.rooms.models import Room
    from app import db
    from flask import request, flash, redirect, url_for
    
    if request.method == "POST":
        name = request.form.get("name")
        capacity = request.form.get("capacity")
        location = request.form.get("location")
        resources = request.form.get("resources", "[]") # as JSON string, but actually it's a list. For prototype, we'll keep it empty.
        
        try:
            new_room = Room(name=name, capacity=int(capacity), location=location, resources=[], is_active=True)
            db.session.add(new_room)
            db.session.commit()
            flash("Sala creada exitosamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")
        return redirect(url_for("web_admin.rooms"))
        
    rooms_list = db.session.query(Room).all()
    return render_template("admin/rooms.html", rooms=rooms_list)

@web_admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    from app.settings.service import SettingsService
    from app.settings.models import SystemSetting
    from flask import request, flash, redirect, url_for
    from app import db
    
    if request.method == "POST":
        for key, value in request.form.items():
            if key != 'csrf_token':
                setting = SystemSetting.query.filter_by(key=key).first()
                if setting:
                    setting.value = value
        db.session.commit()
        flash("Configuraciones actualizadas.", "success")
        return redirect(url_for("web_admin.settings"))
        
    SettingsService.seed_defaults()
    settings_list = SystemSetting.query.all()
    return render_template("admin/settings.html", settings=settings_list)
