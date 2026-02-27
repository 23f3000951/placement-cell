from flask import Flask, render_template, redirect, request
from flask import current_app as app
from .models import *

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form.get("password")
        this_user = User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == password:
                if this_user.role == "Admin":
                    return redirect("/Admin")
                if this_user.role == "student":
                    return redirect(f"/student_dashboard/{this_user.id}")
                if this_user.role == "company" and this_user.is_approved==True:
                    return redirect(f"/company_dashboard/{this_user.id}")
                else:
                    return "Company registered! Please wait for Admin approval."
            else:
                return render_template("incorrect_p.html")
        else:
            return render_template("not_exit.html")
    return render_template("login.html")    


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form.get("username")
        uemail = request.form.get("email")
        upwd = request.form.get("password")
        urole = request.form.get("role")
        user_name = User.query.filter_by(username=uname).first()
        user_email = User.query.filter_by(email=uemail).first()
        if user_name or user_email:
            return render_template("already.html")
        else:
            approve_status = True if urole=="student" else False
            new_user = User(username=uname, email=uemail, password=upwd, role=urole, is_approved=approve_status)
            db.session.add(new_user)
            db.session.commit()
            if urole == 'student':
                udept = request.form.get("department")
                new_profile = Student(user_id=new_user.id, name=uname, department=udept)
                db.session.add(new_profile)
            elif urole == 'company':
                uovw = request.form.get("overview") 
                new_profile = Company(user_id=new_user.id, name=uname, overview=uovw)
                db.session.add(new_profile)
            db.session.commit()
            if urole == 'student':
                return redirect("/login")
            else:
                return "Company registered! Please wait for Admin approval."
    return render_template("register.html")


@app.route("/Admin")
def admin_dashboard():
    admin = User.query.filter_by(role="Admin").first()
    companies = Company.query.join(User).filter(User.is_approved == True).all()
    students = Student.query.all()
    
    pending_companies = Company.query.join(User).filter(User.is_approved == False).all()
    student_apps = Application.query.all()
    ongoing_drives = Drive.query.filter_by(status="Ongoing").all()
    return render_template("Admin_Dashboard.html", admin=admin, companies=companies, students=students, pending_companies=pending_companies, student_apps=student_apps, ongoing_drives=ongoing_drives)


@app.route("/admin/action/<string:action>/<int:user_id>", methods=["GET","POST"])
def admin_action(action, user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    if action == "approve":
        user.is_approved = True
    elif action == "delete":
        db.session.delete(user)
    db.session.commit()
    return redirect("/Admin")


@app.route("/company_dashboard/<int:user_id>")
def company_dashboard(user_id):
    this_company = Company.query.filter_by(user_id=user_id).first()
    if not this_company:
        return "Company profile not found", 404
    upcoming_drives = Drive.query.filter_by(company_id=this_company.id, status='Ongoing').all()
    closed_drives = Drive.query.filter_by(company_id=this_company.id, status='Closed').all()
    return render_template("company_Dashboard.html", company=this_company, upcoming_drives=upcoming_drives, closed_drives=closed_drives)


@app.route("/drive/details/<int:drive_id>")
def drive_details(drive_id):
    drive = Drive.query.get(drive_id)
    if not drive:
        return "Drive record not found!", 404
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("Com_see_app.html", drive=drive, applications=applications)


@app.route("/drive/close/<int:drive_id>")
def close_drive(drive_id):
    drive = Drive.query.get(drive_id)
    if drive:
        drive.status = 'Closed'
        db.session.commit() 
        return redirect(f"/company_dashboard/{drive.company.user_id}")
    return "Drive not found", 404


@app.route("/student/application/review/<int:app_id>", methods=["GET", "POST"])
def review_application(app_id):
    application = Application.query.get(app_id)
    if not application:
        return "Application not found", 404
    if request.method == "POST":
        new_status = request.form.get("status")
        if new_status:
            application.status = new_status 
            db.session.commit()
            return redirect(f"/drive/details/{application.drive_id}")
    return render_template("Com_stu_app.html", app=application)


@app.route("/company/<int:company_id>/create_drive", methods=["GET", "POST"])
def create_drive(company_id):
    this_company = Company.query.get(company_id)
    if not this_company:
        return "Company not found", 404
    if request.method == "POST":
        d_name = request.form.get("drive_name")
        j_title = request.form.get("job_title")
        j_desc = request.form.get("job_description")
        e_criteria = request.form.get("eligibility")
        d_line = request.form.get("deadline")
        salary = request.form.get("salary")
        location = request.form.get("location")
        
        new_drive = Drive(company_id=this_company.id,drive_name=d_name,job_title=j_title,job_description=j_desc, eligibility=e_criteria,deadline=d_line,salary=salary, location=location)
        
        db.session.add(new_drive)
        db.session.commit()
        return redirect(f"/company_dashboard/{this_company.user_id}")
    return render_template("create_drive.html", company_id=company_id)


@app.route("/admin/application/view/<int:app_id>")
def view_student_app(app_id):
    application = Application.query.get(app_id)
    if not application:
        return "Application not found", 404
    return render_template("Adm_stu_app.html", app=application)


@app.route("/admin/view_drive/<int:drive_id>")
def view_comp_drive(drive_id):
    drive = Drive.query.get(drive_id)
    if not drive:
        return "Drive record not found!", 404
    return render_template("Adm_com_drive.html", drive=drive)


@app.route("/student_dashboard/<int:user_id>")
def student_dashboard(user_id):
    this_student = Student.query.filter_by(user_id=user_id).first()
    if not this_student:
        return "Student profile not found", 404
    all_companies = Company.query.join(User).filter(User.is_approved == True).all()
    return render_template("Student_dashboard.html", student=this_student, companies=all_companies)


@app.route("/student_history/<int:user_id>")
def student_history(user_id):
    this_student = Student.query.filter_by(user_id=user_id).first()
    if not this_student:
        return "Student not found", 404
    return render_template("Student_history.html", student=this_student)

@app.route("/student/company_view/<int:user_id>/<int:company_id>")
def student_company_view(user_id, company_id):
    this_student = Student.query.filter_by(user_id=user_id).first()
    this_company = Company.query.get(company_id)
    if not this_company or not this_student:
        return "Data not found", 404
    return render_template("Stud_comp.html", company=this_company, student=this_student)

@app.route("/drive/view/<int:user_id>/<int:drive_id>")
def view_drive_details(user_id, drive_id):
    this_student = Student.query.filter_by(user_id=user_id).first()
    this_drive = Drive.query.get(drive_id)
    if not this_drive or not this_student:
        return "Record not found", 404
    return render_template("Stud_comp_drive.html", drive=this_drive, student=this_student)

@app.route("/drive/apply/<int:sid>/<int:did>", methods=["POST"])
def apply_now(sid, did):
    already_applied = Application.query.filter_by(student_id=sid, drive_id=did).first()
    if not already_applied:
        new_app = Application(student_id=sid, drive_id=did)
        db.session.add(new_app)
        db.session.commit()
    this_student = Student.query.get(sid)
    return redirect(f"/student_dashboard/{this_student.user_id}")

@app.route("/search")
def search():
    search_word = request.args.get("search")
    key = request.args.get("key")
    if key == "student":
        results = Student.query.filter((Student.name.like(f"%{search_word}%")) | (Student.id == search_word) | (Student.department.like(f"%{search_word}%"))).all()
    else:
        results = Company.query.filter(Company.name.like(f"%{search_word}%")).all()
    return render_template("search_results.html", results=results, key=key, search_word=search_word)