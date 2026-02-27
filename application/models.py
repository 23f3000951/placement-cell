from  .database import db
 #by default, context of application is root directory, no dot --> looks in root directory, 
 # with dot --> looks in current directory.


# 1. User Table: Authentication ke liye
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) 
    email = db.Column(db.String(150), unique=True, nullable=False) 
    password = db.Column(db.String(200), nullable=False) 
    role = db.Column(db.String(50), nullable=False) 
    is_approved = db.Column(db.Boolean, default=False)
    student_profile = db.relationship('Student', backref='user_account', cascade="all, delete-orphan", uselist=False)
    company_profile = db.relationship('Company', backref='user_account', cascade="all, delete-orphan", uselist=False)
    
# 2. Student Table: Student profile details
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False) 
    department = db.Column(db.String(100), nullable=False) 
    # Applications ke saath relation
    applications = db.relationship('Application', backref='student', cascade="all, delete-orphan")

# 3. Company Table: Organization profile
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False) 
    overview = db.Column(db.Text) 
    # Drives ke saath relation
    drives = db.relationship('Drive', backref='company', cascade="all, delete-orphan")

# 4. Drive Table: Job postings
class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    drive_name = db.Column(db.String(150), nullable=False) 
    job_title = db.Column(db.String(150), nullable=False) 
    job_description = db.Column(db.Text) 
    eligibility = db.Column(db.Text)
    salary = db.Column(db.Integer, nullable=True) 
    location = db.Column(db.String(100), nullable=True)
    deadline = db.Column(db.String(100)) 
    status = db.Column(db.String(50), default='Ongoing')
    drive_applications = db.relationship('Application', backref='drive', cascade="all, delete-orphan") 

# 5. Application Table: Linking Students and Drives
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    interview_type = db.Column(db.String(100), default='In-person') 
    status = db.Column(db.String(100), default='Pending') 

#1. from database import db --> models.py will look this file in root directory.
#2. from .database import db --> models.py will look this file in current directory(applications folder).
#3. from application.database import db --> models.py will look for this file in application directory 
#   within the application folder itself.