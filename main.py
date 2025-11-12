import os
import sys
import pygame as pg

from flappy import play_flappy_bird

os.environ["SDL_VIDEO_CENTERED"] = '1'
pg.init()
pg.display.set_caption('UAI skibidi toilet')

class Control(object):
    def __init__(self):
        self.done = False

    def main_loop(self):

        play_flappy_bird()
        self.done = True

if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
