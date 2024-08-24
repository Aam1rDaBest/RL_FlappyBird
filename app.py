from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
import os
import subprocess
from title import TitleScreen
from menu import MenuScreen
from FGameScreen import FlappyBirdOptionsScreen
from AiLearnScreen import VisualiseAiLearningScreen
from PVCScreen import PlayerVSCOMScreen
from database import GameDatabase


class App(App):

    # Create app and instances to screens
    def build(self):
        self.check = False
        Window.minimum_height = 600
        Window.minimum_width = 800

        self.db = GameDatabase()
        self.db.create_database()

        self.sm = ScreenManager()
        self.title_screen = TitleScreen(name="title")
        self.menu_screen = MenuScreen(name="menu")
        self.sm.add_widget(self.title_screen)
        self.sm.add_widget(self.menu_screen)
        self.sm.add_widget(FlappyBirdOptionsScreen(name="flappy_bird_options"))
        self.sm.add_widget(VisualiseAiLearningScreen(name="visualise_ai_learn"))
        self.sm.add_widget(PlayerVSCOMScreen(name="player_vs_com"))

        # Start with the title screen
        self.sm.current = "title"

        Window.bind(on_keyboard=self.on_keyboard)  # Bind the 'on_keyboard' event
        return self.sm

    def on_keyboard(self, window, key, *args):
        if key == 27:
            if self.sm.current == "title":
                if self.check == False:
                    self.check = True
                    self.confirm_exit()
                    # Return True to indicate that the key event has been handled
                    return True
                elif self.check == True:
                    return True
            else:
                # Switch back to the title screen
                self.sm.current = "title"
                return (
                    # Return True to indicate that the key event has been handled
                    True
                )

    def confirm_exit(self):
        # Create a BoxLayout to organize buttons horizontally
        button_layout = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=50
        )

        # Create 'Yes' and 'No' buttons
        yes_button = Button(text="Yes", size_hint=(0.5, 1))
        no_button = Button(text="No", size_hint=(0.5, 1))

        # Define the callback functions for buttons
        def on_yes(instance):
            App.get_running_app().stop()  # Stop the Kivy application

        def on_no(instance):
            self.check = False
            popup.dismiss()

        # Bind buttons to their callback functions
        yes_button.bind(on_release=on_yes)
        no_button.bind(on_release=on_no)

        # Add buttons to the button layout
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)

        # Create a popup with exit confirmation message and buttons
        popup = Popup(
            title="Exit Confirmation",
            content=BoxLayout(orientation="vertical", size_hint=(1, 1)),
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=False,
        )

        # Add exit confirmation message to popup content
        popup.content.add_widget(
            Label(text="Are you sure you want to exit?", size_hint=(1, 0.8))
        )

        # Add button layout to popup content
        popup.content.add_widget(button_layout)

        self.check = True

        # Open the popup
        popup.open()


if __name__ == "__main__":
    # Run application
    App().run()
