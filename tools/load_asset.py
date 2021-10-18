import os 
import pygame
from pygame.image import save

GAME_FOLDER = os.path.join(os.path.dirname(__file__), "..")
SPRITE_FOLDER = os.path.join(GAME_FOLDER, "Assets", "Sprites")
SOUND_FOLDER = os.path.join(GAME_FOLDER, "Assets", "Sounds")
FONT_FOLDER = os.path.join(GAME_FOLDER, "Assets", "Fonts")
UI_FOLDER = os.path.join(GAME_FOLDER, "Assets", "UI")

file_cache = {}

def load_image(name, scale=1, save_cache=True):
    """ Load image and return image object"""
    fullname = os.path.join(SPRITE_FOLDER, name)
    try:
        if file_cache.get(fullname) is not None:
            image = file_cache.get(fullname)
        else:
            image = pygame.image.load(fullname)
            if save_cache:
                file_cache[fullname] = image

        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()

        image = pygame.transform.scale(image,
                                       (int(image.get_rect().width * scale), int(image.get_rect().height * scale)))
    except (pygame.error):
        print('Cannot load image:', fullname)
        raise SystemExit
    return image, image.get_rect()


def load_sound(name):
    fullname = os.path.join(SOUND_FOLDER, name)
    try:
        if file_cache.get(fullname) is not None:
            sound = file_cache.get(fullname)
        else:
            sound = pygame.mixer.Sound(fullname)
            file_cache[fullname] = sound
    except (pygame.error):
        print('Cannot load sound:', fullname)
        raise SystemExit
    return sound


def load_all_image(dir):
    result = []
    for filename in os.listdir(os.path.join(SPRITE_FOLDER, dir)):
        result.append(load_image(os.path.join(dir, filename), save_cache=True))
    return result

def load_all_image_not_cache(dir, scale=1):
    result = []
    for filename in os.listdir(os.path.join(SPRITE_FOLDER, dir)):
        result.append(load_image(os.path.join(dir, filename), save_cache=False, scale=scale))
    return result


