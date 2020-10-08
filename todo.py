from datetime import datetime

import bcrypt
from flask import Flask, redirect, render_template, request, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import (
    StringField,
    TextAreaField,
    HiddenField,
    IntegerField,
    PasswordField,
    SubmitField,
)
from wtforms.fields.html5 import DateTimeLocalField, EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo


app = Flask(__name__, static_folder="./assets")
app.config.from_object("config.DevConfig")
app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True
db = SQLAlchemy(app)
login = LoginManager(app)
# csrf = CSRFProtect(app)


class User(UserMixin, db.Model):

    __tablename__ = "user"

    email = db.Column(db.String, primary_key=True)
    _password = db.Column(db.String)
    tasks = db.relationship("Task", backref="author", cascade="delete, delete-orphan")

    def get_id(self):
        return self.email

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plain_pass):
        self._password = bcrypt.hashpw(plain_pass.encode("utf-8"), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self._password)


@login.user_loader
def loader(email):
    return User.query.get(email)


class Task(db.Model):

    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    author_email = db.Column(db.String, db.ForeignKey("user.email"), index=True)
    title = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_due = db.Column(db.DateTime)
    date_completed = db.Column(db.DateTime)
    description = db.Column(db.String)

    def __repr__(self):
        return f"<Task - №{self.id}>"


class RegistrationForm(FlaskForm):
    email = EmailField("Email", validators=[Email()])
    password = PasswordField("Password")
    pass_repeat = PasswordField("Repeat password", validators=[EqualTo("password")])
    submit = SubmitField("Register")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("User with this email already exist")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[Email()])
    password = PasswordField("Password")
    submit = SubmitField("Login")


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    date_due = DateTimeLocalField("Date due", format="%Y-%m-%dT%H:%M")
    description = TextAreaField("Description", validators=[DataRequired()])
    hidden_id = HiddenField()
    submit = SubmitField("Add task")

    def validate_date_due(self, date_due):
        if date_due.data is None:
            raise ValidationError(
                'This field is required with the following \
                                  format "year-month-dayThour:minute"'
            )
        if date_due.data < datetime.now():
            raise ValidationError("Due time must be in the future.")


@app.route("/", methods=["GET", "POST"])
def show_tasks():
    form = TaskForm()
    log_form = LoginForm()
    if "password" in request.form:
        if log_form.validate_on_submit():
            user = User.query.get(log_form.email.data)
            if user.check_password(log_form.password.data):
                login_user(user)
                return redirect("/")
    else:
        if form.validate_on_submit():
            if _id := form.hidden_id.data:
                t = Task.query.get(int(_id))
            else:
                t = Task()
                t.author = current_user if current_user.is_authenticated else None
                db.session.add(t)
            form.populate_obj(t)
            db.session.commit()
            return redirect("/")
    filt = current_user.email if current_user.is_authenticated else None
    result = (
        Task.query.filter_by(author_email=filt)
        .order_by(Task.date_completed.asc(), Task.date_due.desc())
        .all()
    )
    return render_template("index.html", result=result, form=form, log_form=log_form)


@app.route("/get_tasks/", methods=["POST"])
def get_tasks():
    email_filter = current_user.email if current_user.is_authenticated else None
    if request.get_json():
        tasks = Task.query.filter(Task.date_completed == None).filter(
            Task.date_due > datetime.now()
        )
    else:
        tasks = Task.query
    tasks = (
        tasks.filter_by(author_email=email_filter)
        .order_by(Task.date_completed.asc(), Task.date_due.desc())
        .all()
    )
    return render_template("_todos.html", result=tasks)


@app.route("/register/", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("show_tasks"))
    return render_template("register.html", form=form)


@app.route("/profile/<user>")
def profile(user):
    pass


@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")


@app.route("/complete-task/<int:id>")
def complete_task(id):
    Task.query.get(id).date_completed = datetime.now()
    db.session.commit()
    return jsonify(True)


@app.route("/delete-task/<int:id>")
def delete_task(id):
    db.session.delete(Task.query.get(id))
    db.session.commit()
    return jsonify(True)


@app.template_filter()
def time(date_obj):
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")


@app.template_filter()
def interval(interval_obj):
    return str(interval_obj).split(".")[0]


@app.context_processor
def set_required_variables():
    return dict(now=datetime.now())