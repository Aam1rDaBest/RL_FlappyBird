from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
import os
import subprocess


class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super(TitleScreen, self).__init__(**kwargs)
        # Background image
        self.add_widget(
            Image(
                source=os.path.join("images", "background.png"),
                allow_stretch=True,
                keep_ratio=False,
            )
        )

        # Label to start application
        self.add_widget(
            Label(
                text="Press to start",
                font_size=30,
                size_hint=(None, None),
                pos_hint={"center_x": 0.5, "center_y": 0.7},
            )
        )

        # Label to indicate exit
        self.add_widget(
            Label(
                text="Press 'ESC' to exit",
                font_size=15,
                size_hint=(None, None),
                pos_hint={"center_x": 0.5, "center_y": 0.3},
            )
        )

    def on_touch_down(self, touch):
        # Handles press event
        if self.collide_point(*touch.pos):
            if touch.is_touch:
                self.start_game()

    def start_game(self):
        # Opens menu screen
        self.manager.current = "menu"
