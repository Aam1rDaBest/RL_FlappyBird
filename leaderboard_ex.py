from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivy.config import Config
from database import GameDatabase
import os


class LeaderboardPopup(Popup):
    def __init__(self, **kwargs):
        super(LeaderboardPopup, self).__init__(**kwargs)
        self.title = "Leaderboard"
        self.size_hint = (None, None)
        self.size = (825, 675)

        self.db = GameDatabase()

        # Create a relative layout as the parent layout
        self.parent_layout = RelativeLayout(pos_hint={"x": 0, "y": 0}, size_hint=(1, 1))

        # Add background image to parent layout
        self.lead_bo_background = os.path.join("images", "leaderboard_background.jpg")
        background_image = Image(source=self.lead_bo_background, allow_stretch=True)

        # Load rank images
        self.first_image = os.path.join("images", "first_medal.png")
        self.second_image = os.path.join("images", "second_medal.png")
        self.third_image = os.path.join("images", "third_medal.png")
        self.fourth_image = os.path.join("images", "fourth_ribbon.png")
        self.fifth_image = os.path.join("images", "fifth_ribbon.png")

        # Attributes for entry count, mode and difficulty
        self.entry_count = 0
        self.mode = None
        self.difficulty = None

        # Create a child layout
        self.child_layout = RelativeLayout(
            pos_hint={"x": 0.2, "y": 0}, size_hint=(0.5, 0.9)
        )

        # Create grid layout
        self.grid_layout = GridLayout(
            cols=3, spacing=10, size_hint_y=0.5, pos_hint={"x": 0.1, "y": 0.265}
        )
        self.grid_layout.bind(minimum_height=self.grid_layout.setter("height"))

        # Apply background color to grid layout
        with self.grid_layout.canvas.before:
            Color(0.651, 0, 0.757, 1)
            self.grid_layout_rect = RoundedRectangle(
                pos=self.grid_layout.pos,
                size=self.grid_layout.size,
                radius=(15, 15, 15, 15),
            )

        # Bind grid layout properties to update rectangle positions and sizes
        self.grid_layout.bind(
            pos=self.update_grid_layout_rect, size=self.update_grid_layout_rect
        )

        # Add grid layout to child layout
        self.child_layout.add_widget(self.grid_layout)

        # Add horizontal box layout for game mode buttons above the grid layout
        self.game_mode_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            pos_hint={"x": 0.1, "y": 0.9},
            padding=(0, 0, 0, 10),
        )

        # Add horizontal box layout for game difficulty buttons below the game mode buttons
        self.game_difficulty_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            pos_hint={"x": 0.1, "y": 0.8},
            padding=(0, 0, 0, 10),
        )

        # Add toggle buttons for difficulty levels
        self.btn_difficulty_easy = ToggleButton(
            text="Easy", group="difficulty", state="down"
        )
        self.btn_difficulty_normal = ToggleButton(text="Normal", group="difficulty")
        self.btn_difficulty_hard = ToggleButton(text="Hard", group="difficulty")
        self.game_difficulty_layout.add_widget(self.btn_difficulty_easy)
        self.game_difficulty_layout.add_widget(self.btn_difficulty_normal)
        self.game_difficulty_layout.add_widget(self.btn_difficulty_hard)

        # Bind toggle button events for difficulty selection
        self.btn_difficulty_easy.bind(on_press=self.on_difficulty_selected)
        self.btn_difficulty_normal.bind(on_press=self.on_difficulty_selected)
        self.btn_difficulty_hard.bind(on_press=self.on_difficulty_selected)

        # Add difficulty layout to child layout
        self.child_layout.add_widget(self.game_difficulty_layout)

        # Add toggle buttons for game modes
        self.btn_game_mode_1 = ToggleButton(
            text="Play Flappy Bird", group="game_mode", state="down"
        )
        self.btn_game_mode_2 = ToggleButton(text="Player VS COM", group="game_mode")
        self.game_mode_layout.add_widget(self.btn_game_mode_1)
        self.game_mode_layout.add_widget(self.btn_game_mode_2)

        # Bind toggle button events
        self.btn_game_mode_1.bind(on_press=self.on_game_mode_selected)
        self.btn_game_mode_2.bind(on_press=self.on_game_mode_selected)

        # Add game mode layout to child layout
        self.child_layout.add_widget(self.game_mode_layout)

        # Initially select game mode 1 and easy difficulty
        self.on_game_mode_selected(self.btn_game_mode_1)
        self.on_difficulty_selected(self.btn_difficulty_easy)

        # Add image background and child layout to parent layout
        self.parent_layout.add_widget(background_image)
        self.parent_layout.add_widget(self.child_layout)

        # Add parent layout to popup
        self.add_widget(self.parent_layout)

    def add_leaderboard_entries(self, entries):
        # Set properties of the leaderboard
        num_entries = len(entries)
        max_rows = 6

        # handle leaderboard entries
        for entry in entries:
            # Handle field entry
            if entry[0] == "Place":
                player_label = Label(
                    text=entry[0],
                    size_hint=(0.8, 0.8),
                    color=(0.968, 0.94, 0.23, 1),
                    outline_color=[0, 0, 0, 1],
                    outline_width=1,
                    font_name="Roboto-BoldItalic",
                    font_size="20sp",
                )
                points_label = Label(
                    text=entry[1],
                    size_hint=(0.8, 0.8),
                    color=(0.968, 0.94, 0.23, 1),
                    outline_color=[0, 0, 0, 1],
                    outline_width=1,
                    font_name="Roboto-BoldItalic",
                    font_size="20sp",
                )
                empty_label = Label(
                    text=entry[2],
                    size_hint=(0.8, 0.8),
                    color=(0.968, 0.94, 0.23, 1),
                    outline_color=[0, 0, 0, 1],
                    outline_width=1,
                    font_name="Roboto-BoldItalic",
                    font_size="20sp",
                )

                # Draw label background for fields
                with empty_label.canvas.before:
                    Color(0.853, 0.759, 0.708, 1)
                    radius = (15, 0, 15, 0)
                    empty_label.rect = RoundedRectangle(
                        pos=empty_label.pos, size=empty_label.size, radius=radius
                    )

                with player_label.canvas.before:
                    Color(0.853, 0.759, 0.708, 1)
                    radius = (0, 15, 0, 15)
                    player_label.rect = RoundedRectangle(
                        pos=player_label.pos, size=player_label.size, radius=radius
                    )

                with points_label.canvas.before:
                    Color(0.853, 0.759, 0.708, 1)
                    radius = (10, 10, 10, 10)
                    points_label.rect = RoundedRectangle(
                        pos=points_label.pos, size=points_label.size, radius=radius
                    )

            # Handle row entries
            else:
                player_label = Label(
                    text=entry[0],
                    size_hint=(0.8, 0.8),
                    color=(0.2, 0.2, 0.2, 1),
                    font_name="Roboto-BoldItalic",
                )
                points_label = Label(
                    text=entry[1],
                    size_hint=(0.8, 0.8),
                    color=(0.2, 0.2, 0.2, 1),
                    font_name="Roboto-BoldItalic",
                )
                empty_label = Label(
                    size_hint=(0.8, 0.8),
                    color=(0.2, 0.2, 0.2, 1),
                    font_name="Roboto-Italic",
                )

                # Apply background to entries
                with empty_label.canvas.before:
                    Color(0.853, 0.759, 0.708, 1)
                    radius = (0, 15, 0, 15)
                    empty_label.rect = RoundedRectangle(
                        pos=empty_label.pos, size=empty_label.size, radius=radius
                    )

                with player_label.canvas.before:
                    Color(0.853, 0.759, 0.708, 1)
                    radius = (10, 10, 10, 10)
                    player_label.rect = RoundedRectangle(
                        pos=player_label.pos, size=player_label.size, radius=radius
                    )

                with points_label.canvas.before:
                    Color(0.853, 0.759, 0.708, 1)
                    radius = (15, 0, 15, 00)
                    points_label.rect = RoundedRectangle(
                        pos=points_label.pos, size=points_label.size, radius=radius
                    )

            # Bind label properties to update rectangle positions and sizes
            empty_label.bind(pos=self.update_rect, size=self.update_rect)
            player_label.bind(pos=self.update_rect, size=self.update_rect)
            points_label.bind(pos=self.update_rect, size=self.update_rect)

            # Add labels to leaderboard
            if entry[0] == "Place":
                self.grid_layout.add_widget(player_label)
                self.grid_layout.add_widget(points_label)
                self.grid_layout.add_widget(empty_label)
            else:
                self.get_image_for_entry(empty_label)
                self.grid_layout.add_widget(player_label)
                self.grid_layout.add_widget(points_label)

        # Fill grid to retain size on grid layout
        num_empty_rows = max_rows - num_entries
        for _ in range(num_empty_rows):
            for _ in range(3):
                empty_row_label = Label(font_name="Roboto-Bold")
                self.grid_layout.add_widget(empty_row_label)

        self.entry_count = 0

    def update_rect(self, instance, value):
        # Update position and size of the rectangle based on label's position and size
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def get_image_for_entry(self, instance):
        # Set images to first field
        if self.entry_count == 0:
            image_source = self.first_image
        elif self.entry_count == 1:
            image_source = self.second_image
        elif self.entry_count == 2:
            image_source = self.third_image
        elif self.entry_count == 3:
            image_source = self.fourth_image
        elif self.entry_count == 4:
            image_source = self.fifth_image

        award_image = AsyncImage(
            size_hint=(1, 0.8), source=image_source, allow_stretch=True
        )
        # Add background to entries
        with award_image.canvas.before:
            Color(0.853, 0.759, 0.708, 1)
            radius = (0, 15, 0, 15)
            award_image.rect = RoundedRectangle(
                pos=award_image.pos, size=award_image.size, radius=radius
            )
        award_image.bind(pos=self.update_rect, size=self.update_rect)

        self.entry_count = self.entry_count + 1

        # Add to grid layout
        self.grid_layout.add_widget(award_image)

    def update_grid_layout_rect(self, instance, value):
        # Update position and size of the rectangle based on grid layout's position and size
        self.grid_layout_rect.pos = instance.pos
        self.grid_layout_rect.size = instance.size

    def on_difficulty_selected(self, instance):
        # Ensure only one difficulty button is toggled at a time within each game mode
        if instance.state == "down":
            if instance.text == "Easy":
                self.btn_difficulty_normal.state = "normal"
                self.btn_difficulty_hard.state = "normal"
                self.difficulty = "easy"
            elif instance.text == "Normal":
                self.btn_difficulty_easy.state = "normal"
                self.btn_difficulty_hard.state = "normal"
                self.difficulty = "normal"
            elif instance.text == "Hard":
                self.btn_difficulty_easy.state = "normal"
                self.btn_difficulty_normal.state = "normal"
                self.difficulty = "hard"
        if (
            self.btn_difficulty_normal.state == "normal"
            and self.btn_difficulty_hard.state == "normal"
            and self.btn_difficulty_easy.state == "normal"
        ):
            self.btn_difficulty_easy.state = "down"
        self.display_leaderboard(self.mode, self.difficulty)

    def on_game_mode_selected(self, instance):
        # Ensure only one mode button is toggled at a time within each difficulty
        if instance.state == "down":
            if instance.text == "Play Flappy Bird":
                self.btn_game_mode_2.state = "normal"
                self.mode = "game"
            elif instance.text == "Player VS COM":
                self.mode = "pvc"
                self.btn_game_mode_1.state = "normal"
        if (
            self.btn_game_mode_1.state == "normal"
            and self.btn_game_mode_2.state == "normal"
        ):
            self.btn_game_mode_1.state = "down"
        self.display_leaderboard(self.mode, self.difficulty)

    def display_leaderboard(self, instance_mode, instance_difficulty):
        # Displays leaderboard based on mode and difficulty buttons selected
        if instance_mode and instance_difficulty:
            entries = self.get_entries_from_database()
            self.grid_layout.clear_widgets()
            if entries:
                self.add_leaderboard_entries(entries)

    def get_entries_from_database(self):
        # Gets top 5 scores in database
        top_scores = self.db.get_top_scores_leaderboard(self.mode, self.difficulty)

        # Writes top scores into leaderboard
        if top_scores:
            entries = [["Place", "Player", "Score"]]
            for score_entry in top_scores:
                # Handles for mode: game
                if self.mode == "game":
                    score = score_entry[0]
                    user_id = score_entry[2]

                    username = self.db.get_username_from_userid(user_id)
                    username = username.replace(" ", "-")
                    entries.append([username, str(score)])
                # Handles for mode: pvc
                else:
                    score = score_entry[0]
                    ai_id = score_entry[1]
                    user_id = score_entry[2]

                    if ai_id:
                        username = self.db.get_username_from_ai_ID(ai_id)
                        username = username.replace(" ", "-")
                        username_string = f"{ai_id} ({username})"
                    else:
                        username_string = self.db.get_username_from_userid(user_id)
                        username_string = username_string.replace(" ", "-")
                    entries.append([username_string, str(score)])

            return entries

        else:
            return None
