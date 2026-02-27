from flask import Flask
from application.database import db
app = None

def create_app():
    app=Flask(__name__)
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement.sqlite3'
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
from application.controllers import * #ye app k create hone k baad hi likh sakte hain kyu ki controllers.py me app ka use hua hai.
# from application.models import * (not required, like we need to connect models.py to app.py but we will connect it indirectly vie database because models are not required in app.py but its required in databse, if we connect models.py directly then it will increase load on app.py )

if __name__ == '__main__': #run this app, only when invoked.
    with app.app_context():
        db.create_all()
        Manager=User.query.filter_by(username="GOPAL").first()
        if Manager is None:
            Manager=User(username="GOPAL",email="agri@gmail.com",password="71516110",role="Admin")
            db.session.add(Manager)
            db.session.commit()

    app.run()

#Note:- when we run this app module, it will create a proxy object as current_app which we can use later in other files and it will also avoid circular import error, and mapping happens at this place.
