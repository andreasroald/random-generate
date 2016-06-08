import pygame
import random

import sprites
import settings
import resources
import templates

# State template class
class States(object):
    # Initialize the states class
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

# Level template class
class Level(States):
    # Initialize the game state
    def __init__(self):
        States.__init__(self)

        # If quit on exit is true, the game will reset instead of going to the next level when exiting
        self.quit_on_exit = False

    # Function that generates a level randomly
    def generate_level(self):
        # Creating the solution path list
        level = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        row = 0
        # Placing the entrance randomly
        col = random.randint(0, 3)

        level[row][col] = 1

        # Set this to -1, and left will become right, and vice versa
        step = 1

        while True:
            direction = random.randint(1, 5)

            previous = (row, col)

            if direction == 1 or direction == 2:
                col -= step
            elif direction == 3 or direction == 4:
                col += step
            else:
                row += 1

            if col < 0:
                col += 1
                row += 1

                # Switching direction
                if step > 0:
                    step = -1
                if step < 0:
                    step = 1

            if col > 3:
                col -= 1
                row += 1

                # Switching direction
                if step > 0:
                    step = -1
                if step < 0:
                    step = 1

            if row > 3:
                break

            if previous[0] < row:
                level[previous[0]][previous[1]] = 2
                level[row][col] = 3
            elif level[row][col] == 0:
                level[row][col] = 1

        # Place the outer walls
        border_top = sprites.Wall(0, 0, 66*32, 32)
        border_left = sprites.Wall(0, 0, 32, 66*32)
        border_bottom = sprites.Wall(0, 65*32, 66*32, 32)
        border_right = sprites.Wall(65*32, 0, 32, 66*32)

        self.walls.add(border_top)
        self.walls.add(border_left)
        self.walls.add(border_bottom)
        self.walls.add(border_right)

        # Generating the level
        current_template = None

        level_x = 32
        level_y = 32

        exit = True

        for rows in level:
            for cols in rows:
                # Switching to the correct template
                if cols == 0:
                    current_template = templates.templates_all[random.randrange(0, len(templates.templates_all))]
                else:
                    # Reset players spawn position each time a solution path room is made
                    # so that the last room of the solution path is the players spawn point
                    self.player_x = level_x +  16 * 32 / 2
                    self.player_y = level_y +  16 * 32 / 4

                    if cols == 1:
                        current_template = templates.templates_lr[random.randrange(0, len(templates.templates_lr))]
                    elif cols == 2:
                        current_template = templates.templates_tlbr[random.randrange(0, len(templates.templates_tlbr))]
                    elif cols == 3:
                        current_template = templates.templates_tlr[random.randrange(0, len(templates.templates_tlr))]

                temp_level_x = level_x
                temp_level_y = level_y

                # Randomly flip the template
                if random.randint(0, 1) == 1:
                    for flip in current_template:
                        flip.reverse()

                # Creating the level
                for temp_rows in current_template:
                    for temp_cols in temp_rows:
                        if temp_cols == 1:
                            w = sprites.Wall(temp_level_x, temp_level_y, 32, 32)
                            self.walls.add(w)
                        if temp_cols == -1 and exit:
                            w = sprites.Wall(temp_level_x, temp_level_y, 32, 64, settings.green)
                            self.exits.add(w)
                            exit = False # Place exit in first room placed
                        if temp_cols == 2:
                            w = sprites.Wall(temp_level_x, temp_level_y, 32, 32, image=resources.ladder)
                            self.ladders.add(w)

                        temp_level_x += 32
                    temp_level_x = level_x
                    temp_level_y += 32

                level_x += 16 * 32
            level_x = 32
            level_y += 16 * 32

    # Starting the Level state
    def init_level(self):
        # Sprite groups
        self.exits = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

        # PLayer position variables
        self.player_x = 0
        self.player_y =  0

        # Generate the level
        self.generate_level()

        # Creating an instance of the player
        self.player = sprites.Player(self.player_x, self.player_y, self.walls)

        self.max_y_offset = (66 - 20) * 32

        # We blit surfaces to the world surface, then blit the world surface to the game display
        self.world_surface = pygame.Surface((66*32, 66*32))

        # Camera variables
        self.cam_x_offset = 0
        self.cam_y_offset = self.max_y_offset

        # Screen shake variables
        self.shake_amount = 10

    # Common events function
    def events(self, event):
        if event.type == pygame.QUIT:
            self.quit = True

        if event.type == pygame.KEYDOWN:
            # Player jumping
            if event.key == pygame.K_SPACE:
                if self.player.jumping:
                    self.player.test_for_jump()
                else:
                    self.player.jump()

            # Go to next level if player is standing within the exit
            if event.key == pygame.K_w and self.player.in_exit:
                if not self.quit_on_exit:
                    self.done = True
                else:
                    self.quit = True

    # Common updates function
    def updates(self):
        # Horizontal Camera scrolling
        self.cam_x_offset = self.player.rect.x - settings.display_width / 2

        self.cam_x_offset = max(0, self.cam_x_offset)
        self.cam_x_offset = min(((66 - 25) * 32, self.cam_x_offset))

        # Vertical Camera scrolling
        self.cam_y_offset = self.player.rect.center[1] - settings.display_height / 2

        self.cam_y_offset = max(0, self.cam_y_offset)
        self.cam_y_offset = min(self.max_y_offset, self.cam_y_offset)

        # Slowly stop screen shake
        if self.shake_amount > 0:
            self.shake_amount -= 0.5

        # If player is out of view, reset the game
        if self.player.rect.top > 64 * 32:
            self.startup()

    # Common draws function
    def draws(self, screen):
        self.world_surface.blit(resources.brick_background, (32, 32))

        # Draw the player, walls and exits
        self.exits.draw(self.world_surface)
        self.walls.draw(self.world_surface)
        self.player.draw(self.world_surface)

        # Blit the world surface to the main display
        # If shake amount is more than 0, blit the world at a random location between
        # negative and positive shake amount, instead of 0, 0
        if self.shake_amount > 0:
            screen.blit(self.world_surface, (random.randint(int(-self.shake_amount), int(self.shake_amount))-self.cam_x_offset,
                                             random.randint(int(-self.shake_amount), int(self.shake_amount))-self.cam_y_offset))
        else:
            screen.blit(self.world_surface, (0-self.cam_x_offset, 0-self.cam_y_offset))

    # Test if the player is within an exit's boundaries
    def test_for_exits(self, player):
        for exits in self.exits:
            if exits.rect.colliderect(player.rect):
                self.player.in_exit = True
                break
            else:
                self.player.in_exit = False

# Menu state
class Menu(States):
    # Initialize the menu state
    def __init__(self):
        States.__init__(self)
        self.next = "level_1"

        self.startup()

    # Font rendering function
    def render_text(self, msg, color, size, dest_surf, pos):
        font = pygame.font.Font(settings.font_file, size)

        font_surf = font.render(msg, False, color)
        font_rect = font_surf.get_rect()
        font_rect.center = pos

        dest_surf.blit(font_surf, font_rect)

    # Cleaning up the menu state
    def cleanup(self):
        pass

    # Starting the menu state
    def startup(self):
        self.play_color = settings.orange
        self.quit_color = settings.black

        self.selected = "play"

    # State event handling
    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.selected = "play"
            if event.key == pygame.K_s:
                self.selected = "quit"
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected == "play":
                    self.done = True
                if self.selected == "quit":
                    pygame.quit()
                    quit()

    # Update the menu state
    def update(self, display):
        self.draw(display)

        if self.selected == "play":
            self.play_color = settings.orange
        else:
            self.play_color = settings.black

        if self.selected == "quit":
            self.quit_color = settings.orange
        else:
            self.quit_color = settings.black

    # Menu state drawing
    def draw(self, screen):
        screen.fill((255, 255, 255))

        self.render_text("PLAY", self.play_color, 75, screen, (400, 325))
        self.render_text("QUIT", self.quit_color, 75, screen, (400, 400))

# Level 1 state
class Level_1(Level):
    # Initialize the game state
    def __init__(self):
        Level.__init__(self)
        self.next = "level_2"

    # Cleaning up the game state
    def cleanup(self):
        pass

    # Starting the game state
    def startup(self):
        # Initializing the common level variables
        self.init_level()

    # State event handling
    def get_event(self, event):
        self.events(event)


    # Update the game state
    def update(self, display):
        self.player.update()

        self.updates()

        self.test_for_exits(self.player)

        self.draw(display)

    # game state drawing
    def draw(self, screen):
        self.draws(screen)

# Level 2 state
class Level_2(Level):
    # Initialize the game state
    def __init__(self):
        Level.__init__(self)
        self.next = "menu"

    # Cleaning up the game state
    def cleanup(self):
        pass

    # Starting the game state
    def startup(self):
        # Initializing the common level variables
        self.init_level()

    # State event handling
    def get_event(self, event):
        self.events(event)

    # Update the game state
    def update(self, display):
        self.player.update()

        self.updates()

        self.test_for_exits(self.player)

        self.draw(display)

    # game state drawing
    def draw(self, screen):
        self.draws(screen)

# Level 3 state
class Level_3(Level):
    # Initialize the game state
    def __init__(self):
        Level.__init__(self)
        self.next = "menu"

    # Cleaning up the game state
    def cleanup(self):
        pass

    # Starting the game state
    def startup(self):
        # Initializing the common level variables
        self.init_level()

    # State event handling
    def get_event(self, event):
        self.events(event)


    # Update the game state
    def update(self, display):
        self.player.update()

        self.updates()

        self.test_for_exits(self.player)

        self.draw(display)

    # game state drawing
    def draw(self, screen):
        self.draws(screen)

# List of all levels (used for randomizing level order)
def setup_list():
    return [Level_1(), Level_2(), Level_3()]

level_list = setup_list()
