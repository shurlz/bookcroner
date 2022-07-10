from flask import render_template, redirect, flash, request, url_for
from bookapp import app
from bookapp.models import users, all_books, users_contents, search_history
from bookapp import db
from flask_login import login_user , logout_user, current_user, login_required
from bookapp.forms import SignInForm, BookSearch, SignUpForm, CreatePrompt, TodoList, Edit, Delete
from bookapp.recommendation_engine import collaborative_recommender, book_titles
from datetime import date
from bookapp import oauth
import pandas as pd

@app.route('/', methods=['GET','POST'])
def home():
    form = BookSearch()

    # for rendering javascript chart
    try:
        most_searched = []
        for books in search_history.query.all():
            most_searched.append(books.search)

        series = pd.Series(most_searched)
        count = series.value_counts()[:8]
        top_eight = []
        for i in range(8):
            top_eight.append([count.index[i],count[i]])
    except:
        top_eight = [['None',1],['None',1],['None',1],['None',1],['None',1],['None',1],['None',1],['None',1]]


    if form.validate_on_submit():
        book_query = form.query_item.data
        book = all_books.query.filter(all_books.books.like(f'%{book_query}%')).all()
        if book:
            return render_template('home.html', form=form, possible_books=book, top_eight=top_eight)
        else:
            return 'No book like this exists, sorry'
    
    return render_template('home.html',form=form,top_eight=top_eight)


@app.route('/signup', methods=['GET','POST'])
def signup():
    # currently logged in user cannot access signup page
    if current_user.is_authenticated :
        return redirect(url_for('my_books'))

    form = SignUpForm()
    if form.validate_on_submit():
        new_user = users(email=form.email_address.data,password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash(f'sign up successful {form.email_address.data}!', category='success')
        return redirect('myspace')

    if form.errors != {}:
        for message in form.errors.values():
            flash(f'Error... {message[0]}',category='danger')

    return render_template('signup.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
     # currently logged in user cannot access signin page
    if current_user.is_authenticated :
        return redirect(url_for('my_books'))

    form = SignInForm()
    if form.validate_on_submit():
        attempted_user_login = users.query.filter_by(email=form.email.data).first()
        if attempted_user_login and attempted_user_login.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user_login, form.remember_me.data)
            flash(f'login successful, welcome {attempted_user_login.email}',category='success')
            return redirect('myspace')
        flash('Invalid login credentials',category='danger')
    return render_template('login.html', form=form)

@app.route('/myspace/', methods=['GET','POST'])
@login_required
def my_books():
    try:
        user_info = users_contents.query.filter_by(owner=current_user.id).all()
        form = None
        create = CreatePrompt()
        if request.method=='POST':
            form = TodoList()

        if form:    
            if form.validate_on_submit():
                new_todo = users_contents(book_name=form.book_name.data,message=form.message.data,
                            start_time = date.fromisoformat(form.start_time.data),end_time=date.fromisoformat(form.end_time.data),
                            owner=current_user.id)
                db.session.add(new_todo)
                db.session.commit()
                return redirect(url_for('my_books'))
        
        return render_template('myspace.html',user_info=user_info,form=form,create=create,edit=Edit(),
                                            delete=Delete(),calculator=timehelp)
    except:
        flash('Please ensure you enter the date format as specified !',category='danger')
        return redirect(url_for('my_books'))

@app.route('/update-<post_id>', methods=['GET','POST'])
def update(post_id):
    try:
        user_info = users_contents.query.filter_by(owner=current_user.id).all()
        current_post = users_contents.query.filter_by(id=post_id).first()
        form = TodoList()
        create = CreatePrompt()
        edit = Edit()
        delete = Delete()

        if form.validate_on_submit():
            current_post.book_name = form.book_name.data
            current_post.message = form.message.data
            current_post.start_time = date.fromisoformat(form.start_time.data)
            current_post.end_time = date.fromisoformat(form.end_time.data)
            db.session.commit()
            return redirect('myspace')

        form.book_name.data = current_post.book_name
        form.message.data = current_post.message
        form.start_time.data = str(current_post.start_time).split(' ')[0]
        form.end_time.data = str(current_post.end_time).split(' ')[0]
        return render_template('myspace.html',user_info=user_info,form=form,create=create,edit=edit,
                                delete=delete,calculator=timehelp)
    except:
        flash('Please ensure you enter the date format as specified !',category='danger')
        return redirect(url_for('my_books'))

@app.route('/delete-<post_id>', methods=['GET','POST'])
def delete(post_id):

    post_to_delete = users_contents.query.filter_by(id=post_id).first()
    db.session.delete(post_to_delete)
    db.session.commit()

    flash('post deleted successfully')
    return redirect('myspace')

@app.route('/recommend/<bookname>',methods=['GET','POST'])
def recommend(bookname):
    form = BookSearch()

    # javascript chart.js
    try:
        most_searched = []
        for books in search_history.query.all():
            most_searched.append(books.search)

        series = pd.Series(most_searched)
        count = series.value_counts()[:8]
        top_eight = []
        for i in range(8):
            top_eight.append([count.index[i],count[i]])
    except:
        top_eight = [['None',1],['None',1],['None',1],['None',1],['None',1],['None',1],['None',1],['None',1]]

    # for recommendation
    try:
        recommendation = collaborative_recommender(bookname)
    except:
        return 'Invalid Book Request'
    new_search = search_history(search=bookname)
    db.session.add(new_search)
    db.session.commit()
    return render_template('home.html', form=form, recommendation=recommendation,top_eight=top_eight)

@app.route('/logout')
def logout():
    logout_user( )
    return redirect('/')

# destroy
@app.route('/create-books-sql')
def allbooks():
    if len(all_books.query.all()) < 1000:
        for book in book_titles:
            new_book = all_books(books=book)
            db.session.add(new_book)
            db.session.commit()
        return 'done'
    else:
        return redirect(url_for('home'))

google = oauth.register(
    name = 'google',
    client_id = app.config["GOOGLE_CLIENT_ID"],
    client_secret = app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs = {'scope': 'openid email profile'},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs",
    # token_key = "access_token"
)

@app.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    token = oauth.google.authorize_access_token()
    resp = google.get('userinfo').json()
    google_user_email = resp['email']
    google_user_id = resp['id']
    user = users.query.filter_by(email=google_user_email).first()
    if user:
        login_user(user)
        flash(f'login successful {google_user_email}!', category='success')
        return redirect(url_for('my_books'))
    else:
        new_user = users(email=google_user_email,password=google_user_id)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash(f'sign up successful {google_user_email}!', category='success')
        return redirect(url_for('my_books'))
    
class timehelp:
    def time_split(timestamp):
        return str(timestamp).split(' ')[0]

    def date_distance(timestamp1,timestamp2):
        return f"{str(timestamp1 - timestamp2).split(' ')[0]}  days"

