"""
सिध्द गौतम को-ऑप हौसिंग सोसायटी मॅनेजमेंट सिस्टम
Flask मुख्य ऍप्लिकेशन फाईल
Developer: श्री. राजेश भालेराव
"""

import os

AI_ENABLED = False
model = None

try:
    from google.genai import Client
    # We just initialize the client to verify connectivity
    client = Client(api_key=os.getenv("GOOGLE_API_KEY"))
    AI_ENABLED = True
    print("🤖 AI Features Enabled (Gemini Connected)")
except Exception as e:
    print("⚠️ AI Features Disabled:", e)

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps

# AI Helper Import
try:
    from ai_helper import SocietyAI
    ai_assistant = SocietyAI()
    print("🤖 AI Features Enabled")
except Exception as e:
    ai_assistant = None
    print(f"⚠️ AI Features Disabled: {e}")

# Flask ऍप्लिकेशन इनिशियलाईझ करा
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SECRET_KEY'] = 'sidda-goutam-society-2025-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///society.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from werkzeug.utils import secure_filename
import uuid

# इमेज अपलोडसाठी फोल्डर कॉन्फिगरेशन
app.config['UPLOAD_FOLDER_DIRECTORS'] = os.path.join('app/static/uploads/directors')
app.config['UPLOAD_FOLDER_PMC'] = os.path.join('app/static/uploads/pmc')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file, folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # युनिक नाव द्या जेणेकरून फाईल्स ओव्हरराईट होणार नाहीत
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, unique_filename))
        return unique_filename
    return 'default_user.png'

# डेटाबेस इनिशियलाईझ करा
db = SQLAlchemy(app)

# =====================================================
# DATABASE MODELS (डेटाबेस मॉडेल्स)
# =====================================================

class Member(db.Model):
    """सोसायटी मेंबर मॉडेल"""
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    building_no = db.Column(db.String(50), nullable=False)
    flat_no = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    complaints = db.relationship('Complaint', backref='member', lazy=True)
    login_history = db.relationship('LoginHistory', backref='member', lazy=True)
    questions = db.relationship('Question', backref='member', lazy=True)

    @property
    def avatar_char(self):
        """अवतारसाठी पहिले इंग्रजी आद्याक्षर मिळवा (Fix)"""
        import re
        # युजरनेम किंवा नावातील पहिले इंग्रजी अक्षर शोधा
        match = re.search(r'[a-zA-Z]', self.name)
        if match:
            return match.group().upper()
        match = re.search(r'[a-zA-Z]', self.username)
        if match:
            return match.group().upper()
        return self.name[0] if self.name else 'U'

class Director(db.Model):
    """संचालक मंडळ मॉडेल (director_board)"""
    __tablename__ = 'director_board'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    photo = db.Column(db.String(300), default='default_user.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PMCCommittee(db.Model):
    """पी.एम.सी समिती मॉडेल (pmc_committee)"""
    __tablename__ = 'pmc_committee'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    building_no = db.Column(db.String(50), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    photo = db.Column(db.String(300), default='default_user.png')
    role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notice(db.Model):
    """सूचना मॉडेल"""
    __tablename__ = 'notices'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Complaint(db.Model):
    """तक्रार मॉडेल"""
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='प्रलंबित')
    admin_reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime)
    
    # AI Classification Fields
    ai_category = db.Column(db.String(100))  # AI द्वारे ओळखलेला प्रकार
    ai_priority = db.Column(db.String(50))   # AI प्राधान्यता
    ai_sentiment = db.Column(db.String(50))  # AI भावना विश्लेषण
    ai_suggested_reply = db.Column(db.Text)  # AI सुचवलेले उत्तर

class Document(db.Model):
    """दस्तऐवज मॉडेल़"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(300), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)  # minutes, notice, certificate
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class RedevelopmentUpdate(db.Model):
    """रिडेव्हलपमेंट अपडेट मॉडेल"""
    __tablename__ = 'redevelopment_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    progress_percentage = db.Column(db.Integer, default=0)
    update_date = db.Column(db.DateTime, default=datetime.utcnow)

class RedevelopmentInfo(db.Model):
    """रिडेव्हलपमेंट सविस्तर माहिती मॉडेल"""
    __tablename__ = 'redevelopment_info'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_admin = db.Column(db.Integer, default=0)

class LoginHistory(db.Model):
    """लॉगिन इतिहास मॉडेल"""
    __tablename__ = 'login_history'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    username = db.Column(db.String(80), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)
    ip_address = db.Column(db.String(50))

# =====================================================
# AI ASSISTANT MODELS (AI असिस्टंट मॉडेल्स)
# =====================================================

class AIKnowledge(db.Model):
    """AI ज्ञान भांडार मॉडेल (Trained Data)"""
    __tablename__ = 'ai_knowledge'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False) # नियम, मेंटेनन्स, रिडेव्हलपमेंट, कायदेशीर
    question_pattern = db.Column(db.Text, nullable=False) # प्रश्न किंवा कीवर्ड्स
    answer = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(200)) # Bye-laws, Meeting Minutes, etc.
    priority = db.Column(db.Integer, default=1) # High=3, Medium=2, Low=1
    status = db.Column(db.String(50), default='Approved') # Approved, Pending, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIInteraction(db.Model):
    """AI संवाद इतिहास मॉडEL"""
    __tablename__ = 'ai_interactions'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True) # Null for Admin or Guest if any
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    response_type = db.Column(db.String(50)) # Approved_DB, Legal_KB, AI_Gen, Not_Found
    category_tag = db.Column(db.String(100))
    sentiment = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_safe = db.Column(db.Boolean, default=True)
    feedback_score = db.Column(db.Integer) # 1 to 5

class AITrainingRequest(db.Model):
    """Admin कडे पाठवलेले अनुत्तरित प्रश्न"""
    __tablename__ = 'ai_training_requests'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    asked_by_member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    status = db.Column(db.String(50), default='New') # New, Training, Completed
    suggested_answer = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    """सदस्यांचे प्रश्न (Questions) मॉडेल"""
    __tablename__ = 'member_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='प्रलंबित')
    
    # Relationship for replies
    replies = db.relationship('Reply', backref='question', lazy=True, cascade="all, delete-orphan")

class Reply(db.Model):
    """अॅडमिनची उत्तरे (Replies) मॉडेल"""
    __tablename__ = 'admin_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('member_questions.id'), nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    reply_date = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, default=0) # 0 for default admin

# =====================================================
# AUTHENTICATION DECORATORS (प्रमाणीकरण डेकोरेटर्स)
# =====================================================

def login_required(f):
    """लॉगिन आवश्यक डेकोरेटर"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('कृपया प्रथम लॉगिन करा', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """अॅडमिन आवश्यक डेकोरेटर"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('या पृष्ठासाठी अॅडमिन परवानगी आवश्यक आहे', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# PUBLIC ROUTES (सार्वजनिक रूट्स)
# =====================================================

@app.route('/')
def index():
    """मुख्य पृष्ठ"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('member_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """नवीन सदस्य नोंदणी"""
    if request.method == 'POST':
        name = request.form.get('name')
        building_no = request.form.get('building_no')
        flat_no = request.form.get('flat_no')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # युजरनेम आधीच अस्तित्वात आहे का तपासा
        existing_user = Member.query.filter_by(username=username).first()
        if existing_user:
            flash('हे युजरनेम आधीच वापरात आहे', 'danger')
            return redirect(url_for('register'))
        
        # ईमेल आधीच अस्तित्वात आहे का तपासा
        existing_email = Member.query.filter_by(email=email).first()
        if existing_email:
            flash('हा ईमेल आधीच नोंदणीकृत आहे', 'danger')
            return redirect(url_for('register'))
        
        # नवीन सदस्य तयार करा
        hashed_password = generate_password_hash(password)
        new_member = Member(
            name=name,
            building_no=building_no,
            flat_no=flat_no,
            email=email,
            mobile=mobile,
            username=username,
            password=hashed_password
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        flash('नोंदणी यशस्वी! आता तुम्ही लॉगिन करू शकता', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """लॉगिन पृष्ठ"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # अॅडमिन लॉगिन तपासा
        if username == 'admin' and password == '123':
            session['user_id'] = 0
            session['username'] = 'admin'
            session['role'] = 'admin'
            
            # लॉगिन इतिहास जतन करा
            login_record = LoginHistory(
                username='admin',
                ip_address=request.remote_addr
            )
            db.session.add(login_record)
            db.session.commit()
            session['login_history_id'] = login_record.id
            
            flash('अॅडमिन लॉगिन यशस्वी!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # सदस्य लॉगिन तपासा
        member = Member.query.filter_by(username=username).first()
        if member and check_password_hash(member.password, password):
            if not member.is_active:
                flash('तुमचे खाते निष्क्रिय आहे. कृपया अॅडमिनशी संपर्क साधा', 'danger')
                return redirect(url_for('login'))
            
            session['user_id'] = member.id
            session['username'] = member.username
            session['name'] = member.name
            session['role'] = 'member'
            
            # लॉगिन इतिहास जतन करा
            login_record = LoginHistory(
                member_id=member.id,
                username=username,
                ip_address=request.remote_addr
            )
            db.session.add(login_record)
            db.session.commit()
            session['login_history_id'] = login_record.id
            
            flash(f'स्वागत आहे, {member.name}!', 'success')
            return redirect(url_for('member_dashboard'))
        
        flash('चुकीचे युजरनेम किंवा पासवर्ड', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """लॉगआउट"""
    # लॉगआउट वेळ अपडेट करा
    if 'login_history_id' in session:
        login_record = LoginHistory.query.get(session['login_history_id'])
        if login_record:
            login_record.logout_time = datetime.utcnow()
            db.session.commit()
    
    session.clear()
    flash('तुम्ही यशस्वीरित्या लॉगआउट झाला आहात', 'info')
    return redirect(url_for('index'))

# =====================================================
# MEMBER ROUTES (सदस्य रूट्स)
# =====================================================

@app.route('/member/dashboard')
@login_required
def member_dashboard():
    """सदस्य डॅशबोर्ड"""
    notices = Notice.query.filter_by(is_active=True).order_by(Notice.created_at.desc()).limit(5).all()
    directors = Director.query.order_by(Director.id).all()
    redevelopment = RedevelopmentUpdate.query.order_by(RedevelopmentUpdate.update_date.desc()).first()
    
    return render_template('member/dashboard.html', 
                         notices=notices, 
                         directors=directors,
                         redevelopment=redevelopment)

@app.route('/member/profile')
@login_required
def member_profile():
    """सदस्य प्रोफाइल पहाणे"""
    member = Member.query.get(session['user_id'])
    questions = Question.query.filter_by(member_id=session['user_id']).order_by(Question.question_date.desc()).all()
    return render_template('member/profile.html', member=member, questions=questions)

@app.route('/member/profile/update', methods=['POST'])
@login_required
def update_profile():
    """प्रोफाईल माहिती अपडेट करणे"""
    member = Member.query.get(session['user_id'])
    member.name = request.form.get('name')
    member.building_no = request.form.get('building_no')
    member.flat_no = request.form.get('flat_no')
    member.email = request.form.get('email')
    member.mobile = request.form.get('mobile')
    member.username = request.form.get('username')
    
    db.session.commit()
    flash('तुमची माहिती यशस्वीरित्या अपडेट झाली आहे!', 'success')
    return redirect(url_for('member_profile'))

@app.route('/member/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """पासवर्ड बदलणे"""
    member = Member.query.get(session['user_id'])
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password == confirm_password:
        member.password = generate_password_hash(new_password)
        db.session.commit()
        flash('पासवर्ड यशस्वीरित्या बदलला आहे!', 'success')
    else:
        flash('पासवर्ड मॅच झाले नाहीत!', 'danger')
        
    return redirect(url_for('member_profile'))

@app.route('/member/profile/ask-question', methods=['POST'])
@login_required
def ask_question():
    """नवीन प्रश्न विचारणे"""
    question_text = request.form.get('question_text')
    if question_text:
        new_q = Question(
            member_id=session['user_id'],
            question_text=question_text
        )
        db.session.add(new_q)
        db.session.commit()
        flash('तुमचा प्रश्न अॅडमिनला पाठवला गेला आहे.', 'success')
    return redirect(url_for('member_profile'))

@app.route('/member/complaints', methods=['GET', 'POST'])
@login_required
def member_complaints():
    """सदस्य तक्रारी"""
    if request.method == 'POST':
        subject = request.form.get('subject')
        description = request.form.get('description')
        
        complaint = Complaint(
            member_id=session['user_id'],
            subject=subject,
            description=description
        )
        
        # AI Classification (if enabled)
        if ai_assistant:
            try:
                ai_result = ai_assistant.classify_complaint(subject, description)
                complaint.ai_category = ai_result.get('category', 'सामान्य')
                complaint.ai_priority = ai_result.get('priority', 'मध्यम')
                complaint.ai_sentiment = ai_result.get('sentiment', 'तटस्थ')
                
                # Generate AI suggested reply
                suggested_reply = ai_assistant.suggest_reply(subject, description, complaint.ai_category)
                complaint.ai_suggested_reply = suggested_reply
                
                flash(f'तक्रार नोंदवली गेली (AI वर्गीकरण: {complaint.ai_category})', 'success')
            except Exception as e:
                print(f"AI Error: {e}")
                flash('तक्रार नोंदवली गेली', 'success')
        else:
            flash('तक्रार नोंदवली गेली', 'success')
        
        db.session.add(complaint)
        db.session.commit()
        
        return redirect(url_for('member_complaints'))
    
    complaints = Complaint.query.filter_by(member_id=session['user_id']).order_by(Complaint.created_at.desc()).all()
    return render_template('member/complaints.html', complaints=complaints)

@app.route('/member/notices')
@login_required
def member_notices():
    """सूचना फलक"""
    notices = Notice.query.filter_by(is_active=True).order_by(Notice.created_at.desc()).all()
    return render_template('member/notices.html', notices=notices)

@app.route('/member/redevelopment')
@login_required
def member_redevelopment():
    """रिडेव्हलपमेंट"""
    info = RedevelopmentInfo.query.first()
    updates = RedevelopmentUpdate.query.order_by(RedevelopmentUpdate.update_date.desc()).all()
    return render_template('member/redevelopment.html', info=info, updates=updates)

@app.route('/member/documents')
@login_required
def member_documents():
    """दस्तऐवज"""
    documents = Document.query.order_by(Document.uploaded_at.desc()).all()
    return render_template('member/documents.html', documents=documents)

@app.route('/document/download/<int:id>')
@login_required
def download_document(id):
    """दस्तऐवज डाउनलोड करा"""
    document = Document.query.get_or_404(id)
    upload_path = os.path.join(app.root_path, 'static/uploads/documents')
    file_path = os.path.join(upload_path, document.filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('फाईल सापडली नाही!', 'danger')
        return redirect(request.referrer)

# =====================================================
# ADMIN ROUTES (अॅडमिन रूट्स)
# =====================================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """प्रोफेशनल ॲडमिन डॅशबोर्ड"""
    stats = {
        'total_members': Member.query.count(),
        'active_members': Member.query.filter_by(is_active=True).count(),
        'pending_complaints': Complaint.query.filter(Complaint.status != 'Closed').count(),
        'total_notices': Notice.query.count(),
        'pending_questions': Question.query.filter_by(status='प्रलंबित').count()
    }
    
    # Check if redevelopment info exists for first time
    if not RedevelopmentInfo.query.first():
        sample_info = RedevelopmentInfo(
            title="सिध्द गौतम को-ऑप हौसिंग सोसायटी रिडेव्हलपमेंट माहिती",
            details="आमच्या सोसायटीच्या पुनर्विकासाचे काम प्रगतीपथावर आहे. सर्व सभासदांना विनंती आहे की त्यांनी अद्ययावत माहितीसाठी हा विभाग तपासावा."
        )
        db.session.add(sample_info)
        db.session.commit()
    
    recent_activity = LoginHistory.query.order_by(LoginHistory.login_time.desc()).limit(10).all()
    members = Member.query.all()
    return render_template('admin/dashboard.html', stats=stats, activity=recent_activity, members=members)

@app.route('/admin/login-activity')
@admin_required
def admin_login_activity():
    """सर्व सदस्यांची अलीकडील लॉगिन कृती पाहणे (Admin Only) with Filters"""
    role = request.args.get('role', 'all')
    time_filter = request.args.get('time', 'all')
    search = request.args.get('search', '')

    query = LoginHistory.query

    # Role Filter
    if role == 'admin':
        query = query.filter(LoginHistory.username == 'admin')
    elif role == 'member':
        query = query.filter(LoginHistory.username != 'admin')

    # Time Filter
    now = datetime.utcnow()
    if time_filter == 'today':
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(LoginHistory.login_time >= today_start)
    elif time_filter == 'week':
        week_start = now - timedelta(days=7)
        query = query.filter(LoginHistory.login_time >= week_start)

    # Search
    if search:
        query = query.filter(LoginHistory.username.ilike(f'%{search}%'))

    activities = query.order_by(LoginHistory.login_time.desc()).limit(100).all()
    return render_template('admin/login_activity.html', 
                           activities=activities, 
                           current_role=role, 
                           current_time=time_filter, 
                           search_query=search)

@app.route('/admin/member/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_member_edit(id):
    """सभासद माहिती संपादन (Admin)"""
    member = Member.query.get_or_404(id)
    if request.method == 'POST':
        member.name = request.form.get('name')
        member.email = request.form.get('email')
        member.mobile = request.form.get('mobile')
        member.building_no = request.form.get('building_no')
        member.flat_no = request.form.get('flat_no')
        db.session.commit()
        flash('सभासदाची माहिती अपडेट झाली!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_member.html', member=member)

@app.route('/admin/notice/send-specific', methods=['POST'])
@admin_required
def send_specific_notice():
    """विशिष्ट सभासदाला सूचना देणे"""
    member_id = request.form.get('member_id')
    title = request.form.get('title')
    content = f"वैयक्तिक सूचना: {request.form.get('content')}"
    
    # सध्या आपण साध्या नोटीसमध्येच सेव्ह करत आहोत, 
    # भविष्यात यासाठी वेगळे 'Notification' टेबल वापरता येईल.
    notice = Notice(title=title, content=f"(For ID: {member_id}) {content}")
    db.session.add(notice)
    db.session.commit()
    flash('वैयक्तिक सूचना पाठवली गेली!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/members')
@admin_required
def admin_members():
    """सदस्य यादी"""
    members = Member.query.order_by(Member.created_at.desc()).all()
    return render_template('admin/members.html', members=members)

@app.route('/admin/member/toggle/<int:id>')
@admin_required
def admin_member_toggle(id):
    """सदस्य सक्रिय/निष्क्रिय करा"""
    member = Member.query.get_or_404(id)
    member.is_active = not member.is_active
    db.session.commit()
    
    status = 'सक्रिय' if member.is_active else 'निष्क्रिय'
    flash(f'सदस्य {status} केला', 'success')
    return redirect(url_for('admin_members'))



@app.route('/admin/notices', methods=['GET', 'POST'])
@admin_required
def admin_notices():
    """सूचना व्यवस्थापन"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_active = request.form.get('status') == 'active'
        created_at_str = request.form.get('publish_date')
        
        notice = Notice(title=title, content=content, is_active=is_active)
        
        if created_at_str:
            try:
                notice.created_at = datetime.strptime(created_at_str, '%Y-%m-%d')
            except:
                pass
                
        db.session.add(notice)
        db.session.commit()
        
        flash('नवीन सूचना यशस्वीरित्या जोडली गेली!', 'success')
        return redirect(url_for('admin_notices'))
    
    notices = Notice.query.order_by(Notice.created_at.desc()).all()
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/notices.html', notices=notices, today_date=today_date)

@app.route('/admin/notice/edit/<int:id>', methods=['POST'])
@admin_required
def admin_notice_edit(id):
    """सूचना सुधारणे (Edit)"""
    notice = Notice.query.get_or_404(id)
    notice.title = request.form.get('title')
    notice.content = request.form.get('content')
    notice.is_active = request.form.get('status') == 'active'
    
    publish_date = request.form.get('publish_date')
    if publish_date:
        try:
            notice.created_at = datetime.strptime(publish_date, '%Y-%m-%d')
        except:
            pass
            
    db.session.commit()
    flash('सूचना यशस्वीरित्या सुधारली गेली!', 'success')
    return redirect(url_for('admin_notices'))

@app.route('/admin/notice/delete/<int:id>')
@admin_required
def admin_notice_delete(id):
    """सूचना हटवा"""
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()
    
    flash('सूचना हटवली गेली', 'success')
    return redirect(url_for('admin_notices'))

@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    """तक्रार व्यवस्थापन"""
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    return render_template('admin/complaints.html', complaints=complaints)

@app.route('/admin/complaint/reply/<int:id>', methods=['POST'])
@admin_required
def admin_complaint_reply(id):
    """तक्रारीला उत्तर द्या"""
    complaint = Complaint.query.get_or_404(id)
    complaint.admin_reply = request.form.get('reply')
    complaint.status = 'उत्तर दिले'
    complaint.replied_at = datetime.utcnow()
    db.session.commit()
    
    flash('उत्तर जतन केले', 'success')
    return redirect(url_for('admin_complaints'))

# =====================================================
# BOARD & PMC ROUTES (ADMIN)
# =====================================================

@app.route('/admin/dashboard/director-board', methods=['GET', 'POST'])
@admin_required
def admin_director_board():
    """संचालक मंडळ व्यवस्थापन (Admin)"""
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        mobile = request.form.get('mobile')
        photo_file = request.files.get('photo')
        
        photo_name = 'default_user.png'
        if photo_file:
            photo_name = save_uploaded_image(photo_file, app.config['UPLOAD_FOLDER_DIRECTORS'])
            
        director = Director(name=name, position=position, mobile=mobile, photo=photo_name)
        db.session.add(director)
        db.session.commit()
        flash('संचालक यशस्वीरित्या जोडला गेला!', 'success')
        return redirect(url_for('admin_director_board'))
        
    directors = Director.query.order_by(Director.id).all()
    return render_template('admin/director_board.html', directors=directors)

@app.route('/admin/dashboard/director/delete/<int:id>')
@admin_required
def delete_director(id):
    director = Director.query.get_or_404(id)
    db.session.delete(director)
    db.session.commit()
    flash('संचालक हटवण्यात आला!', 'info')
    return redirect(url_for('admin_director_board'))

@app.route('/admin/dashboard/director/edit/<int:id>', methods=['POST'])
@admin_required
def edit_director(id):
    director = Director.query.get_or_404(id)
    director.name = request.form.get('name')
    director.position = request.form.get('position')
    director.mobile = request.form.get('mobile')
    
    photo_file = request.files.get('photo')
    if photo_file:
        director.photo = save_uploaded_image(photo_file, app.config['UPLOAD_FOLDER_DIRECTORS'])
        
    db.session.commit()
    flash('संचालक माहिती अद्ययावत केली!', 'success')
    return redirect(url_for('admin_director_board'))

@app.route('/admin/dashboard/pmc', methods=['GET', 'POST'])
@admin_required
def admin_pmc():
    """पी.एम.सी समिती व्यवस्थापन (Admin)"""
    if request.method == 'POST':
        name = request.form.get('name')
        building_no = request.form.get('building_no')
        mobile = request.form.get('mobile')
        role = request.form.get('role')
        photo_file = request.files.get('photo')
        
        photo_name = 'default_user.png'
        if photo_file:
            photo_name = save_uploaded_image(photo_file, app.config['UPLOAD_FOLDER_PMC'])
            
        pmc = PMCCommittee(name=name, building_no=building_no, mobile=mobile, role=role, photo=photo_name)
        db.session.add(pmc)
        db.session.commit()
        flash('PMC सदस्य यशस्वीरित्या जोडला गेला!', 'success')
        return redirect(url_for('admin_pmc'))
        
    pmc_members = PMCCommittee.query.order_by(PMCCommittee.id).all()
    return render_template('admin/pmc.html', members=pmc_members)

@app.route('/admin/dashboard/pmc/delete/<int:id>')
@admin_required
def delete_pmc(id):
    pmc = PMCCommittee.query.get_or_404(id)
    db.session.delete(pmc)
    db.session.commit()
    flash('PMC सदस्य हटवण्यात आला!', 'info')
    return redirect(url_for('admin_pmc'))

@app.route('/admin/dashboard/pmc/edit/<int:id>', methods=['POST'])
@admin_required
def edit_pmc(id):
    pmc = PMCCommittee.query.get_or_404(id)
    pmc.name = request.form.get('name')
    pmc.building_no = request.form.get('building_no')
    pmc.mobile = request.form.get('mobile')
    pmc.role = request.form.get('role')
    
    photo_file = request.files.get('photo')
    if photo_file:
        pmc.photo = save_uploaded_image(photo_file, app.config['UPLOAD_FOLDER_PMC'])
        
    db.session.commit()
    flash('PMC सदस्य माहिती अद्ययावत केली!', 'success')
    return redirect(url_for('admin_pmc'))

@app.route('/admin/redevelopment', methods=['GET', 'POST'])
@admin_required
def admin_redevelopment():
    """रिडेव्हलपमेंट माहिती व प्रश्नोत्तरे व्यवस्थापन (Admin)"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            title = request.form.get('redevelopment_title')
            details = request.form.get('redevelopment_details')
            
            info = RedevelopmentInfo.query.first()
            if not info:
                info = RedevelopmentInfo(title=title, details=details)
                db.session.add(info)
            else:
                info.title = title
                info.details = details
                info.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('रिडेव्हलपमेंट माहिती यशस्वीरित्या अद्ययावत केली!', 'success')
            
        elif action == 'reply_question':
            q_id = request.form.get('question_id')
            reply_text = request.form.get('reply_text')
            
            question = Question.query.get_or_404(q_id)
            
            # Check for existing reply
            reply = Reply.query.filter_by(question_id=q_id).first()
            if not reply:
                reply = Reply(question_id=q_id, reply_text=reply_text)
                db.session.add(reply)
            else:
                reply.reply_text = reply_text
                reply.reply_date = datetime.utcnow()
            
            question.status = 'उत्तर दिले'
            db.session.commit()
            flash('प्रश्नाचे उत्तर यशस्वीरित्या जतन केले!', 'success')
            
        return redirect(url_for('admin_redevelopment'))
    
    redevelopment_info = RedevelopmentInfo.query.first()
    questions = Question.query.order_by(Question.question_date.desc()).all()
    
    return render_template('admin/admin_redevelopment.html', 
                         info=redevelopment_info, 
                         questions=questions)

@app.route('/admin/documents', methods=['GET', 'POST'])
@admin_required
def admin_documents():
    """अॅडमिन दस्तऐवज व्यवस्थापन"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        doc_type = request.form.get('doc_type')
        file = request.files.get('document')
        
        if file and file.filename != '':
            os.makedirs(os.path.join('app/static/uploads/documents'), exist_ok=True)
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file.save(os.path.join('app/static/uploads/documents', unique_filename))
            
            new_doc = Document(
                title=title,
                description=description,
                filename=unique_filename,
                doc_type=doc_type
            )
            db.session.add(new_doc)
            db.session.commit()
            flash('दस्तऐवज यशस्वीरित्या अपलोड झाला!', 'success')
        else:
            flash('कृपया फाईल निवडा!', 'danger')
            
        return redirect(url_for('admin_documents'))
        
    documents = Document.query.order_by(Document.uploaded_at.desc()).all()
    return render_template('admin/documents.html', documents=documents)

@app.route('/admin/document/delete/<int:id>')
@admin_required
def admin_document_delete(id):
    """दस्तऐवज हटवा"""
    document = Document.query.get_or_404(id)
    # फाईल सिस्टिम मधून हटवा
    file_path = os.path.join('app/static/uploads/documents', document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    db.session.delete(document)
    db.session.commit()
    flash('दस्तऐवज हटवला गेला!', 'info')
    return redirect(url_for('admin_documents'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """अॅडमिन सेटिंग्स"""
    if request.method == 'POST':
        # सेटिंग्स सेव्ह करण्याची लॉजिक येथे येईल
        # सध्यासाठी फक्त यश संदेश दाखवू
        flash('सेटिंग्स यशस्वीरित्या अपडेट झाल्या!', 'success')
        return redirect(url_for('admin_settings'))
        
    return render_template('admin/settings.html')

@app.route('/admin/view')
@admin_required
def admin_view():
    """अॅडमिन डेटा व्ह्यू (Read-only)"""
    page = request.args.get('page', 1, type=int)
    members = Member.query.order_by(Member.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/admin_view.html', members=members)

# =====================================================
# BOARD & PMC ROUTES (MEMBER)
# =====================================================

@app.route('/member/director-board')
@login_required
def member_director_board():
    """संचालक मंडळ पाहणे (Member)"""
    directors = Director.query.order_by(Director.id).all()
    return render_template('member/director_board.html', directors=directors)

@app.route('/member/pmc')
@login_required
def member_pmc():
    """पी.एम.सी समिती पाहणे (Member)"""
    pmc_members = PMCCommittee.query.order_by(PMCCommittee.id).all()
    return render_template('member/pmc.html', members=pmc_members)

# =====================================================
# AI ASSISTANT API & ROUTES (AI असिस्टंट)
# =====================================================

@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    data = request.json
    user_question = data.get("question", "")

    if not user_question:
        return jsonify({"reply": "कृपया प्रश्न लिहा."})

    # Legal-safe prompt
    system_prompt = f"""
    तू हौसिंग सोसायटीसाठी AI सहाय्यक आहेस.
    उत्तर मराठीत द्यायचे आहे.
    अंतिम कायदेशीर सल्ला देऊ नकोस.
    गरज असल्यास Disclaimer द्यायचा.

    प्रश्न: {user_question}
    """

    try:
        response = model.generate_content(system_prompt)
        answer = response.text

        # Mandatory disclaimer
        answer += "\n\n⚠️ टीप: ही माहिती सामान्य स्वरूपाची आहे. अंतिम निर्णयासाठी तज्ज्ञांचा सल्ला घ्यावा."

        return jsonify({"reply": answer})

    except Exception as e:
        return jsonify({"reply": f"AI उत्तर देऊ शकले नाही. कारण: {str(e)}"})

@app.route('/admin/ai-training')
@admin_required
def admin_ai_training():
    """AI ट्रेनिंग पॅनेल"""
    knowledge = AIKnowledge.query.order_by(AIKnowledge.updated_at.desc()).all()
    requests = AITrainingRequest.query.filter_by(status='New').all()
    stats = {
        'total_knowledge': AIKnowledge.query.count(),
        'pending_requests': AITrainingRequest.query.filter_by(status='New').count(),
        'total_interactions': AIInteraction.query.count()
    }
    return render_template('admin/ai_training.html', knowledge=knowledge, requests=requests, stats=stats)

@app.route('/admin/ai-training/add', methods=['POST'])
@admin_required
def admin_ai_add_knowledge():
    """नवीन ज्ञान जोडणे"""
    category = request.form.get('category')
    question_pattern = request.form.get('question_pattern')
    answer = request.form.get('answer')
    source = request.form.get('source')
    priority = request.form.get('priority', 1)
    
    new_kb = AIKnowledge(
        category=category,
        question_pattern=question_pattern,
        answer=answer,
        source=source,
        priority=priority,
        status='Approved'
    )
    db.session.add(new_kb)
    db.session.commit()
    
    flash('नवीन माहिती AI ज्ञान भांडारात यशस्वीरित्या जोडली गेली!', 'success')
    return redirect(url_for('admin_ai_training'))

@app.route('/admin/ai-training/approve-request/<int:req_id>', methods=['POST'])
@admin_required
def admin_ai_approve_request(req_id):
    """सदस्याच्या प्रश्नाचे उत्तर देऊन जतन करणे"""
    req = AITrainingRequest.query.get_or_404(req_id)
    answer = request.form.get('answer')
    category = request.form.get('category')
    
    # AI Knowledge मध्ये जोडा
    new_kb = AIKnowledge(
        category=category,
        question_pattern=req.question,
        answer=answer,
        status='Approved'
    )
    db.session.add(new_kb)
    
    # रिक्वेस्ट पूर्ण म्हणून मार्क करा
    req.status = 'Completed'
    req.suggested_answer = answer
    
    db.session.commit()
    flash('उत्तर यशस्वीरित्या जतन केले आणि AI ला ट्रेन केले!', 'success')
    return redirect(url_for('admin_ai_training'))

# =====================================================
# DATABASE INITIALIZATION (डेटाबेस इनिशियलायझेशन)
# =====================================================

def init_db():
    """डेटाबेस इनिशियलाईझ करा आणि सॅम्पल डेटा जोडा"""
    with app.app_context():
        db.create_all()
        
        # संचालक मंडळ जोडा (जर नसेल तर)
        if Director.query.count() == 0:
            directors_data = [
                ("श्री. शामराव बाबुराव मोरे", "चेअरमन", "9423557744"),
                ("श्री दिपक भगवानदास मोरे", "सचिव", "9922030401"),
                ("श्री. श्रीकांत विठ्ठल शेरे", "खजिनदार", "8237626246"),
                ("श्री. जिवन बाबुराव वाघ", "सदस्य", "9763439323"),
                ("श्री. त्रंबक सोनु सांगळे", "सदस्य", "8237626246"),
                ("श्री. अमोल मधुकर म्हेमाने", "सदस्य", "9890322301"),
                ("श्री. रुपेश शरद पहाडी", "सदस्य", "9921310205"),
                ("श्री. देविदास तुळशीराम सुर्यवंशी", "सदस्य", "9225117519"),
                ("श्री. सुभाष सोपन भवर", "सदस्य", "901105974"),
                ("सौ. कविता अनिल अंभगे", "सदस्य", "9823776948"),
                ("श्रीमती माधुरी अशोक गांगुर्डे", "सदस्य", "9270619888"),
            ]
            
            for name, position, mobile in directors_data:
                director = Director(name=name, position=position, mobile=mobile)
                db.session.add(director)
            
            db.session.commit()
            print("✅ संचालक मंडळ डेटा जोडला गेला")
        
        # सॅम्पल नोटीस जोडा
        if Notice.query.count() == 0:
            notices_data = [
                ("सोसायटी मासिक सभा", "आगामी मासिक सभा दिनांक १५ जानेवारी २०२५ रोजी संध्याकाळी ६ वाजता होईल. सर्व सदस्यांनी उपस्थित राहावे."),
                ("पाणी पुरवठा बंद", "दिनांक १० जानेवारी २०२५ रोजी सकाळी ८ ते दुपारी २ वाजेपर्यंत पाणी पुरवठा बंद राहील."),
                ("रिडेव्हलपमेंट अपडेट", "रिडेव्हलपमेंट प्रकल्पाची प्रगती ४०% झाली आहे. नवीन अपडेट लवकरच येईल."),
            ]
            
            for title, content in notices_data:
                notice = Notice(title=title, content=content)
                db.session.add(notice)
            
            db.session.commit()
            print("✅ सॅम्पल नोटीस डेटा जोडला गेला")
            
        # सॅम्पल AI Knowledge जोडा
        if AIKnowledge.query.count() == 0:
            ai_data = [
                ('नियम', 'मेंबरशिप हस्तांतरण नियम, शेअर सर्टिफिकेट फी, वारस नोंदणी', 'सोसायटी सभासदत्व हस्तांतरणासाठी ५००/- रुपये प्रवेश फी आणि हस्तांतरण शुल्काची माहिती उपविधी (Bye-laws) कलम ३८ मध्ये दिली आहे.'),
                ('मेंटेनन्स', 'मेंटेनन्स कधी भरायचा, दंड, उशिरा पेमेंट, देखभाल शुल्क', 'सोसायटीचे मासिक मेंटेनन्स बिल दर महिन्याच्या १० तारखेपर्यंत भरणे आवश्यक आहे. उशिरा पेमेंट केल्यास दरमहा २१% व्याजाने दंड आकारला जाईल.'),
                ('रिडेव्हलपमेंट', 'रिडेव्हलपमेंट कधी सुरू होईल, बिल्डर माहिती, घरांचा ताबा', 'रिडेव्हलपमेंट प्रकल्पासाठी सध्या निविदा प्रक्रिया सुरू आहे. सदस्यांनी विशेष सर्वसाधारण सभेत घेतलेल्या निर्णयानुसार पुढील कार्यवाही केली जाईल.'),
                ('कायदेशीर', 'हक्क आणि कर्तव्ये, सभासद हक्क, सोसायटी कायदा', 'महाराष्ट्र सहकारी संस्था कायदा १९६० कलम २४-२६ नुसार, प्रत्येक सदस्याला सोसायटीच्या कारभारात सहभागी होण्याचा, मतदान करण्याचा आणि आवश्यक माहिती मिळवण्याचा अधिकार आहे.'),
                ('कायदेशीर', 'वारस नोंदणी कशी करावी, नॉमिनेशन फॉर्म', 'वारस नोंदणीसाठी फॉर्म नं. ५ भरून तो सचिवांकडे जमा करावा लागतो. यासाठी मयत सभासदाचा मृत्यू दाखला आणि वारसाहक्काचे पुरावे आवश्यक असतात.'),
                ('नियम', 'पाळीव प्राणी नियम, कुत्रा पाळणे, सोसायटी आक्षेप', 'सोसायटीत पाळीव प्राणी पाळण्यास मनाई नाही, परंतु प्राण्यांमुळे इतर सदस्यांना त्रास होऊ नये आणि स्वच्छतेची काळजी घ्यावी, असे उपविधी स्पष्ट करतात.'),
            ]
            
            for cat, pattern, ans in ai_data:
                kb = AIKnowledge(category=cat, question_pattern=pattern, answer=ans)
                db.session.add(kb)
            
            db.session.commit()
            print("✅ सॅम्पल AI नॉलेज डेटा (Legal KB) जोडला गेला")

# =====================================================
# MAIN EXECUTION (मुख्य एक्झिक्यूशन)
# =====================================================

if __name__ == '__main__':
    # डेटाबेस इनिशियलाईझ करा
    init_db()
    
    # अपलोड फोल्डर्स तयार करा
    os.makedirs(app.config['UPLOAD_FOLDER_DIRECTORS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_PMC'], exist_ok=True)
    
    # ऍप्लिकेशन चालवा
    print("🚀 सिध्द गौतम सोसायटी वेबसाईट सुरू होत आहे...")
    print("🌐 URL: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
