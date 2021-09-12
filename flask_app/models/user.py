from flask_app.config.mysqlconnection import connectToMySQL
from flask import Flask, flash, session
import re
from flask_bcrypt import Bcrypt
from flask_app.models import recipe
app = Flask(__name__)
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.full_name = f"{self.first_name} {self.last_name}"
        self.recipes = []
        
    @classmethod
    def select(cls, data=None):
        if data:
            query = "SELECT * FROM users WHERE users.id = %(id)s"
            results = connectToMySQL('recipes').query_db(query, data)
            print("*****************************",results)
            user = cls(results[0])
            return user
        else:
            query = "SELECT * FROM users"
            results = connectToMySQL('recipes').query_db(query)
            users = []
            for user in results:
                users.append(cls(user))
            return users
    
    @classmethod
    def select_with_recipes(cls, data):
        query = "SELECT * FROM users LEFT JOIN recipes ON users.id = recipes.user_id WHERE users.id = %(id)s"
        results = connectToMySQL('recipes').query_db(query, data)
        user = cls(results[0])
        for x in results:
            recipe_data = {
            'id': x['recipes.id'],
            'name': x['name'],
            'description': x['description'],
            'instructions': x['instructions'],
            'date_made_on': x['date_made_on'],
            'under_30_min': x['under_30_min'],
            'created_at': x['recipes.created_at'],
            'updated_at': x['recipes.updated_at'],
            'user_id': x['user_id']
            }
            user.recipes.append(recipe.Recipe(recipe_data))
        return user
    @classmethod
    def select_by_email(cls, data):
        if data:
            query = "SELECT * FROM users WHERE users.email = %(email)s"
            results = connectToMySQL('recipes').query_db(query, data)
            user = cls(results[0])
            return user
    @classmethod
    def check_login(cls, data):
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        results = connectToMySQL('recipes').query_db( query, data )
        user = cls(results[0])
        if user.email == data['email'] and bcrypt.check_password_hash(user.password, data['password']):
            print("TRUE")
            session['logged_in'] = user.id
            return True
        else:
            print("FALSE")
            flash("Incorrect email/password try again", 'login')
            return False

    @classmethod
    def registration(cls, data):
        data['password'] = bcrypt.generate_password_hash(data['password'])
        data1 = data['password']
        print(data1)
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s)"
        results = connectToMySQL('recipes').query_db(query, data)
        print (results)
        if query:
            session['id'] = results.id
        return results


    @staticmethod #login validation
    def validate_login(data):
        is_valid = True
        query1 = "select * from users where users.email = %(email)s"
        if not connectToMySQL('recipes').query_db(query1, data):
            flash("Email doesn't exist", 'login')
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid Email Address!", 'login')
            is_valid = False
        return is_valid
    
    @staticmethod #registration validation
    def validate_register(data):
        is_valid = True
        if not data['password_confirmation'] == data['password']:
            flash('Passwords Do Not Match', 'registration')
            is_valid = False
        if len(data['email']) < 7:
            flash('Email must be at least 7 characters', 'registration')
            is_valid = False
        if not NAME_REGEX.match(data['first_name']):
            flash ("First Name can only contain letters", 'registration')
        if not NAME_REGEX.match(data['last_name']):
            flash ("Last Name can only contain letters", 'registration')
        if len(data['first_name']) < 2:
            flash("First Name MUST be at least 2 characters long", 'registration')
            is_valid = False
        if len(data['last_name']) < 2:
            flash("Last Name MUST be at least 2 characters long", 'registration')
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid Email Address!", 'registration')
            is_valid = False
        query1 = "select * from users where users.email = %(email)s"
        if connectToMySQL('recipes').query_db(query1, data):
            flash("Email already exists, please Login, if you forgot your password TOUGH", 'registration')
            is_valid = False
        if len(data['password']) < 8:
            flash('Password must be at least 8 characters', 'registration')
            is_valid = False
        str1 = data['password']
        digits = 0
        uppers = 0
        for i in str1:
            if i.isdigit():
                digits += 1
            if i.isupper():
                uppers += 1
        if digits == 0:
            flash ('Password MUST contain at least one number!', 'registration')
            is_valid = False
        if uppers == 0:
            flash ('Password MUST contain at least ONE capital letter!', 'registration')
            is_valid = False
        return is_valid