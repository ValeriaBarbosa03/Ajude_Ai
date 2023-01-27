from flask import Flask, render_template,flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, CampanhasForm, UserForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


app = Flask(__name__)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:bancod2830/*@localhost/usuarios'
app.config['SECRET_KEY'] = "my secret key"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app,db)


class Campanhas(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    #author = db.Column(db.String(255), nullable=False)
    finality = db.Column(db.String(255), nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    content = db.Column(db.String(255), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True) 
    date_add = db.Column(db.DateTime, default =datetime.utcnow)
    profile_picture = db.Column(db.String(1000), nullable = True)
    password_hash = db.Column(db.String(128))
    campanhas = db.relationship('Campanhas', backref='author')

    @property
    def password(self):
        raise AttibuteError('A senha não é um atributo a ser lido!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<Name %r>' % self.name

#Routes

#Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/add-campanha', methods= ['GET','POST'])
def add_campanha():
    form = CampanhasForm()
    if form.validate_on_submit():
        author = current_user.id
        campanha = Campanhas(title= form.title.data, author_id = author, finality = form.finality.data, goal = form.goal.data, slug = form.slug.data, content = form.content.data)
        form.title.data = ''
        #form.author.data = ''
        form.finality.data = ''
        form.goal.data = ''
        form.slug.data = ''
        form.content.data = ''
        db.session.add(campanha)
        db.session.commit()
        form = CampanhasForm(formdata = None)

        flash("Campanha adicionada com sucesso!")
        
    return render_template("add_campanha.html", form=form)


@app.route('/campanhas')
def campanhas():
    campanhas = Campanhas.query.order_by(Campanhas.date_posted)
    return render_template("campanhas.html", campanhas=campanhas)

@app.route('/campanhas/<int:id>')
def campanha(id):
    campanha = Campanhas.query.get_or_404(id)
    return render_template('campanha.html', campanha=campanha)

@app.route('/campanhas/edit/<int:id>', methods= ['GET','POST'])
@login_required
def edit_campanha(id):
    campanha = Campanhas.query.get_or_404(id)
    form = CampanhasForm()
    if form.validate_on_submit():
        campanha.title = form.title.data
        #campanha.author = form.author.data
        campanha.finality = form.finality.data
        campanha.goal = form.goal.data
        campanha.slug = form.slug.data
        campanha.content = form.content.data
        db.session.add(campanha)
        db.session.commit()
        flash("Campanha atualizada com sucesso.")
        return redirect(url_for('campanha', id = campanha.id))

    if current_user.id == campanha.author_id or current_user.id == 53:
        form.title.data = campanha.title
        #form.author.data = campanha.author
        form.finality.data = campanha.finality
        form.goal.data = campanha.goal
        form.slug.data = campanha.slug
        form.content.data = campanha.content
        return render_template('edit_campanha.html', form = form)
    else:
        flash("Você não está autorizado a editar essa camapanha!")
        campanhas = Campanhas.query.order_by(Campanhas.date_posted)
        return render_template("campanhas.html", campanhas=campanhas)


@app.route('/campanhas/delete/<int:id>')
@login_required
def delete_campanha(id):
    campanha_del = Campanhas.query.get_or_404(id)
    id = current_user.id
    if id == campanha_del.author.id or id == 53: 
        try:
            db.session.delete(campanha_del)
            db.session.commit()
            flash("Campanha excluída.")
            campanhas = Campanhas.query.order_by(Campanhas.date_posted)
            return render_template("campanhas.html", campanhas=campanhas)
        except:
            flash("Houve um problema ao excluir a campanha. Tente novamente.")
    else:
        flash("Você não tem autorização para deletar essa campanha.")
        campanhas = Campanhas.query.order_by(Campanhas.date_posted)
        return render_template("campanhas.html", campanhas=campanhas)


@app.route('/user/add', methods= ['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email= form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name = form.name.data, username = form.username.data, email= form.email.data, password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash = ''
        flash("Usuário adicionado com sucesso!")
    our_users = Users.query.order_by(Users.date_add)
       
    return render_template ('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/update/<int:id>', methods= ['GET','POST'])
@login_required
def update(id):
    form = UserForm()
    name_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_update.name = request.form['name']
        name_update.email = request.form['email']
        name_update.username = request.form['username']
        try:
            db.session.commit()
            flash("Usuário atualizado com sucesso!")
            return render_template("update.html", form=form, name_update=name_update, id=id)
        except:
            flash("Erro ao atualizar os dados! Tente novamente.")
            return render_template("update.html", form=form, name_update=name_update, id=id)
    else:
        return render_template("update.html", form=form, name_update=name_update, id=id)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
        user_delete = Users.query.get_or_404(id)
        name= None
        form = UserForm()
        try:
            db.session.delete(user_delete)
            db.session.commit()
            flash("Usuário excluído!")
            our_users = Users.query.order_by(Users.date_add)
            return render_template ('add_user.html', form=form, name=name, our_users=our_users)
        except:
            flash("Erro ao excluir um usuário!")
            return render_template ('add_user.html', form=form, name=name, our_users=our_users)
    else:
         flash("Você não pode excluir esse usuário!")
         return redirect(url_for('dashboard'))

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 53:
        return render_template ('admin.html')
    else:
        flash("Você precisa ser Admin para acessar essa página.")
        return redirect(url_for('dashboard')) 


#Error Pages
#Invalid Urls
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/name', methods= ['GET','POST'])
def name():
    name= None
    formulario = Form()
    if formulario.validate_on_submit():
        name = formulario.name.data
        formulario.name.data = ''
        flash("Form enviado corretamente!")
    return render_template ("name.html",
    name=name,
    formulario = formulario)

@app.route('/login', methods= ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login feito com sucesso!")
                return redirect(url_for('dashboard'))
            else:
                flash("Senha errada. Tente novamente.")
        else:
            flash("O usuário não existe. Tente novamente.")

    return render_template('login.html', form=form)

@app.route('/logout', methods= ['GET','POST'])
@login_required
def logout():
   logout_user()
   flash("Você saiu do sistema.")
   return redirect(url_for('login')) 


@app.route('/dashboard', methods= ['GET','POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_update.name = request.form['name']
        name_update.email = request.form['email']
        name_update.username = request.form['username']
        
        if request.files['profile_picture']:
            name_update.profile_picture = request.files['profile_picture']

            picture_filename = secure_filename(name_update.profile_picture.filename)
            picture_name = str(uuid.uuid1()) + "_" + picture_filename
            saver = request.files['profile_picture']

            name_update.profile_picture = picture_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'],picture_name))
                flash("Usuário atualizado com sucesso!")
                return render_template("dashboard.html", form=form, name_update=name_update)
            except:
                flash("Erro ao atualizar os dados! Tente novamente.")
                return render_template("dashboard.html", form=form, name_update=name_update)
        else:
            db.session.commit()
            flash("Usuário atualizado com sucesso!")
            return render_template("dashboard.html", form=form, name_update=name_update)

    else:
        return render_template("dashboard.html", form=form, name_update=name_update, id=id)
    return render_template('dashboard.html') 

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    campanhas = Campanhas.query
    if form.validate_on_submit():
        campanha.searched = form.searched.data 
        campanhas = campanhas.filter(Campanhas.title.like('%' + campanha.searched + '%'))
        campanhas = campanhas.order_by(Campanhas.date_posted).all()
        return render_template("search.html", form=form, searched = campanha.searched, campanhas = campanhas)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
