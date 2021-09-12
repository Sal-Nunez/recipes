from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.recipe import Recipe
from flask_app.models.user import User

@app.route('/recipes/new')
def new_recipe():
    if 'id' not in session:
        flash("Please Login", "login")
        return redirect('/')
    elif session['logged_in'] > 0:
        id = session['id']
        return render_template('new_recipe.html', id=id)

@app.route('/recipes/<int:id>')
def show_one_recipe(id):
    if 'id' not in session:
        flash("Please Login", "login")
        return redirect('/')
    data = {
    'recipe': Recipe.select(data={'id': id}),
    'user': User.select(data={'id': session['id']})
    }
    print(data)
    return render_template('show_recipe.html', **data)

@app.route('/recipes/create', methods=['POST'])
def create_recipe():
    if 'id' not in session:
        flash("Please Login", "login")
        return redirect('/')
    if not Recipe.validate_recipe(request.form):
        return redirect('/new')
    else:
        Recipe.insert(request.form)
        return redirect('/dashboard')

@app.route('/recipes/delete/<int:id>')
def delete_recipe(id):
    recipe = Recipe.select(data={'id': id})
    user = User.select(data={'id': session['id']})
    if user.id != recipe.user_id:
        flash("Must be logged in to delete your recipe!")
        return redirect('/dashboard')
    else:
        Recipe.delete(data={'id': id})
        return redirect('/dashboard')

@app.route('/recipes/edit/<int:id>')
def edit_recipe(id):
    recipe = Recipe.select(data={'id': id})
    user = User.select(data={'id': session['id']})
    data = {
        'user': user,
        'recipe': recipe
    }
    print(recipe.date_made_on)
    if user.id != recipe.user_id:
        flash("Must be logged in to edit your recipe!")
        return redirect('/dashboard')
    else:
        return render_template('edit_recipe.html', **data)

@app.route('/recipes/edit', methods=['POST'])
def update_recipe():
    if 'id' not in session:
        flash("Please Login", "login")
        return redirect('/')
    if not Recipe.validate_recipe(request.form):
        recipe = Recipe.select(data={'id':request.form['id']})
        return redirect(f'/recipes/edit/{recipe.id}')
    else:
        Recipe.update_recipe(request.form)
        return redirect('/dashboard')