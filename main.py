__version__ = '0.1'
#copyright Clyde Tressler 2014
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget
from kivy.graphics.fbo import Fbo
from kivy.animation import Animation
from kivy.core.image import Image
from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from random import choice, randint
from kivy.graphics.opengl import glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from colorsys import hsv_to_rgb
from kivy.base import EventLoop
from kivy.core.window import Window
EventLoop.ensure_window()

class MoodRing(Widget):

    def __init__(self, **kwargs):
        super(MoodRing, self).__init__(**kwargs)
        self.tex = Image('jewel6.png')
        self.tex2 = Image('ring5.png')
        self.size = (.75*Window.width, .75*3.0*Window.width/4.0)
        self.mood = (.8,.8,.8,1)
        self.label = Label(text = 'text', font_size = '48sp', opacity = 0)
        self.initialize = Label(text = 'Place thumb on jewel until\n  mood matrix initializes',
            font_size = '24sp', opacity = 1, halign = 'justify')
        self.w= Window.width
        self.v= Window.height
        x = self.w - self.size[0]
        y = self.v - self.size[1]
        self.buf_pos = (x/2,3*y/4)
        with self.canvas:
            self.fbo = Fbo(size=(self.size), with_depthbuffer = True)
            Rectangle(size = self.size, pos = self.buf_pos, texture = self.fbo.texture)
        self.new_color()
        self.color_duration = 5

    def update(self, *args):
        self.color.rgba = self.mood

    def animate_color(self, *args):
        self.color.rgba = self.mood
        app =App.get_running_app()
        random_color =self.new_hue()
        if app.word not in app.mood_dict:
            app.mood_dict[app.word] = random_color
        anim = Animation(mood = app.mood_dict[app.word], duration = 1.5, t = 'in_out_cubic')
        anim.on_start = self.animate_opacity
        anim.start(self)

    def animate_opacity(self, *args):
        opacity_ = 0 if self.label.opacity == 1 else 1
        anim2 = Animation(opacity  = opacity_, duration = 1.5, t = 'in_out_cubic')
        anim2.on_complete = self.choose_word
        anim2.start(self.label)

    def choose_word(self, *args):
        if self.label.opacity == 1:
            return True
        elif self.label.opacity == 0:
            app = App.get_running_app()
            new_list = [word for word in app.mood_list if word != app.word]
            app.word = choice(new_list)
            self.label.text = app.word
            self.color_duration = choice([6,6,8,8,8,8,8,8,8,8,16,16,16,24,24,30])
            Clock.schedule_once(self.animate_color)
            Clock.schedule_once(self.animate_opacity, (self.color_duration - 1.5))
            return True

    def new_hue(self, *args):
        hues = [x/14. for x in range(1,15)]
        app = App.get_running_app()
        new_hues = [hue for hue in hues if hue != app.hue]
        app.hue = choice(new_hues)
        random_color = (app.hue, 1, 1)
        random_color = hsv_to_rgb(*random_color)
        return (random_color[0], random_color[1], random_color[2], 1)

    def new_color(self, *args):
        with self.fbo:
            Rectangle(size = self.size, texture = self.tex2.texture)
            self.color = Color(*self.mood)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            Rectangle(size = self.size, texture = self.tex.texture)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            Clock.schedule_once(app.remove_initialize, 3.)
            return True
        return True

    def on_touch_up(self, touch):
            app = App.get_running_app()
            Clock.unschedule(app.remove_initialize)
            return True

def play_sound():
    sound =SoundLoader.load('Hojus.ogg')
    sound.play()
    return True

class MoodRingApp(App):

    def __init__(self, **kwargs):
        super(MoodRingApp, self).__init__(**kwargs)
        with open('moods.txt', 'r') as moods:
            self.mood_list = [line.strip() for line in moods]
        self.word = choice(self.mood_list)
        self.mood_dict = {}
        self.hue = 1
        self.initialized = False

    def remove_initialize(self, root, *args):
        """removes the initialize label and starts animating moods"""
        if self.initialized == True:
            return True
        self.root.remove_widget(self.root.children[0])
        Clock.schedule_once(self.root.children[0].animate_color, self.root.children[0].color_duration)
        Clock.schedule_interval(self.root.children[0].update, 0)
        random_color = self.root.children[0].new_hue()
        self.mood_dict[self.word] = random_color
        self.root.children[0].mood = random_color
        self.root.children[0].label.opacity = 1
        self.root.add_widget(self.root.children[0].label)
        play_sound()
        self.initialized = True
        print self.word, self.mood_dict
        return True

    def on_pause(self):
        # Here you can save data if needed
        #Clock.unschedule(self.root.children[0].animate_color)
        #Clock.unschedule(self.root.children[0].animate_opacity)
        return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        #Clock.schedule_once(self.root.children[0].choose_word, self.root.children[0].color_duration)
        pass

    def build(self):
        root = BoxLayout(orientation = 'vertical')
        moodring = MoodRing()
        moodring.label.text = self.word
        root.add_widget(moodring)
        root.add_widget(moodring.initialize)
        return root

if __name__ == "__main__":
    MoodRingApp().run()