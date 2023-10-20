from flask_wtf import FlaskForm
from wtforms import SelectField, FileField, StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo("password")])
    email = StringField('Email', validators=[DataRequired(),Email()])

    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remeber = BooleanField('Remeber Me')

    submit = SubmitField('Log In')

class InputForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text',validators=[DataRequired()])
    img = FileField('Upload Image', validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField("Post")

class ConfirmForm(FlaskForm):
    confirm = BooleanField("Confirmed",default=False)
    submit = SubmitField("Submit")

class SearchForm(FlaskForm):
    searched = TextAreaField('Text',validators=[DataRequired()])
    search_type = SelectField("Search Type",choices=["Author","Contents","Title"])
    submit = SubmitField("Submit")

class CommentForm(FlaskForm):
    comment = TextAreaField('Text',validators=[DataRequired()])
    submit = SubmitField("Submit")