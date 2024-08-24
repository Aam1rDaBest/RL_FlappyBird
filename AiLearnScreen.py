import subprocess
import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.uix.button import Button
from gameOptionsScreen import GameOptionsScreen
from FlappyBirdGame import FlappyBirdGame


class VisualiseAiLearningScreen(GameOptionsScreen):
    def __init__(self, **kwargs):
        super(VisualiseAiLearningScreen, self).__init__(**kwargs)

        # Define the options for Flappy Bird
        options = [
            "Learn to fly to live",
            "Learn to fly through a pipe",
            "           Learn to fly until \nachieved more than 3 pipes",
        ]

        # Position the buttons vertically
        y_positions = [0.7, 0.5, 0.3]

        # Create buttons for each option and add them to the screen
        for option, y_pos in zip(options, y_positions):
            button_border = Button(
                size_hint=(None, None),
                size=(310, 105),
                background_color=(
                    2.15,
                    1.7,
                    0,
                    1,
                ),
                pos_hint={
                    "center_x": 0.5,
                    "center_y": y_pos,
                },
            )
            button = Button(
                text=option,
                size_hint=(None, None),
                size=(290, 90),
                background_color=(0.7, 1.5, 0.6, 1),
                color=(1, 1, 1, 1),
                pos_hint={
                    "center_x": 0.5,
                    "center_y": y_pos,
                },  # center horizontally, y relative
            )
            button.bind(size=button.setter("text_size"))  # Allow text wrapping
            button.bind(on_press=self.on_button_press)  # Bind button press event
            self.add_widget(button_border)
            self.add_widget(button)

    def on_button_press(self, instance):
        # Select option from button
        option = instance.text
        if "live" in option:
            option_with_space = "easy vis"
        elif "a pipe" in option:
            option_with_space = "normal vis"
        elif "3" in option:
            option_with_space = "hard vis"
        script_path = os.path.join(os.getcwd(), "FlappyBirdGame.py")
        Window.hide()
        # Run Flappy Bird game code
        subprocess.run(["python", script_path, option_with_space])
        Window.show()
