from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.image import Image
from leaderboard_ex import LeaderboardPopup
import os


class GameOptionsScreen(Screen):
    def __init__(self, **kwargs):
        super(GameOptionsScreen, self).__init__(**kwargs)

        # Add background image
        self.add_widget(
            Image(
                source=os.path.join("images", "background.png"),
                allow_stretch=True,
                keep_ratio=False,
            )
        )

        # Button to return to the menu screen
        return_button = Button(
            size_hint=(None, None),
            size=(150, 150),
            background_normal="images/arrow.png",
            background_down="images/arrow.png",
            pos_hint={"x": 0, "top": 1},  # top left corner
        )

        # Button to open the leaderboard screen
        leaderboard_button = Button(
            size_hint=(None, None),
            size=(150, 150),
            background_normal="images/leaderboard.png",
            background_down="images/leaderboard.png",
            pos_hint={"x": 0.85, "top": 0.975},  # top right corner
        )

        leaderboard_button.bind(on_release=self.show_leaderboard)
        self.add_widget(leaderboard_button)

        return_button.bind(on_release=self.return_to_menu_screen)
        self.add_widget(return_button)

    def return_to_menu_screen(self, instance):
        # Open meny screen
        app = App.get_running_app()
        app.root.current = "menu"

    def show_leaderboard(self, instance):
        # Create and open leaderboard popup
        popup = LeaderboardPopup()
        popup.open()
