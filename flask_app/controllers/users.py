from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_app.models.recipe import Recipe

@app.route('/')
def index():
    if 'id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if not User.validate_login(request.form):
        return redirect('/')
    if not User.check_login(request.form):
        return redirect('/')
    else:
        print(request.form)
        user = User.select_by_email(data = {'email':request.form['email']})
        session['id'] = user.id
        return redirect('/dashboard')

@app.route('/register', methods=['POST'])
def register():
    if not User.validate_register(request.form):
        return redirect('/')
    else:
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': request.form['password']
        }
        session['id'] = User.registration(data)
    return redirect('/dashboard')

@app.route('/dashboard')
def success():
    if not 'id' in session:
        flash("Please Login", "login")
        return redirect('/')
    elif session['id'] > 0:
        data = {
        'recipes': Recipe.select(),
        'user': User.select_with_recipes(data={'id': session['id']})
        }
        print(data['user'].recipes)
        return render_template('dashboard.html', **data)

@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')