import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room
from werkzeug.utils import secure_filename

# -------------------- APP CONFIG --------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ✅ FIX: Remove eventlet dependency
socketio = SocketIO(app, async_mode='eventlet')

# -------------------- DATABASE MODEL --------------------
class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50))
    filename = db.Column(db.String(200))
    filetype = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)
    scheduled_time = db.Column(db.DateTime, nullable=True)
    expire_date = db.Column(db.DateTime, nullable=True)

# -------------------- HELPERS --------------------
def get_file_type(filename):
    return filename.split('.')[-1].lower()

def save_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    return render_template('index.html')

# ---------------- AUTH ----------------
users = {}

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users[request.form['username']] = request.form['password']
        flash("Signup successful")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if users.get(request.form['username']) == request.form['password']:
            session['username'] = request.form['username']
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    departments = ['cse', 'it', 'ece', 'mech']
    return render_template('dashboard.html', departments=departments)

# ---------------- DEPARTMENT LOGIN ----------------
@app.route('/department/<dept>', methods=['GET', 'POST'])
def department(dept):
    if request.method == 'POST':
        if request.form['admin_pass'] == f"{dept}@22":
            return redirect(url_for('admin', dept=dept))
        flash("Wrong password")
    return render_template('department.html', department=dept)

# ---------------- ADMIN PANEL ----------------
@app.route('/admin/<dept>', methods=['GET', 'POST'])
def admin(dept):
    if request.method == 'POST':
        file = request.files['file']
        expire_date = request.form.get('expire_date')

        filename = save_file(file)
        filetype = get_file_type(filename)

        notice = Notice(
            department=dept,
            filename=filename,
            filetype=filetype,
            expire_date=datetime.strptime(expire_date, "%Y-%m-%d") if expire_date else None
        )

        db.session.add(notice)
        db.session.commit()

        socketio.emit('new_notice', {
            "id": notice.id,
            "filename": filename,
            "filetype": filetype
        }, room=dept)

        return redirect(url_for('admin', dept=dept))

    immediate = Notice.query.filter_by(department=dept, scheduled_time=None).all()
    prescheduled = Notice.query.filter(Notice.department==dept, Notice.scheduled_time != None).all()

    return render_template('admin.html',
                           department=dept,
                           immediate_notices=[(n.id, n.department, n.filename, n.filetype) for n in immediate],
                           prescheduled_notices=[(n.id, n.department, n.filename, n.filetype) for n in prescheduled])

# ---------------- SCHEDULE NOTICE ----------------
@app.route('/schedule/<dept>', methods=['GET', 'POST'])
def schedule_notice(dept):
    if request.method == 'POST':
        file = request.files['file']
        date = request.form['date']
        time = request.form['time']
        ampm = request.form['ampm']
        expire_date = request.form.get('expire_date')

        filename = save_file(file)
        filetype = get_file_type(filename)

        hour, minute = map(int, time.split(":"))
        if ampm == "PM" and hour != 12:
            hour += 12

        scheduled_time = datetime.strptime(date, "%Y-%m-%d").replace(hour=hour, minute=minute)

        notice = Notice(
            department=dept,
            filename=filename,
            filetype=filetype,
            scheduled_time=scheduled_time,
            expire_date=datetime.strptime(expire_date, "%Y-%m-%d") if expire_date else None
        )

        db.session.add(notice)
        db.session.commit()

        socketio.emit('new_prescheduled_notice', {
            "id": notice.id,
            "filename": filename,
            "filetype": filetype,
            "scheduled_time": scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
        }, room=dept)

        return redirect(url_for('admin', dept=dept))

    return render_template('schedule_notice.html', department=dept)

# ---------------- PUBLIC VIEW ----------------
@app.route('/public/<dept>')
def public(dept):
    now = datetime.now()

    notices = Notice.query.filter_by(department=dept).all()

    valid = []
    for n in notices:
        if n.scheduled_time and n.scheduled_time > now:
            continue
        if n.expire_date and n.expire_date < now:
            continue
        valid.append((n.id, n.department, n.filename, n.filetype))

    return render_template('public.html', department=dept, notices=valid)

# ---------------- SLIDESHOW ----------------
@app.route('/slideshow/<dept>')
def slideshow(dept):
    now = datetime.now()

    notices = Notice.query.filter_by(department=dept).all()

    valid = []
    for n in notices:
        if n.scheduled_time and n.scheduled_time > now:
            continue
        if n.expire_date and n.expire_date < now:
            continue
        valid.append((n.id, n.department, n.filename, n.filetype))

    return render_template('slideshow.html', department=dept, notices=valid)

# ---------------- DELETE ----------------
@app.route('/delete_notice/<int:id>')
def delete_notice(id):
    notice = Notice.query.get(id)
    if notice:
        dept = notice.department
        db.session.delete(notice)
        db.session.commit()

        socketio.emit('delete_notice', {"id": id}, room=dept)

    return redirect(request.referrer or '/')

@app.route('/delete_all/<dept>', methods=['POST'])
def delete_all_notices(dept):
    Notice.query.filter_by(department=dept).delete()
    db.session.commit()

    socketio.emit('delete_notice', {"all": True}, room=dept)

    return redirect(url_for('admin', dept=dept))

# ---------------- FILE SERVE ----------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------- SOCKET ----------------
@socketio.on('join')
def on_join(room):
    join_room(room)

# ---------------- INIT DB ----------------
with app.app_context():
    db.create_all()

# ---------------- RUN ----------------
if __name__ == "__main__":
    socketio.run(app, debug=True)