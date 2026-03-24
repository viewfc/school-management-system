import os
import sqlite3
from functools import wraps
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'school.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-secret-key')
app.config['DATABASE'] = DATABASE


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    schema_path = os.path.join(BASE_DIR, 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())

    admin = db.execute('SELECT id FROM users WHERE email = ?', ('admin@school.local',)).fetchone()
    if admin is None:
        db.execute(
            '''
            INSERT INTO users (full_name, email, password_hash, role, phone, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                'System Administrator',
                'admin@school.local',
                generate_password_hash('admin123'),
                'admin',
                '000-000-0000',
                'Administration',
            ),
        )

    announcement = db.execute('SELECT id FROM announcements LIMIT 1').fetchone()
    if announcement is None:
        db.execute(
            'INSERT INTO announcements (title, content) VALUES (?, ?)',
            (
                'Welcome to School Management System',
                'Use this starter project to manage users, classes, and school announcements.',
            ),
        )

    db.commit()
    db.close()


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)

    return wrapped_view


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if session.get('role') not in allowed_roles:
                flash('You are not allowed to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


@app.context_processor
def inject_user():
    return {'current_user': current_user()}


@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '')
        phone = request.form.get('phone', '').strip()
        grade_level = request.form.get('grade_level', '').strip()
        section = request.form.get('section', '').strip()
        department = request.form.get('department', '').strip()

        if not full_name or not email or not password:
            flash('Full name, email, and password are required.', 'danger')
            return render_template('register.html')

        if role not in ('teacher', 'student'):
            flash('Only teacher and student accounts can be created from the register page.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Password and confirm password do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        db = get_db()
        existing_user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            flash('This email is already registered.', 'warning')
            return render_template('register.html')

        db.execute(
            '''
            INSERT INTO users (full_name, email, password_hash, role, phone, grade_level, section, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                full_name,
                email,
                generate_password_hash(password),
                role,
                phone,
                grade_level if role == 'student' else None,
                section if role == 'student' else None,
                department if role == 'teacher' else None,
            ),
        )
        db.commit()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_db().execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        session.clear()
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        flash(f"Welcome back, {user['full_name']}!", 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user = current_user()
    announcements = db.execute(
        'SELECT * FROM announcements ORDER BY created_at DESC LIMIT 5'
    ).fetchall()

    context = {
        'user': user,
        'announcements': announcements,
    }

    if user['role'] == 'admin':
        stats = {
            'total_users': db.execute('SELECT COUNT(*) AS total FROM users').fetchone()['total'],
            'total_students': db.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'student'").fetchone()['total'],
            'total_teachers': db.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'teacher'").fetchone()['total'],
            'total_classes': db.execute('SELECT COUNT(*) AS total FROM classes').fetchone()['total'],
        }
        recent_users = db.execute(
            'SELECT * FROM users ORDER BY created_at DESC LIMIT 5'
        ).fetchall()
        recent_classes = db.execute(
            '''
            SELECT c.*, u.full_name AS teacher_name
            FROM classes c
            LEFT JOIN users u ON u.id = c.teacher_id
            ORDER BY c.created_at DESC
            LIMIT 5
            '''
        ).fetchall()
        context.update({'stats': stats, 'recent_users': recent_users, 'recent_classes': recent_classes})

    elif user['role'] == 'teacher':
        teacher_classes = db.execute(
            '''
            SELECT c.*, u.full_name AS teacher_name
            FROM classes c
            LEFT JOIN users u ON u.id = c.teacher_id
            WHERE c.teacher_id = ?
            ORDER BY c.created_at DESC
            ''',
            (user['id'],),
        ).fetchall()
        context.update({'teacher_classes': teacher_classes})

    elif user['role'] == 'student':
        student_profile = {
            'grade_level': user['grade_level'] or '-',
            'section': user['section'] or '-',
            'phone': user['phone'] or '-',
        }
        classes = db.execute(
            '''
            SELECT c.*, u.full_name AS teacher_name
            FROM classes c
            LEFT JOIN users u ON u.id = c.teacher_id
            ORDER BY c.created_at DESC
            LIMIT 6
            '''
        ).fetchall()
        context.update({'student_profile': student_profile, 'classes': classes})

    return render_template('dashboard.html', **context)


@app.route('/users', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def users_page():
    db = get_db()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '')
        phone = request.form.get('phone', '').strip()
        grade_level = request.form.get('grade_level', '').strip()
        section = request.form.get('section', '').strip()
        department = request.form.get('department', '').strip()

        if not full_name or not email or not password or role not in ('admin', 'teacher', 'student'):
            flash('Please complete the form and choose a valid role.', 'danger')
            return redirect(url_for('users_page'))

        existing_user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            flash('Email already exists.', 'warning')
            return redirect(url_for('users_page'))

        db.execute(
            '''
            INSERT INTO users (full_name, email, password_hash, role, phone, grade_level, section, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                full_name,
                email,
                generate_password_hash(password),
                role,
                phone,
                grade_level if role == 'student' else None,
                section if role == 'student' else None,
                department if role in ('teacher', 'admin') else None,
            ),
        )
        db.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('users_page'))

    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    return render_template('users.html', users=users)


@app.post('/users/<int:user_id>/delete')
@login_required
@role_required('admin')
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete your own account while logged in.', 'warning')
        return redirect(url_for('users_page'))

    db = get_db()
    db.execute('UPDATE classes SET teacher_id = NULL WHERE teacher_id = ?', (user_id,))
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    flash('User deleted successfully.', 'info')
    return redirect(url_for('users_page'))


@app.route('/classes', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def classes_page():
    db = get_db()

    if request.method == 'POST':
        class_name = request.form.get('class_name', '').strip()
        subject_name = request.form.get('subject_name', '').strip()
        room = request.form.get('room', '').strip()
        schedule = request.form.get('schedule', '').strip()
        teacher_id = request.form.get('teacher_id', '').strip()
        teacher_id = int(teacher_id) if teacher_id else None

        if not class_name or not subject_name:
            flash('Class name and subject are required.', 'danger')
            return redirect(url_for('classes_page'))

        db.execute(
            '''
            INSERT INTO classes (class_name, subject_name, room, schedule, teacher_id)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (class_name, subject_name, room, schedule, teacher_id),
        )
        db.commit()
        flash('Class created successfully.', 'success')
        return redirect(url_for('classes_page'))

    teachers = db.execute(
        "SELECT id, full_name FROM users WHERE role = 'teacher' ORDER BY full_name ASC"
    ).fetchall()
    classes = db.execute(
        '''
        SELECT c.*, u.full_name AS teacher_name
        FROM classes c
        LEFT JOIN users u ON u.id = c.teacher_id
        ORDER BY c.created_at DESC
        '''
    ).fetchall()
    return render_template('classes.html', classes=classes, teachers=teachers)


@app.post('/classes/<int:class_id>/delete')
@login_required
@role_required('admin')
def delete_class(class_id):
    db = get_db()
    db.execute('DELETE FROM classes WHERE id = ?', (class_id,))
    db.commit()
    flash('Class deleted successfully.', 'info')
    return redirect(url_for('classes_page'))


@app.route('/announcements', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def announcements_page():
    db = get_db()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('announcements_page'))

        db.execute(
            'INSERT INTO announcements (title, content) VALUES (?, ?)',
            (title, content),
        )
        db.commit()
        flash('Announcement published successfully.', 'success')
        return redirect(url_for('announcements_page'))

    announcements = db.execute(
        'SELECT * FROM announcements ORDER BY created_at DESC'
    ).fetchall()
    return render_template('announcements.html', announcements=announcements)


@app.post('/announcements/<int:announcement_id>/delete')
@login_required
@role_required('admin')
def delete_announcement(announcement_id):
    db = get_db()
    db.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
    db.commit()
    flash('Announcement deleted successfully.', 'info')
    return redirect(url_for('announcements_page'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    init_db()
