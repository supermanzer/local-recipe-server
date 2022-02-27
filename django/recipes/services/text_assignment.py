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
        'title': '',
        'ingredients': [],
        'steps': []
    }
