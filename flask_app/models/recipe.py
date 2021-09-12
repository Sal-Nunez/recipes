from flask_app.config.mysqlconnection import connectToMySQL
from flask import Flask, flash, session
import re
from flask_bcrypt import Bcrypt
from flask_app.models.user import User
app = Flask(__name__)
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

class Recipe:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_made_on = data['date_made_on']
        self.under_30_min = data['under_30_min']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
    @classmethod
    def select(cls, data=None):
        if data:
            query = "SELECT * FROM recipes WHERE recipes.id = %(id)s"
            results = connectToMySQL('recipes').query_db(query, data)
            print("RECIPEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",results)
            recipe = cls(results[0])
            return recipe
        else:
            query = "SELECT * FROM recipes"
            results = connectToMySQL('recipes').query_db(query)
            recipes = []
            for recipe in results:
                recipes.append(cls(recipe))
            return recipes
    
    @classmethod
    def insert(cls, data):
        query = "INSERT INTO recipes (name, description, instructions, date_made_on, under_30_min, user_id) VALUES (%(name)s, %(description)s, %(instructions)s, %(date_made_on)s, %(under_30_min)s, %(user_id)s)"
        results = connectToMySQL('recipes').query_db(query, data)
        recipe = Recipe.select(data = {'id':results})
        return recipe

    @classmethod
    def update_recipe(cls, data):
        query = "UPDATE recipes SET name = %(name)s, description = %(description)s, instructions = %(instructions)s, date_made_on = %(date_made_on)s, under_30_min = %(under_30_min)s where recipes.id = %(id)s"
        return connectToMySQL('recipes').query_db( query, data )
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM recipes WHERE recipes.id = %(id)s"
        return connectToMySQL('recipes').query_db(query, data)

    @staticmethod #recipe_create_validation
    def validate_recipe(data):
        is_valid = True
        query1 = "select * from recipes where recipes.name = %(name)s and recipes.description = %(description)s and recipes.instructions = %(instructions)s and recipes.date_made_on = %(date_made_on)s and recipes.under_30_min = %(under_30_min)s and recipes.user_id = %(user_id)s"
        if connectToMySQL('recipes').query_db(query1, data):
            flash("Recipe Already Exists")
            is_valid = False
        if len(data['name']) < 3:
            flash ("Name must be at least 3 characters.")
            is_valid = False
        if len(data['description']) < 3:
            flash ("Description must be at least 3 characters.")
            is_valid = False
        if len(data['instructions']) < 3:
            flash ("Instructions must be at least 3 characters.")
            is_valid = False
        if 'date_made_on' not in data:
            flash("Please enter a date!")
            is_valid = False
        elif data['date_made_on'] == '':
            flash("Please enter a date!")
            is_valid = False
        if 'under_30_min' not in data:
            flash("Please select a response if under 30 min")
            is_valid = False
        else:
            if data['under_30_min'] not in ['yes', 'no']:
                flash ("Is recipe under 30 min?")
                is_valid = False
        print("DATE MADE ON????????????????????????????", is_valid)
        return is_valid