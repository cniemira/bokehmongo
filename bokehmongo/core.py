import math
import numpy as np
import random
import time

from bokeh.charts import Scatter
from bokeh.io import push_notebook, output_notebook, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import ImageURL
from bokeh.plotting import figure
from ipywidgets import interact_manual
from scipy.spatial.distance import cdist

class BaseMon(object):
    # acceleration, max velocity, jitter
    _x_motion = (0.0, 0.0, 0.0)
    _y_motion = (0.0, 0.0, 0.0)
    _mon_h = 32
    _mon_w = 32
    _mon_url = "/files/logo.png"
    _max_dist = 10
    _max_throws = 5
    _max_time = 10 
    
    _escaped = False
    _hit = False
    _spawned = 0
    _throws = 0

    
    def __init__(self):
        self._x_speed = 0
        self._y_speed = 0
        self._mon_x = random.randrange(500,1000)
        self._mon_y = random.randrange(1,800) if self._y_motion[1] > 0 else 1        
        
        self._ball_path = np.array([[0.,0.,]])
        self._source = ColumnDataSource(data=dict(
            ball_x=self._ball_path[:, 0],
            ball_y=self._ball_path[:, 1],
            mon_x=[self._mon_x],
            mon_y=[self._mon_y],
            mon_h=[self._mon_h],
            mon_w=[self._mon_w],
            mon_u=[self._mon_url]
            ))
#plot_width=500, plot_height=500, 
        self._figure = figure(tools='', x_range=(0,1000), y_range=(0,1200))
        self._figure.circle(x="ball_x", y="ball_y", size=3, line_color="navy", fill_color="red", source=self._source)
        self._figure.image_url(url="mon_u", x="mon_x", y="mon_y", w="mon_w", h="mon_h", anchor="bottom_center",
                               source=self._source, h_units="screen", w_units="screen")

        self._spawned = time.time()
        show(self._figure)
    
    def __repr__(self):
        return str(self.__class__.__name__)
    
    def catch(self):
        self._interact = interact_manual(self._throw, velocity=(0.,530., 1.), v_angle=(1.,89., 1.))
        self._interact.widget.children[-1].description = 'Throw Ball'
        print('You have %d seconds to catch %s' % (self._max_time, self))

    def _throw(self, velocity, v_angle):
        assert not self._hit

        try:
            if self._escaped:
                raise UserWarning('%s is not a valid target!' % (self,))

            self._update_ball_trajectory(velocity, v_angle)
            self._move_target()

            distances = cdist(self._ball_path, [[self._mon_x, self._mon_y]])
            closest = distances.min()
            if closest < self._max_dist:
                self._hit = True
                impact_point = distances.argmin()
                x = self._ball_path[impact_point,0]
                y = self._ball_path[impact_point,1]
                self._ball_path = self._ball_path[:impact_point]
                print('Hit at %0.2f×%0.2f with a distance of %f' % (x, y, closest))
                self._interact.widget.set_trait('visible', False)

            self._source.data['ball_x'] = self._ball_path[:, 0]
            self._source.data['ball_y'] = self._ball_path[:, 1]

            # this seems like a filthy hack...
            # Bokeh seems to want every data item to have the same len
            n = self._source.data['ball_x'].shape[0]
            self._source.data['mon_x'] = [self._mon_x]*n
            self._source.data['mon_y'] = [self._mon_y]*n
            self._source.data['mon_h'] = [self._mon_h]*n
            self._source.data['mon_w'] = [self._mon_w]*n
            self._source.data['mon_u'] = [self._mon_url]*n
            
            push_notebook()

        except UserWarning as e:
            print(e)
        
    def _update_ball_trajectory(self, velocity, v_angle):
        self._throws += 1
        if self._throws > self._max_throws:
            self._escaped = True
            raise UserWarning('Too many tries. %s escaped!' % (self,))

        coords = []
        v_rads = math.radians(v_angle)
        t = 0.0
        while True:
            y = (t * velocity * math.sin(v_rads)) - (9.8 * t * t)/2
            if y < 0:
                break
            x = velocity * math.cos(v_rads) * t
            coords.append((x, y))
            t += 0.1

        self._ball_path = np.array(coords)

    def _move_target(self):
        now = time.time()
        time_lapse = int(now - self._spawned)
        if (time_lapse > self._max_time):
            self._escaped = True
            raise UserWarning('You took too long. %s escaped!' % (self,))

        x_dir = -1 if random.random() < self._x_motion[2] else 1
        self._x_speed += random.random() * x_dir * self._x_motion[1]
        self._x_speed = max(self._x_speed, self._x_motion[0] * -1) if self._x_speed < 0 else min(self._x_speed, self._x_motion[0])
        x_pos = self._mon_x + self._x_speed
        self._x_speed = self._x_speed * -1.5 if x_pos > 999 or x_pos < 1 else self._x_speed
        self._mon_x += self._x_speed

        y_dir = -1 if random.random() < self._y_motion[2] else 1
        self._y_speed += random.random() * y_dir * self._y_motion[1]
        self._y_speed = max(self._y_speed, self._y_motion[0] * -1) if self._y_speed < 0 else min(self._y_speed, self._y_motion[0])
        y_pos = self._mon_y + self._y_speed
        self._y_speed = self._y_speed * -1.5 if y_pos > 999 or y_pos < 1 else self._y_speed
        self._mon_y += self._y_speed

        print('%s velocity: %f,%f\nYou have %0.2f seconds left.' % (self, self._x_speed, self._y_speed,
                                                                     self._max_time-time_lapse))


_dex = []
def _register(cls):
    _dex.append(cls)

class TestMon(BaseMon):
    # max velocity, acceleration, jitter
    _x_motion = (50.0, 10.0, 0.5)
    _y_motion = (0.0, 0.0, 0.0)
    _max_dist = 100
    _max_throws = 100
    _max_time = 90


@_register
class Bulbasaur(BaseMon):
    _x_motion = (50.0, 10.0, 0.5)
    _y_motion = (0.0, 0.0, 0.0)
    _max_dist = 40
    _max_throws = 5
    _max_time = 30

    _mon_h = 32
    _mon_w = 32
    _mon_url = "https://img.pokemondb.net/artwork/bulbasaur.jpg"


@_register
class Zubat(BaseMon):
    _x_motion = (60.0, 20.0, 0.5)
    _y_motion = (60.0, 20.0, 0.5)
    _max_dist = 40
    _max_throws = 5
    _max_time = 30

    _mon_h = 32
    _mon_w = 32
    _mon_url = "https://img.pokemondb.net/artwork/zubat.jpg"


def track():
    cls = _dex[random.randrange(0, len(_dex))]
    return cls()

