import random

import pygame

import settings
import sprites
#import tiles
import states

# Control classw
class Control:
    # Initialize the control class
    def __init__(self):
        pygame.init()
        self.running = True
        self.playing = True
        self.game_display = pygame.display.set_mode((settings.display_width, settings.display_height))
        self.clock = pygame.time.Clock()

    # Setup the state control
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    # Function that runs when switching state
    def switch_state(self):
        self.state.done = False
        previous, self.state_name = self.state_name, self.state.next

        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()

        self.state.previous = previous

    # Game loop
    def loop(self):
        while self.playing:
            self.clock.tick(settings.FPS)
            self.events()
            self.update()
            pygame.display.update((0, 0, settings.display_width, settings.display_height))
            pygame.display.set_caption(settings.title + " running at " + str(int(self.clock.get_fps())) + " frames per second")

    # Event handling
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            self.state.get_event(event)

    # Update the control class
    def update(self):
            if self.state.quit:
                self.playing = False
            elif self.state.done:
                self.switch_state()
            self.state.update(self.game_display)

# Randomizing the level order function
def randomize_level_order(my_dict):
    for level_num in range(1, len(states.level_list)+1):
        my_dict["level_{}".format(level_num)] = states.level_list[random.randrange(0, len(states.level_list))]
        states.level_list.remove(my_dict["level_{}".format(level_num)])
        if level_num <= len(states.level_list)+1:
            my_dict["level_{}".format(level_num)].next = "level_{}".format(level_num + 1)
        else:
            my_dict["level_{}".format(level_num)].next = "menu"
            my_dict["level_{}".format(level_num)].quit_on_exit = True

game = Control()
state_dict = {
    "menu": states.Menu()
}

while game.running:
    game.__init__()
    states.level_list = states.setup_list()

    randomize_level_order(state_dict)
    game.setup_states(state_dict, "menu")
    game.loop()

pygame.quit()
quit()
