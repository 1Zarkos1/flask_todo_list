import datetime
import json
import os

from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, IntegerField
from wtforms.widgets import HiddenInput
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError


app = Flask(__name__, static_folder="./assets")
app.config.from_object("config.DevConfig")
app.jinja_options["trim_blocks"] = True
app.jinja_options["lstrip_blocks"] = True
db = SQLAlchemy(app)


class Task(db.Model):

    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    date_due = db.Column(db.DateTime)
    date_completed = db.Column(db.DateTime)
    description = db.Column(db.String)

    def __repr__(self):
        return f"Task - №{self.id}"


class TaskForm(FlaskForm):
    id = HiddenField()
    title = StringField("Title", validators=[DataRequired()])
    date_due = DateTimeLocalField("Date due", format="%Y-%m-%dT%H:%M")
    description = TextAreaField("Description", validators=[DataRequired()])
    hidden = HiddenField()

    def validate_date_due(self, date_due):
        if date_due.data is None:
            raise ValidationError(
                'This field is required with the following \
                                  format "year-month-dayThour:minute"'
            )
        if date_due.data < datetime.datetime.now():
            raise ValidationError("Due time must be in the future.")


@app.route("/", methods=["GET", "POST"])
def show_tasks():
    form = TaskForm()
    print(form.hidden.data)
    if form.validate_on_submit():
        print("valid")
        if form.hidden.data:
            t = Task.query.get(int(form.hidden.data))
        else:
            t = Task()
            db.session.add(t)
        t.title = form.title.data
        t.date_due = form.date_due.data
        t.description = form.description.data
        db.session.commit()
        return redirect("/")

    print(form.errors)

    result = Task.query.order_by(Task.date_completed.asc(), Task.date_due.desc()).all()
    return render_template("index.html", result=result, form=form)


@app.route("/get_tasks/", methods=["POST"])
def get_tasks():
    if request.get_json():
        tasks = (
            Task.query.filter(Task.date_completed == None)
            .filter(Task.date_due > datetime.datetime.now())
            .order_by(Task.date_completed.asc(), Task.date_due.desc())
            .all()
        )
    else:
        tasks = Task.query.order_by(
            Task.date_completed.asc(), Task.date_due.desc()
        ).all()
    return render_template("_todos.html", result=tasks)


@app.route("/complete-task/<int:id>")
def complete_task(id):
    Task.query.get(id).date_completed = datetime.datetime.now()
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
    return dict(now=datetime.datetime.now())