"""
    services/text_assignment.py
    
    Take in full text and create a JSON represenation of a recipe object with related steps and ingredients.
"""

from logging import getLogger

logger = getLogger(__name__)


def assign_text_to_recipe(full_text: str) -> dict:
    """
        Take in full text and create a JSON represenation of a recipe object with related steps and ingredients.
    """
    logger.info('Assigning text to recipe: {}'.format(full_text))

    return {
        'title': "Mama Tucci's Pasta",
        'ingredients': [
            {'number': 1, 'name': 'Flour', 'quantity': '2', 'unit': 'cups'},
            {'number': 2, 'name': 'Eggs (whipped)',
             'quantity': '2', 'unit': ''},
            {'number': 3, 'name': 'Salt', 'quantity': '1', 'unit': 'teaspoon'},
        ],
        'steps': [
            {'number': 1, 'text': 'Mix flour and salt in a bowl.'},
            {'number': 2, 'text': 'Create a well in the center of the bowl.'},
            {'number': 3, 'text': 'Pour egg mixture into the well.'},
        ]
    }
