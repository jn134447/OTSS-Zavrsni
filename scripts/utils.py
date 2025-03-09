import pygame
import json
import os

BASE_IMG_PATH = 'data/images/'
BLACK = (0, 0, 0)

def json_into_dictionary(path):
    dictionary = {}
    with open(BASE_IMG_PATH + path, 'r') as json_file:
        json_file_loaded = json.load(json_file)
    dictionary = json_file_loaded
    return dictionary

def create_images_from_spritesheet(spritesheet, w, h, frame_total = 1):
    images = []
    single_frame = pygame.Surface((w, h))
    for current_frame in range(frame_total):
        single_frame.fill(BLACK)
        single_frame.blit(spritesheet, (0, 0), (w * current_frame, 0, w, h))
        single_frame.set_colorkey(BLACK)
        images.append(single_frame)
    return images

    
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    img.set_colorkey(BLACK)
    return img

def load_images(path):
    images = []
    for img_names in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_names))
    return images
    
