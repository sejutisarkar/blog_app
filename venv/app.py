from flask import Flask, g, render_template, redirect, url_for,flash,abort;
import models;
import forms;
from flask_login import LoginManager, login_user, logout_user,login_required,current_user
from flask_bcrypt import check_password_hash


DEBUG = True
PORT=8080
HOST='0.0.0.0'


app = Flask(__name__)
app.secret_key = 'asejfuf.dudm18,!28sms9wjdnoijl'

login_manager = LoginManager();
login_manager.init_app(app)
login_manager.login_view = 'login';

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user=current_user

@app.after_request
def after_request(response):
    g.db.close();
    return response

@app.route('/register',methods=('get','post'))
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash('you are registered',"success")
        models.User.create_user(
            username = form.username.data,
            email = form.email.data,
            password = form.password.data,
            is_admin = form.is_admin.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("you are logged out",'success')
    return render_template('logout.html')

@app.route('/new_post',methods=('get','post'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),content=form.content.data.strip())
        flash("messge Posted","success")
        return redirect(url_for('index'))
    return render_template('post.html',form=form)

@app.route('/')
def index():
    stream = models.Post.select().limit(200)
    return render_template('stream.html',stream = stream)

@app.route('/stream')
@app.route('/stream<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        user = models.User.select().where(models.User.username**username).get()
        stream = user.posts.limit(200)
    else:
        stream = current_user.get_stream().limit(200)
        user = current_user
    if username:
        template = 'user_stream.html'
        return render_template(template,stream=stream,user=user)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    return render_template('stream.html',stream=posts)

@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash("You're now following {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash("You've unfollowed {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='sejuti',
            email='1605527@kiit.ac.in',
            password='secret',
            is_admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG,host=HOST,port=PORT)
