from __future__ import division, print_function, unicode_literals

__author__ = 'zhenhua.xu'

from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.actions import *
from cocos.sprite import Sprite
from pyglet.window import mouse
from enum import Enum
from math import sqrt
from random import randint

import cocos.euclid as eu
import cocos.collision_model as cm
import soundx

class Direction(Enum):
    LEFT = -1
    RIGHT = 1

    def reverse(self):
        if self == Direction.LEFT:
            return Direction.RIGHT
        else:
            return Direction.LEFT

class MainLayer(Layer):

    is_event_handler = True

    def __init__(self):
        super(MainLayer, self).__init__()
        window_width, window_height = director.window.get_size()

        # add crocodile
        self.crocodile = Sprite('media/crocodile.png', scale=0.25)
        self.crocodile.position = window_width/2, window_height/2
        self.crocodile_direction = Direction.LEFT # it faces LEFT at the beginning
        self.add(self.crocodile)

        # add the bloody moon
        self.moon = Sprite('media/moon.png', scale=0.15)
        self.moon.position = 75, 400
        self.add(self.moon)
        self.moon.do(Repeat(FadeTo(128, 2) + FadeTo(256,2)))

        # add some kids
        self.kids = []
        for i in range(10):
            kid = Sprite('media/kid.png', scale=0.4)
            x_min = int(kid.width/2)
            x_max = window_width - x_min
            y_min = int(kid.height/2)
            y_max = window_height - y_min
            kid.position = randint(x_min,x_max), randint(y_min,y_max)
            add_cshape(kid)
            self.kids.append(kid)
            self.add(kid)

        # collision manager
        self.collision_manager = cm.CollisionManagerBruteForce()
        add_cshape(self.crocodile)
        self.collision_manager.add(self.crocodile)
        for kid in self.kids:
            add_cshape(kid)
            self.collision_manager.add(kid)

        self.schedule(self.update)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == mouse.LEFT:
            self.crocodile.stop()

            # make sure the sprite does not go off the screen
            window_width, window_height = director.window.get_size()
            y_max = window_height - self.crocodile.height / 2
            y_min = self.crocodile.height / 2
            x_max = window_width - self.crocodile.width / 2
            x_min = self.crocodile.width / 2

            y = max(y_min, min(y_max, y))
            x = max(x_min, min(x_max, x))

            # calculate distance and duration
            cx, cy = self.crocodile.position
            dx, dy = cx - x, cy - y
            distance = sqrt(dx**2 + dy**2)
            duration = distance/150

            # define the move action
            move = MoveTo((x,y), duration)
            soundx.play('media/go.mp3')
            self.crocodile.do(move)

            # flip the sprite so that it faces the right direction
            if (dx > 0 and self.crocodile_direction == Direction.RIGHT) or \
               (dx < 0 and self.crocodile_direction == Direction.LEFT):
                self.crocodile.scale_x *= -1
                self.crocodile_direction = self.crocodile_direction.reverse()

    def update(self, dt):
        self.crocodile.cshape.center = self.crocodile.position
        for kid in self.kids:
            kid.cshape.center = kid.position

        collisions = self.collision_manager.objs_colliding(self.crocodile)
        if collisions:
            for kid in collisions:
                self.kids.remove(kid)
                self.collision_manager.remove_tricky(kid)
                self.remove(kid)
                soundx.play('media/swallow.wav')


def add_cshape(sprite):
    cx, cy = sprite.position
    width = sprite.width
    height = sprite.height
    sprite.cshape = cm.AARectShape(eu.Vector2(cx, cy), width/2, height/2)

if __name__ == "__main__":
    director.init(resizable=False, audio=True)
    mainLayer = MainLayer()
    mainScene = Scene(mainLayer)
    director.run(mainScene)
