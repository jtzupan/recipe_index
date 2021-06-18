import pytesseract
import string
from typing import List, Set


def get_recipe_ingredients(recipe_image_path: str, ingredients_set: Set[str], additional_ingredients: List[str]):
    """Given a path to a recipe, extract any ingredients from the known ingredient list
    """
    # In order to bypass the image conversions of pytesseract, just use relative or absolute image path
    # NOTE: In this case you should provide tesseract supported images or tesseract will return error
    try:
        recipe = pytesseract.image_to_string(recipe_image_path)
        recipe = recipe.lower().translate(str.maketrans('', '', string.punctuation))
        recipe = recipe.translate(str.maketrans('', '', string.digits))
        recipe = recipe.replace('\n', ' ')
        recipe_list = recipe.split()
        recipe_list.extend(additional_ingredients)
        word_set = set(recipe_list)
        ingredients = list(word_set.intersection(ingredients_set))
    except:
        return 'Tesseract Error'
    return ingredients
