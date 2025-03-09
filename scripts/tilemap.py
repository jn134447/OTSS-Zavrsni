import pygame
import os
import json

# NEIGHBOR_OFFSETS = [(-1, -1), (0, -1), (1, -1),
#                     (-1, 0),           (1, 0),
#                     (-1, 1),  (0, 1),  (1, 1)
#                    ]
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICAL_TILES = {'space_ship_ground'}

BASE_LEVEL_DATA_PATH = 'data/level_data/'

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.render_distance = 2
        
        self.world_folders = os.listdir(BASE_LEVEL_DATA_PATH)            
        # self.level_files = os.listdir(BASE_LEVEL_DATA_PATH + self.world_folders[self.selected_world_folder])
        
    def load_level(self, world_and_level_index):
        self.level_files = sorted(os.listdir(BASE_LEVEL_DATA_PATH + self.world_folders[world_and_level_index[0]]))
        with open(BASE_LEVEL_DATA_PATH + self.world_folders[world_and_level_index[0]] + '/' + self.level_files[world_and_level_index[1]], 'r') as json_file:
            json_file_loaded = json.load(json_file)
        self.tilemap = json_file_loaded    
        
        
    
    def tiles_around(self, pos, entity_type):
        pos = eval('self.game.' + entity_type + '.center_pos')
        if pos == None:
            return []
        tiles_around_middle = []
        tile_location_middle = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_location = str(tile_location_middle[0] + offset[0]) + ';' + str(tile_location_middle[1] + offset[1])
            if check_location in self.tilemap:
                tiles_around_middle.append(self.tilemap[check_location])
        
        return tiles_around_middle
        
    
    def physics_rect_around(self, pos, entity_type):
        pos = eval('self.game.' + entity_type + '.center_pos')
        rects = []
        if pos == None:
            return rects
        for tile in self.tiles_around(pos, entity_type):
            if tile['type'] in PHYSICAL_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size)) 
        return rects
    
    def render(self, surface, camera_offset=(0, 0)):
        # Off-grid tile render (not dependant on render_distance)
        for tile in self.offgrid_tiles:
            surface.blit(pygame.transform.rotate(self.game.assets[tile['type']][tile['variant']], tile['rotation'] * -90), (tile['pos'][0] - camera_offset[0], 
                                                                                                                            tile['pos'][1] - camera_offset[1]))
        
        # On-Grid Tile Render (Render in camera prox)
        for x in range(camera_offset[0] // self.tile_size, (camera_offset[0] + surface.get_width()) // self.tile_size + self.render_distance):
            for y in range(camera_offset[1] // self.tile_size, (camera_offset[1] + surface.get_height()) // self.tile_size + self.render_distance):
                location = str(x) + ';' + str(y)
                if location in self.tilemap:
                    tile = self.tilemap[location]
                    surface.blit(pygame.transform.rotate(self.game.assets[tile['type']][tile['variant']], tile['rotation'] * -90), (tile['pos'][0] * self.tile_size - camera_offset[0], 
                                                                                                                                    tile['pos'][1] * self.tile_size - camera_offset[1]))

            # Nested Dictionary for PNGs, for exemple...
            # self.game.assets[ [space_ship_ground] [1] ]
            # gives the 2nd image from the (sorted) system Directory search
            # space_ship_grounds > 00.png           
            #                > 01.png [Picked]
            #                > 02.png
