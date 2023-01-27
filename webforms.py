from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, PasswordField, BooleanField, ValidationError, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Enviar")

class CampanhasForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    author = StringField("Autor da campanha ")
    finality = StringField("Finalidade da Campanha", validators=[DataRequired()])
    goal = IntegerField("Meta da campanha", validators=[DataRequired()])
    slug = StringField("Palavras-chave da campanha", validators=[DataRequired()])
    content = CKEditorField('Conteúdo', validators=[DataRequired()])
    submit = SubmitField("Enviar", validators=[DataRequired()])

class UserForm(FlaskForm):
    name= StringField("Nome", validators=[DataRequired()])
    username = StringField("Usuário", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Senha', validators=[DataRequired(), EqualTo('password_hash2', message='As senhas não são iguais.')])
    password_hash2 = PasswordField('Confirmar Senha',validators=[DataRequired()])
    profile_picture = FileField("Foto de Perfil")
    submit = SubmitField("Enviar")

class Form(FlaskForm):
    name= StringField("Qual seu nome?", validators=[DataRequired()])
    submit = SubmitField("Enviar")

class SearchForm(FlaskForm):
    searched = StringField("Pesquisar", validators=[DataRequired()])
    submit = SubmitField("Enviar")

