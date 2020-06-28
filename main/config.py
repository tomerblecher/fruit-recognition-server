from main.learner import Learner
from main.utils.utils_func import *


class Config:
    def __init__(self):
        self.path = {
            'tokens': 'data/tokens.json',
            'labels': 'data/lable_json.json',
            'nutrition_db': 'data/nutrition_db.json',
            'client_config': 'data/client_config.json',
            'img_folder': 'data/imgs/'
        }
        # Path for the images.
        # self.img_folder = "data/imgs"
        self.tokens = []
        self.nutrition = []
        self.learn = Learner('data', load_json(self.path['labels']))
        self.tokens = load_json(self.path['tokens'])
        self.nutrition = load_json(self.path['nutrition_db'])
