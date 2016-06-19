import pygame
import random

import settings

# Player class
class Player(pygame.sprite.Sprite):
    # Initialize the player class
    def __init__(self, x, y, solid_list):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((32, 64))
        self.image.fill((settings.blue))
        self.image_rect = self.image.get_rect()
        self.image_rect.center = (-1000, -1000)
        self.rect = self.image_rect.copy()
        self.rect.x, self.rect.y = (x, y)

        self.left_lock = False
        self.right_lock = False

        self.acceleration = 0
        self.x_top_speed = 6
        self.y_top_speed = 30
        self.x_velocity = 0
        self.y_velocity = 0

        self.jumping = False
        self.jump_rect = pygame.Rect((0, 0, 32, 35))
        self.should_jump = False

        self.direction = "right"

        self.cam_direction = "middle"

        self.space = False

        self.in_exit = False

        # Ghost jump variables
        self.previous = (0, 0) # Index 0 is previous jumping state (True/False), 1 is last y-coordinate
        self.ghost_jump = False
        self.ghost_jump_started = 0

        # Solid list is the sprite group that contains the walls
        self.solid_list = solid_list

    # Make the player jump
    def jump(self):
        if not self.jumping or self.ghost_jump:
            self.jumping = True

            self.y_velocity = -15

    # If space is pressed and the jump rect is touching the ground, jump automaticly right after landing
    def test_for_jump(self):
        for tiles in self.solid_list:
            if self.jump_rect.colliderect(tiles.rect):
                self.should_jump = True
                break

    def update(self):
        #Reset moving & acceleration
        self.acceleration = 0

        self.previous = (self.jumping, self.rect.y)

        # Movement keys handling
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LSHIFT] and not self.jumping:
            self.x_top_speed = 10
        if not keys[pygame.K_LSHIFT]:
            self.x_top_speed = 6

        if keys[pygame.K_a] and not self.left_lock:
            self.right_lock = True

            self.acceleration = -settings.player_acc

            # Switch direction faster
            if self.x_velocity > 0:
                self.x_velocity += self.acceleration + self.acceleration * settings.reactivity_percent
            else:
                self.x_velocity += self.acceleration

            self.x_velocity = max(self.x_velocity, -self.x_top_speed)

        else:
            self.right_lock = False

        if keys[pygame.K_d] and not self.right_lock:
            self.left_lock = True

            self.acceleration = settings.player_acc

            # Switch direciton faster
            if self.x_velocity < 0:
                self.x_velocity += self.acceleration + self.acceleration * settings.reactivity_percent
            else:
                self.x_velocity += self.acceleration

            self.x_velocity = min(self.x_velocity, self.x_top_speed)

        else:
            self.left_lock = False

        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            if self.x_velocity > 0:
                self.x_velocity -= settings.player_acc * 2
            if self.x_velocity < 0:
                self.x_velocity += settings.player_acc * 2

        # Check if space is still held
        if keys[pygame.K_SPACE]:
            self.space = True
        elif self.space:
            self.space = False

        # Change direciton based on velocity
        if self.x_velocity > 0:
            self.direction = "right"
        if self.x_velocity < 0:
            self.direction = "left"

        # X-Axis movement
        self.rect.x += self.x_velocity

        # Check if the player hit any walls during X-movement
        hit_list = pygame.sprite.spritecollide(self, self.solid_list, False)
        for hits in hit_list:
            # If top solid is true, the tile can be moved through on the X-Axis
            if self.direction == "right":
                self.rect.right = hits.rect.left
                self.x_velocity = settings.player_acc # Set x_velocity to settings.player_acc/-settings.player_acc so that x_velocity doesnt build up

            elif self.direction == "left":
                self.rect.left = hits.rect.right
                self.x_velocity = -settings.player_acc

        # Y-Axis Movement
        if self.y_velocity < self.y_top_speed:
            self.y_velocity += settings.player_grav

        self.rect.y += self.y_velocity

        # Cut jump if space is not pressed
        if self.y_velocity < -5:
            if not self.space:
                self.y_velocity = -5

        # Check if the player hit any walls during Y-movement
        hit_list = pygame.sprite.spritecollide(self, self.solid_list, False)
        for hits in hit_list:
            if self.y_velocity > 0:
                self.rect.bottom = hits.rect.top
                self.y_velocity = settings.player_grav # Set y_velocity to settings.player_grav so that y_velocity doesnt build up
                self.jumping = False

                if self.should_jump:
                    self.jump()
                    self.should_jump = False

                break
            elif self.y_velocity < 0:
                self.rect.top = hits.rect.bottom
                self.y_velocity = 0
                self.jumping = True
                break
        # If loop doesnt break, then player is in-air and shouldnt be able to jump
        else:
            self.jumping = True

        # Ghost-jumping
        if not self.previous[0] and self.jumping:
            if self.rect.y > self.previous[1]:
                self.ghost_jump = True
                self.ghost_jump_started = pygame.time.get_ticks()

        if self.ghost_jump:
            if pygame.time.get_ticks() - self.ghost_jump_started > 100:
                self.ghost_jump = False

        # Only auto jump if jump rect collides with the ground all the time
        if self.should_jump:
            for tiles in self.solid_list:
                if self.jump_rect.colliderect(tiles.rect):
                    break
            else:
                self.should_jump = False

        # Reposition jump Rect
        self.jump_rect.center = self.rect.center
        self.jump_rect.top = self.rect.bottom

        # Reposition image drawing rect
        self.image_rect.center = self.rect.center
        self.image_rect.bottom = self.rect.bottom

    # Player drawing function
    def draw(self, display):
        display.blit(self.image, self.image_rect)

# Wall class
class Wall(pygame.sprite.Sprite):
    # Initialize the wall class
    def __init__(self, x, y, w, h, color=settings.black, image=None):
        pygame.sprite.Sprite.__init__(self)
        if image is None:
            self.image = pygame.Surface((w, h))
            self.image.fill(color)
        else:
            self.image = image

        self.image.convert_alpha()

        self.dead = False

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Camera sprite that follows the player smoothly (does not handle the game scrolling)
class Camera(pygame.sprite.Sprite):
    # Initialize the camera class
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)

        self.player = player

        self.camera_align = "middle"

        self.rect = pygame.Rect((self.player.rect.x, self.player.rect.y, 40, 40))

    def update(self):
        self.rect.x += (self.player.rect.x - self.rect.x) * 0.1

        self.rect.y += (self.player.rect.y - self.rect.y) * 0.1
