from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from leaderboard_ex import LeaderboardPopup
import os


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        # Add background image
        self.add_widget(
            Image(
                source=os.path.join("images", "background.png"),
                allow_stretch=True,
                keep_ratio=False,
            )
        )

        # Define the options for the menu
        options = ["Play Flappy Bird", "Visualise AI learning", "Player vs COM"]

        # Position the buttons vertically
        y_positions = [0.7, 0.5, 0.3]

        # Create buttons for each option and add them to the screen
        for option, y_pos in zip(options, y_positions):
            # Border of button
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
            # Button on the left side with text
            button = Button(
                text=option,
                size_hint=(None, None),
                size=(180, 90),
                font_size="13sp",
                background_color=(0.7, 1.5, 0.6, 1),
                color=(1, 1, 1, 1),
                pos_hint={
                    "center_x": 0.44,
                    "center_y": y_pos,
                },
            )

            # Button for image on right side
            button_two = Button(
                size_hint=(None, None),
                size=(130, 90),
                color=(1, 1, 1, 1),
                pos_hint={
                    "center_x": 0.585,
                    "center_y": y_pos,
                },
            )

            # Button for background of right side
            button_three = Button(
                size_hint=(None, None),
                size=(130, 90),
                background_color=(0.7, 1.5, 0.6, 1),
                color=(1, 1, 1, 1),
                pos_hint={
                    "center_x": 0.585,
                    "center_y": y_pos,
                },
            )

            # Handle selected bind properties of buttons
            if option == "Play Flappy Bird":
                button.bind(on_release=self.play_flappy_bird)
                button_three.bind(on_release=self.play_flappy_bird)
                button_two.bind(on_release=self.play_flappy_bird)

                button_two.background_normal = "images/bird.png"
            if option == "Visualise AI learning":
                button.bind(on_release=self.visualise_ai_learning)
                button_three.bind(on_release=self.visualise_ai_learning)
                button_two.bind(on_release=self.visualise_ai_learning)

                button_two.background_normal = "images/ai_learn.png"
                button_two.background_size = (None, None)
            if option == "Player vs COM":
                button.bind(on_release=self.player_vs_com)
                button_three.bind(on_release=self.player_vs_com)
                button_two.bind(on_release=self.player_vs_com)

                button_two.background_normal = "images/pvc.png"

            self.add_widget(button_border)
            self.add_widget(button_three)
            self.add_widget(button_two)
            self.add_widget(button)

        # Button to return to title screen
        return_button = Button(
            size_hint=(None, None),
            size=(150, 150),
            background_normal="images/arrow.png",
            background_down="images/arrow.png",
            pos_hint={"x": 0, "top": 1},  # Left corner
        )

        # Button to open leaderboard screen
        leaderboard_button = Button(
            size_hint=(None, None),
            size=(150, 150),
            background_normal="images/leaderboard.png",
            background_down="images/leaderboard.png",
            pos_hint={"x": 0.85, "top": 0.975},  # top right corner
        )

        leaderboard_button.bind(on_release=self.show_leaderboard)
        self.add_widget(leaderboard_button)

        return_button.bind(on_press=self.return_to_title)
        self.add_widget(return_button)

    def return_to_title(self, instance):
        # Opens title screen
        app = App.get_running_app()
        app.root.current = "title"

    def show_leaderboard(self, instance):
        # Create and open leaderboard popup
        popup = LeaderboardPopup()
        popup.open()

    def play_flappy_bird(self, instance):
        # Opens mode: game screen
        app = App.get_running_app()
        app.root.current = "flappy_bird_options"

    def visualise_ai_learning(self, instance):
        # Opens mode: vis screen
        app = App.get_running_app()
        app.root.current = "visualise_ai_learn"

    def player_vs_com(self, instance):
        # Opens mode: pvc screen
        app = App.get_running_app()
        app.root.current = "player_vs_com"
