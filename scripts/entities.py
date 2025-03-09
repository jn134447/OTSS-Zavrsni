import pygame

class PhysicsEntity:
    def __init__(self, game, entity_type, pos, size, speed = 1):
        self.game = game
        
        # Physical Properties
        self.type = entity_type
        self.pos = list(pos)
        self.size = size
        self.base_size = tuple(self.size)
        self.base_pos = tuple(self.pos)
    
        # Movement
        self.velocity = [0, 0]
        self.gravity = 0.2
        self.terminal_velocity = 5
        self.speed = speed
        self.collisions = {'up': False, 'down': False,
                           'left': False, 'right': False}
        
        # Animation
        self.action = ''
        self.animation_offset = (0, 0)
        self.flip_x = False
        self.flip_y = False
        self.set_action('idle')
        
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            self.animation_offset = (self.size[0] - self.animation.frame_width,
                                     self.size[1] - self.animation.frame_height)
            
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        
    def update(self, tilemap, movement=(0,0), speed = 1):
        
        self.center_pos = (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2)
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        
        frame_movement = (movement[0] + self.velocity[0], # movement[1]
                          self.velocity[1]) 
        
        
        self.pos[0] += frame_movement[0] * speed
        # Collision Y
        entity_rect = self.rect()
        for rect in tilemap.physics_rect_around(self.pos, self.type):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        
        self.pos[1] += frame_movement[1] # * speed
        # Collision X
        entity_rect = self.rect()
        for rect in tilemap.physics_rect_around(self.pos, self.type):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        # Gravity
        self.velocity[1] = min(self.terminal_velocity, self.velocity[1] + self.gravity)
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        # Flip
        if frame_movement[0] > 0:
            self.flip_x = False
        if frame_movement[0] < 0:
            self.flip_x = True
            
        # Animation
        self.animation.update()
            
    def render(self, surface, camera_offset=(0, 0), debug_hitbox_show = False):
        surface.blit(pygame.transform.flip(self.animation.extract_sprite(0, 0, self.animation.frame_width, self.animation.frame_height), self.flip_x, self.flip_y),
                     (int(self.pos[0]) - camera_offset[0] + self.animation_offset[0],
                      int(self.pos[1]) - camera_offset[1] + self.animation_offset[1]))
        
        # Hitbox Show
        if debug_hitbox_show:
            hitbox_rect = pygame.Surface((self.size))
            hitbox_rect.fill((255, 0, 0))
            surface.blit(hitbox_rect, (int(self.pos[0]) - camera_offset[0],
                                       int(self.pos[1]) - camera_offset[1])) 
            
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        
        # Initiate Jumping Variables
        self.used_jump = False
        self.canceled_jump = False
        self.air_time = 0
        self.COYOTE_EFFECT_TIME_FRAME = 7
        self.BASE_JUMP_STRENGHT = 5
          
        self.BASE_SPEED = 2
        self.ducking = False
        
    def update(self, tilemap, movement=(0, 0), speed=1):
        super().update(tilemap, movement, speed)
        
        self.speed = self.BASE_SPEED
        self.jump_strenght = self.BASE_JUMP_STRENGHT
        

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.used_jump = False
            self.canceled_jump = False
        
        # Animation Logic
        if movement[1] == 1:
            if movement[0] != 0:
                self.set_action('duck_run')
            else:
                self.set_action('duck')
        elif self.air_time >= 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        elif movement[0] == 0:
            self.set_action('idle')

    def register_input_events(self):
        # Make inputs last until start of a new update loop (game loop)
        self.movement = [0, 0]
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:    
            self.speed = self.BASE_SPEED * 0.5
            self.jump_strenght = self.BASE_JUMP_STRENGHT * 0.75
            self.movement[1] = 1
        if keys[pygame.K_DOWN] == False and self.ducking == True:
            self.pos[1] += 9
        if keys[pygame.K_UP] and self.air_time <= self.COYOTE_EFFECT_TIME_FRAME:
            if self.used_jump == False:
                self.canceled_jump = False
                self.used_jump = True
                self.velocity[1] = - self.jump_strenght
        if keys[pygame.K_UP] == False and self.used_jump == True:
            if self.canceled_jump == False and self.velocity[1] < 0:
                self.canceled_jump = True
                self.velocity[1] *= 0.3
        if keys[pygame.K_LEFT]:
            self.movement[0] = -1
        if keys[pygame.K_RIGHT]:
            self.movement[0] = 1
        
           
class Coin(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'coin', pos, size)
        self.collected = False
        
    def update(self, tilemap, movement=(0, 0), speed=0):
        super().update(tilemap, movement, speed)
        self.velocity[0] = 0
        self.velocity[1] = 0
        
        if self.rect().colliderect(self.game.player.rect()):
            self.next_level()
        
    def next_level(self):
        if self.collected == True:
            return None
        if self.game.current_world_and_level[1] >= 3:
            self.game.current_world_and_level[1] = 0
            self.game.current_world_and_level[0] += 1
        else: 
            self.game.current_world_and_level[1] += 1
        self.collected = True
        
















