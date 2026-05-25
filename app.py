from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# MODEL
# =========================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), default='user')

# =========================
# DATABASE INIT
# =========================

with app.app_context():

    db.create_all()

    admin_exists = User.query.filter_by(username='admin').first()

    if not admin_exists:

        admin = User(
            username='admin',
            password=generate_password_hash('admin'),
            role='admin'
        )

        db.session.add(admin)

        db.session.commit()

# =========================
# HELPERS
# =========================

def current_user():

    if 'user_id' in session:

        return User.query.get(session['user_id'])

    return None

def is_admin():

    user = current_user()

    return user and user.role == 'admin'

# =========================
# HOME
# =========================

@app.route('/')
def index():

    return render_template(
        'index.html',
        user=current_user()
    )

# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:

            flash('Utilisateur déjà existant')

            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role='user'
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect(url_for('login'))

    return render_template(
        'register.html',
        user=current_user()
    )

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.id

            return redirect(url_for('index'))

        flash('Identifiants invalides')

    return render_template(
        'login.html',
        user=current_user()
    )

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('index'))

# =========================
# PROFILE
# =========================

@app.route('/profile')
def profile():

    user = current_user()

    if not user:

        return redirect(url_for('login'))

    return render_template(
        'profile.html',
        user=user
    )

# =========================
# ADMIN USERS
# =========================

@app.route('/admin/users')
def admin_users():

    if not is_admin():

        return redirect(url_for('index'))

    users = User.query.all()

    return render_template(
        'admin_users.html',
        users=users,
        user=current_user()
    )

# =========================
# CREATE USER
# =========================

@app.route('/admin/users/create', methods=['POST'])
def create_user():

    if not is_admin():

        return redirect(url_for('index'))

    username = request.form['username']

    password = request.form['password']

    role = request.form['role']

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:

        flash('Utilisateur déjà existant')

        return redirect(url_for('admin_users'))

    new_user = User(
        username=username,
        password=generate_password_hash(password),
        role=role
    )

    db.session.add(new_user)

    db.session.commit()

    return redirect(url_for('admin_users'))

# =========================
# EDIT USER
# =========================

@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):

    if not is_admin():

        return redirect(url_for('index'))

    edit_user = User.query.get_or_404(id)

    if request.method == 'POST':

        edit_user.username = request.form['username']

        edit_user.role = request.form['role']

        db.session.commit()

        return redirect(url_for('admin_users'))

    return render_template(
        'edit_user.html',
        edit_user=edit_user,
        user=current_user()
    )

# =========================
# DELETE USER
# =========================

@app.route('/admin/users/delete/<int:id>')
def delete_user(id):

    if not is_admin():

        return redirect(url_for('index'))

    user_delete = User.query.get_or_404(id)

    db.session.delete(user_delete)

    db.session.commit()

    return redirect(url_for('admin_users'))

# =========================
# RUN
# =========================

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
