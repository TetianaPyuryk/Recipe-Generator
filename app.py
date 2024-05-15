from flask import Flask, render_template, request, redirect, url_for, make_response, session, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from config.db import engine, user_table, recipe_table
from sqlalchemy.exc import IntegrityError
from passlib.hash import sha256_crypt
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('API_KEY')

tokenizer = GPT2Tokenizer.from_pretrained("./gpt2-tokenizer")
model = GPT2LMHeadModel.from_pretrained("./gpt2-fine-tuned")
tokenizer.pad_token_id = tokenizer.eos_token_id

@app.route('/')
def home():
    return render_template('index.html', recipe='')

@app.route('/', methods=['POST'])
def get_recipe():
    ingredients = request.form['ingredients']
    prompt_text = f"[Q] Ingredients: {ingredients}"
    input_ids = tokenizer.encode(prompt_text, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_length=100,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=2,
        num_beams=3,
    )
    decoded_text = tokenizer.decode(output[0], skip_special_tokens=True)
    recipe = decoded_text.split('\n\n')[0]
    return render_template('index.html', recipe=recipe)

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/sign_up', methods=['POST'])
def sign_up_post():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm-password']

    if password != confirm_password:
        error_message = 'Passwords do not match. Please try again'
        return render_template('sign_up.html', error_message=error_message)

    hashed_password = sha256_crypt.hash(password)

    with engine.connect() as connection:
        try:
            insert_query = user_table.insert().values(username=username, password=hashed_password).returning(user_table.c.id)
            result = connection.execute(insert_query)
            connection.commit()
            user_id = result.fetchone()[0]
            session['user_id'] = user_id

            response = make_response(redirect(url_for('home')))
            response.set_cookie('logged_in', 'true')
            return response

        except IntegrityError:
            error_message = 'Username already exists. Please choose a different one'
            return render_template('sign_up.html', error_message=error_message)

        except Exception:
            error_message = 'An error occurred. Please try again later'
            return render_template('sign_up.html', error_message=error_message)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    with engine.connect() as connection:
        try:
            select_query = user_table.select().where(user_table.c.username == username)
            result = connection.execute(select_query)
            user = result.fetchone()
        except Exception:
            error_message = 'An error occurred. Please try again later'
            return render_template('login.html', error_message=error_message)

    if user:
        stored_password = user.password

        if sha256_crypt.verify(password, stored_password):
            response = make_response(redirect(url_for('home')))
            response.set_cookie('logged_in', 'true')
            session['user_id'] = user.id
            return response

    error_message = 'Invalid username or password. Please try again'
    return render_template('login.html', error_message=error_message)

@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    recipe = data.get('recipe')
    user_id = session['user_id']

    if not recipe:
        return jsonify({'error': 'Recipe not provided'}), 400

    parts = recipe.split('\n')
    if len(parts) < 2:
        return jsonify({'error': 'Invalid recipe format'}), 400

    ingredients, directions = parts

    with engine.connect() as connection:
        try:
            insert_query = recipe_table.insert().values(
                ingredients=ingredients.strip(),
                directions=directions.strip(),
                user_id=user_id
            ).returning(recipe_table.c.id)
            result = connection.execute(insert_query)
            connection.commit()
            recipe_id = result.fetchone()[0]
            session['recipe_id'] = recipe_id
            return jsonify({'message': 'Recipe saved successfully'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/delete_recipe', methods=['DELETE'])
def delete_recipe():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    if 'recipe_id' not in session:
        return jsonify({'error': 'Recipe ID not provided'}), 400

    recipe_id = session['recipe_id']
    user_id = session['user_id']

    with engine.connect() as connection:
        try:
            delete_query = recipe_table.delete().where(recipe_table.c.id == recipe_id, recipe_table.c.user_id == user_id)
            result = connection.execute(delete_query)

            if result.rowcount == 0:
                return jsonify({'error': 'Recipe not found'}), 404

            connection.commit()
            session.pop('recipe_id', None)
            return jsonify({'message': 'Recipe deleted successfully'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/my_recipes')
def get_recipes():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']

    with engine.connect() as connection:
        try:
            select_query = recipe_table.select().where(recipe_table.c.user_id == user_id)
            result = connection.execute(select_query)
            recipes = result.fetchall()

            recipes_dict = {}
            for recipe_id, ingredients, directions, user_id in recipes:
                recipes_dict[recipe_id] = ingredients

            return render_template('user_recipes.html', recipes=recipes_dict)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/my_recipes/<int:recipe_id>')
def get_directions(recipe_id):
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']

    with engine.connect() as connection:
        try:
            select_query = recipe_table.select().where(
                (recipe_table.c.user_id == user_id) & (recipe_table.c.id == recipe_id)
            )
            result = connection.execute(select_query)
            recipe = result.fetchone()

            if not recipe:
                return jsonify({'error': 'Recipe not found'}), 404

            directions = recipe[2]
            return jsonify({'directions': directions}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)