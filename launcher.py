from kivy.app import App
from kivy.uix.button import Button
import subprocess
import os


class GameLauncherApp(App):
    def build(self):
        # Set the current working directory to the script's directory
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        # Create a button to launch the Flappy Bird game
        launch_button = Button(text="Launch Flappy Bird")
        launch_button.bind(on_press=self.launch_flappy_bird)
        return launch_button

    def launch_flappy_bird(self, instance):
        script_path = os.path.join(os.getcwd(), "FlappyBirdGame.py")
        subprocess.run(["python", script_path])


if __name__ == "__main__":
    GameLauncherApp().run()
