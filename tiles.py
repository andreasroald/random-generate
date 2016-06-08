import pygame

from resources import *

class Tileset:
    # Initialize the tileset class
    def __init__(self, image, id):
        self.image = image

        self.id = id

        # Getting the individual tile images from the tileset
        self.top = {
                    "image": self.image.subsurface((0, 0, 32, 32)),
                    "id": self.id + 0.01
                    }

        self.left = {
                     "image": self.image.subsurface((32, 0, 32, 32)),
                     "id": self.id + 0.02
                     }

        self.bottom = {
                       "image": self.image.subsurface((64, 0, 32, 32)),
                       "id": self.id + 0.03
                       }

        self.right = {
                      "image": self.image.subsurface((96, 0, 32, 32)),
                      "id": self.id + 0.04
                      }

        self.tlcorner = {
                         "image": self.image.subsurface((0, 32, 32, 32)),
                         "id": self.id + 0.05
                         }

        self.trcorner = {
                         "image": self.image.subsurface((32, 32, 32, 32)),
                         "id": self.id + 0.06
                         }

        self.blcorner = {
                         "image": self.image.subsurface((64, 32, 32, 32)),
                         "id": self.id + 0.07
                         }

        self.brcorner = {
                         "image": self.image.subsurface((96, 32, 32, 32)),
                         "id": self.id + 0.08
                         }

        self.tl_90deg = {
                         "image": self.image.subsurface((0, 64, 32, 32)),
                         "id": self.id + 0.09
                         }

        self.tr_90deg = {
                         "image": self.image.subsurface((32, 64, 32, 32)),
                         "id": self.id + 0.10
                         }

        self.bl_90deg = {
                         "image": self.image.subsurface((64, 64, 32, 32)),
                         "id": self.id + 0.11
                         }

        self.br_90deg = {
                         "image": self.image.subsurface((96, 64, 32, 32)),
                         "id": self.id + 0.12
                         }

        self.plain = {
                      "image": self.image.subsurface((0, 96, 32, 32)),
                      "id": self.id + 0.13
                      }

        self.all_tiles = [self.top, self.left, self.bottom, self.right,
                          self.tlcorner, self.trcorner, self.blcorner, self.brcorner,
                          self.tl_90deg, self.tr_90deg, self.bl_90deg, self.br_90deg,
                          self.plain]

tileset_grass = Tileset(tileset_grass, 1)
tileset_details = Tileset(tileset_details, 2)
tileset_oak_trees = Tileset(tileset_oak_trees, 3)
tileset_house_1 = Tileset(tileset_house_1, 4)
tileset_platforms = Tileset(tileset_platforms, 5)

tileset_list = [tileset_grass, tileset_details, tileset_oak_trees, tileset_house_1, tileset_platforms]
