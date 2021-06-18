import os
import pandas as pd

from app import db, UPLOAD_FOLDER
from app.models import Recipe, Ingredients, Cuisine
from flask import render_template, flash, request, redirect, send_file, url_for, current_app
from werkzeug.utils import secure_filename
from app.main.utils import get_recipe_ingredients
from app.main.forms import RecipeForm, SearchForm
from app.main import bp

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/add_recipe/', methods=['GET', 'POST'])
def add_recipe():
    form = RecipeForm()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if form.validate_on_submit():
            filename = secure_filename(form.file.data.filename)
            full_filepath = os.path.join(UPLOAD_FOLDER, filename)
            # full_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(full_filepath)
            ingredients_df = pd.read_csv(os.path.join('.', 'raw_ingredient_data', 'ingredient_list.csv'))
            ingredients_set = set(ingredients_df.iloc[:, 0])
            additional_ingredients = [i.strip() for i in request.form['optional_description'].split(',')]
            ingredients = get_recipe_ingredients(full_filepath, ingredients_set=ingredients_set,
                                                 additional_ingredients=additional_ingredients)

            if ingredients == 'Tesseract Error':
                flash('Sorry, filetype not recognized.  Please upload a .png, .jpg, or .jpeg.')
                return redirect('/add_recipe/')
            cuisine_info = [i.strip() for i in request.form.getlist('cuisine_type')]
            ingredients_text = ' '.join(ingredients)
            recipe = Recipe(recipe_name=request.form['recipe_name'], recipe_image_link=filename,
                            recipe_text=ingredients_text)
            db.session.add(recipe)
            for ingredient in ingredients:
                i = Ingredients(ingredient_name=ingredient, ingredient_type=recipe)
                db.session.add(i)
            for cuisine in cuisine_info:
                c = Cuisine(cuisine_type=cuisine, recipe_cuisine=recipe)
                db.session.add(c)
            db.session.commit()
            flash('Thanks for adding a recipe!')
            return redirect('/')

    return render_template('upload.html', form=form)


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    directory = os.path.join('..', 'uploads', filename)
    # directory = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    return send_file(directory, attachment_filename=filename)


@bp.route('/search')
# @login_required
def search():
    search_form = SearchForm()
    if not search_form.validate():
        return render_template('search_form.html', form=search_form)
    page = request.args.get('page', 1, type=int)
    try:
        recipes, total, matched_strings = Recipe.search(search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    except ValueError:
        flash('Sorry, no recipes exist with those keywords.')
        return redirect('/search')

    print(matched_strings)
    next_url = url_for('main.search', q=search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', recipes=recipes, matched_strings=matched_strings,
                           next_url=next_url, prev_url=prev_url)
