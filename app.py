from flask import Flask, redirect, url_for, render_template, request
from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo


app = Flask(__name__)

mongo = PyMongo(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

user_details = {}

#user class for flask-loginytho
class User(UserMixin):

    def __init__(self, pagename):
        global user_details

        user_details = mongo.db.userdetails.find_one({"pagename":pagename})
        self.pagename = pagename
        
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.pagename   



#for wtfforms
class RegisterForm(FlaskForm):
    remail = StringField('Email', validators=[DataRequired(), Length(min=7,max=25)])
    rpassword = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    pagename = StringField('Name of the Page', validators= [DataRequired(), Length(min = 1,max= 20)])

class LoginForm(FlaskForm):
    lemail = StringField('Email', validators=[DataRequired(), Email()])
    lpassword = PasswordField('Password',validators=[DataRequired()])


@app.route("/")
@login_required
def homepage():
	global user_details
	return render_template("dashboard.html",pagename = user_details['pagename'],email=user_details['email'],details = user_details['details'],extras = user_details['extras'],html = user_details['html'],css = user_details['css'],extra = zip(user_details['extras']['fieldtitle'],user_details['extras']['fielddescription']))



@app.route("/login",methods = ['GET','POST'])
def login():
	lform = LoginForm()
	rform = RegisterForm(request.form)

	db = mongo.db.userdetails
	
	if request.method == "POST":
		if request.form['btn'] == 'login':
			if lform.validate_on_submit():
				if db.find_one({"email":lform.lemail.data,"password":lform.lpassword.data}):
					data = db.find_one({"email":lform.lemail.data})
					user = User(data['pagename'])
					login_user(user)
					return redirect("/")
				else:
					return "wrong password or not registerd"
			else:
				return "wrong form structure"

		else:
			if rform.validate():
				if db.find_one({"email":rform.remail.data}) or db.find_one({"pagename":rform.pagename.data}):
					return "email already exists or pagename already taken"
				else:
					db.insert({"email":rform.remail.data,"password":rform.rpassword.data,"pagename":rform.pagename.data,"details": {"name":"","phone":"","email":"","description":"","education":"","projects":"","achievements":"","skills":"","fb":"","twitter":"","blog":"","linkedin":"","github":"","img":"../static/img/user4.png","intrests":"","resume":""},"extras" : {"fieldtitle":[],"fielddescription":[]},"html":"","css":""})
					user = User(rform.pagename.data)
					login_user(user)
					return redirect("/")
			else:
				return "Error in Registring"
	else:
		return render_template("homepage.html",lform = lform,rform = rform)



@app.route("/editpage",methods=['GET','POST'])
@login_required
def editpage():
	if request.method == "POST":
		
		name = request.form['name']
		email = request.form['email']
		phone = request.form['phone']
		description = request.form['description']
		education = request.form['education']
		projects = request.form['projects']	
		achievements = request.form['achievements']
		skills = request.form['skills']
		intrests = request.form['intrests']

		fb = request.form['fb']
		twitter = request.form['twitter']
		blog = request.form['blog']
		linkedin = request.form['linkedin']
		github = request.form['github']
		img = request.form['img']
		resume = request.form['resume']

		html = request.form['html']
		css = request.form['css']


		# if request.form['submit'] == 'editpage':
		data = {"name":name,"phone":phone, "email":email,"description":description,"education":education,"projects":projects,"achievements":achievements,"skills":skills,"fb":fb,"twitter":twitter,"blog":blog,"linkedin":linkedin,"github":github,"img":img,"intrests":intrests,"resume":resume}
		
		global user_details
		db = mongo.db.userdetails
		db.find_one_and_update({"email":user_details['email']},{'$set':{'details':data,"html":html,"css":css}})
		user_details['details'] = data
		user_details['html'] = html
		user_details['css'] = css

		return redirect("/")

	else:
		return render_template("editpage.html",pagename = user_details['pagename'],email=user_details['email'],details = user_details['details'],extras = user_details['extras'],html = user_details['html'],css = user_details['css'])

@app.route("/addnewfield",methods=['GET','POST'])
@login_required
def addnewfield():
	global user_details

	if request.method == "POST":
	
		fieldtitle = request.form['title']
		fielddescription = request.form['description']

		if fieldtitle in user_details['extras']['fieldtitle'] and fielddescription in user_details['extras']['fielddescription']:
			return "this data already exists"
		else:	
			user_details['extras']['fieldtitle'].append(fieldtitle)
			user_details['extras']['fielddescription'].append(fielddescription)
			
			db = mongo.db.userdetails
			db.find_one_and_update({"email":user_details['email']},{'$set':{'extras':user_details['extras']}})
			
			return redirect(url_for("addnewfield"))
	else:
		return render_template("addnewfield.html",pagename = user_details['pagename'],extras = zip(user_details['extras']['fieldtitle'],user_details['extras']['fielddescription']))


@app.route("/addnewfield/<title>/<description>",methods = ['GET','POST'])
@login_required
def editfield(title,description):
	global user_details
	db = mongo.db.userdetails

	if request.method == "POST":
		if request.form['submit'] == 'save':
			user_details['extras']['fieldtitle'].remove(title)
			user_details['extras']['fielddescription'].remove(description)

			user_details['extras']['fieldtitle'].append(request.form['fieldtitle'])
			user_details['extras']['fielddescription'].append(request.form['fielddescription'])

			db.find_one_and_update({"email":user_details['email']},{'$set':{'extras':user_details['extras']}})
			return redirect(url_for("addnewfield"))
		else:
			user_details['extras']['fieldtitle'].remove(title)
			user_details['extras']['fielddescription'].remove(description)

			db.find_one_and_update({"email":user_details['email']},{'$set':{'extras':user_details['extras']}})
			return redirect(url_for("addnewfield"))
	else:
		return render_template("editfield.html",title = title,description = description)



@app.route("/theme")
@login_required
def theme():
	return render_template("404.html")


@app.route("/<string>")
def preview(string):
	db = mongo.db.userdetails

	if db.find_one({"pagename":string}):
		data = db.find_one({"pagename":string})
	else:
		return "requested user not available yet"
	return render_template("preview.html",data = data,extra = zip(data['extras']['fieldtitle'],data['extras']['fielddescription']))



@app.route("/aboutus")
def about():
	return render_template("aboutpage.html")


@login_manager.user_loader
def load_user(username):
	return User(username)


@app.route("/logout")
@login_required
def logout():
	logout_user()
	global user_details
	user_details = {}
	return redirect("/")

if __name__ == "__main__":
	app.run()
