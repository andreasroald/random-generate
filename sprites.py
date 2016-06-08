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

        self.moving = False
        self.left_lock = False
        self.right_lock = False

        self.acceleration = 0
        self.x_top_speed = 6
        self.y_top_speed = 30
        self.x_velocity = 0
        self.y_velocity = 0

        self.jumping = False
        self.jump_rect = pygame.Rect((0, 0, 51, 35))
        self.should_jump = False

        self.direction = "right"

        self.space = False

        self.in_exit = False

        # Solid list is the sprite group that contains the walls
        self.solid_list = solid_list

    # Player class event handling
    def events(self):
        #Reset moving & acceleration
        self.moving = False
        self.acceleration = 0

        # Movement keys handling
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and not self.left_lock:
            self.right_lock = True
            self.moving = True
            self.acceleration = -settings.player_acc
            self.accelerate(self.acceleration)
        else:
            self.right_lock = False

        if keys[pygame.K_d] and not self.right_lock:
            self.left_lock = True
            self.moving = True
            self.acceleration = settings.player_acc
            self.accelerate(self.acceleration)
        else:
            self.left_lock = False

        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            if self.x_velocity != 0:
                self.moving = True
            self.accelerate(self.acceleration)

        # Check if space is still held
        if keys[pygame.K_SPACE]:
            self.space = True
        elif self.space:
            self.space = False

    # Accelerate the player movement with acc_movement
    def accelerate(self, acc_movement):
        if acc_movement > 0:
            if self.x_velocity >= self.x_top_speed:
                self.x_velocity = self.x_top_speed

            elif acc_movement < self.x_top_speed:
                self.x_velocity += acc_movement

        elif acc_movement < 0:
            if self.x_velocity <= -self.x_top_speed:
                self.x_velocity = -self.x_top_speed

            elif acc_movement > -self.x_top_speed:
                self.x_velocity += acc_movement

        # If x_velocity is not 0, slowly make x_velocity slower
        else:
            # Decelerate faster on ground (multiply by 3)
            if self.x_velocity > 0:
                if self.x_velocity - settings.player_acc * 3 > 0:
                    self.x_velocity -= settings.player_acc * 3
                else:
                    self.x_velocity -= settings.player_acc
            elif self.x_velocity < 0:
                if self.x_velocity + settings.player_acc * 3 < 0:
                    self.x_velocity += settings.player_acc * 3
                else:
                    self.x_velocity += settings.player_acc

    # Make the player jump
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.y_velocity = -15

    # If space is pressed and the jump rect is touching the ground, jump automaticly right after landing
    # This makes the game feel more responsive and prevents the "aw shit i pressed space why didnt i jump" - situations
    def test_for_jump(self):
        for tiles in self.solid_list:
            if self.jump_rect.colliderect(tiles.rect):
                self.should_jump = True
                break

    # Movement and collision detection
    def movement(self):
        self.events()

        # Change direciton based on velocity
        if self.x_velocity > 0:
            self.direction = "right"
        if self.x_velocity < 0:
            self.direction = "left"

        # X-Axis movement
        if self.moving:
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
        # If loop doesnt break, then player is in-air and shouldnt be able to jump (unless wall-hugging)
        else:
            self.jumping = True

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

    # Update the player class
    def update(self):
        self.movement()

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
