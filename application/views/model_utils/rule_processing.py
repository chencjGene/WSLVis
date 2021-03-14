import numpy as np
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import pickle_load_data, pickle_save_data
from application.views.model_utils import WSLModel

def rule_process(idx, logits, activations, strings):
    # number
    y_pred = [x > 0 for x in logits]
    label_names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 
        'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'zebra', 'giraffe', 'backpack', 'umbrella', 
        'handbag', 'tie', 'suitcase', 'skis', 'kite', 'baseball bat', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 
        'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 
        'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 
        'laptop', 'keyboard', 'cell phone', 'oven', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'teddy bear']
    rules = {
        'train_forbidden_words_rules': {
            'person': ['terminal', 'trailers', 'tossed'], 
            'car': ['thru', 'county', 'wih', 'hoodie', 'vehicles', 'double-decker', 'windshield'], 
            'bottle': ['banquet', 'cafeteria', 'coke'], 
            'wine glass': ['celebratory'], 
            'cup': ['beverage', 'drinks', 'breakfast', 'stools', 'cafeteria', 'toiletries', 'diced', 'chili'], 
            'knife': ['diced'], 
            'bowl': ['marinara'], 
            'chair': ['fedora', 'gymnasium', 'tables', 'tents', 'apartment', 'dining', 'patio', 'galley'], 
            'couch': ['wii'], 
            'potted plant': ['wih'], 
            'dining table': ['cake', 'roast', 'pie'], 
            'clock': ['nightstand'], 
            'tie': ['wedding', 'bride', 'groom'], 
            'keyboard': ['desktop']
        }, 
        'valid_forbidden_words_rules': {
            'person': ['cutlery', 'amusement', 'trailers', 'terminal', 'mans', 'cranberry', 'pineapple', 'decker', 'rig', 
                'metro', 'mall', 'advertisements', 'walked', 'alcoholic', 'airways', 'fondant', 'streets', 'stoplight', 'onlookers', 
                'storefront', 'wheeled', 'booze', 'automobiles', 'crooked'], 
            'car': ['tractor', 'hoodie', 'thru', 'windy', 'dodge', 'rainy', 'bmw', 'downtown', 'streets', 'auto', 'trailers', 
                'mopeds', 'windshield', 'cop', 'scooters', 'motorbikes', 'double-decker', 'launches'], 
            'truck': ['vandalized', 'launches'], 
            'backpack': ['families', 'hikers', 'peddling', 'commuters'], 
            'umbrella': ['coconut', 'amusement', 'vendors'], 
            'handbag': ['sidewalks', 'planters', 'costumed', 'purse'], 
            'bottle': ['beers', 'essentials', 'cafeteria', 'coke', 'toiletries'], 
            'wine glass': ['hearty', 'champagne'], 
            'cup': ['diced', 'mango', 'sip', 'tea', 'chili', 'canned', 'pickles', 'toiletries', 'aquarium', 'celebratory', 
                'snacks', 'drinks', 'beverage', 'stools', 'breakfast', 'beverages'], 
            'fork': ['entrees', 'mango', 'hash', 'diced', 'quiche'], 
            'knife': ['diced'], 
            'spoon': ['platters', 'stew'], 
            'bowl': ['marinara', 'cooker', 'steaming', 'pineapple', 'banquet', 'champagne'], 
            'hot dog': ['meatball'], 
            'cake': ['desserts', 'cookies'], 
            'chair': ['football', 'auditorium', 'apartment', 'pong', 'bedding', 'patio', 'tables', 'essentials', 'gymnasium', 'dr', 'fedora', 'apartments', 'rag', 'dining'], 
            'couch': ['comfy', 'wii'], 
            'potted plant': ['essentials', 'tp', 'seating', 'dr', 'planter', 'cranberry', 'newlywed', 'planted', 'birdcage'], 
            'dining table': ['entrees', 'crackers', 'luncheon', 'cutlery', 'pie', 'cake', 'pantry', 'menu', 'breakfast', 'dr'], 
            'book': ['halloween', 'cigarettes', 'notebook', 'stocked'], 
            'clock': ['guided', 'barber', 'microwaves', 'nurse', 'teacher'], 
            'vase': ['champagne']
        }, 
        'forbidden_words_rules': {
        }, 
        'additional_words_rules': {
        }
    }
    for label_name in rules['forbidden_words_rules']:
        label_id = label_names.index(label_name)
        if y_pred[label_id]:
            y_pred[label_id] = False
            for support_word in activations:
                if label_id in support_word['cats'] and support_word["text"] not in rules['forbidden_words_rules'][label_name]:
                    y_pred[label_id] = True
                    break
    for label_name in rules['additional_words_rules']:
        label_id = label_names.index(label_name)
        if not y_pred[label_id]:
            for word in strings:
                if word in rules['additional_words_rules'][label_name]:
                    y_pred[label_id] = True
                    break
    
    return y_pred