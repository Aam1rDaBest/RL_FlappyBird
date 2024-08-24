from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle


class LeaderboardApp(App):
    def build(self):
        # Create a BoxLayout to hold the leaderboard
        leaderboard_layout = BoxLayout(orientation="vertical")

        # Add headers row
        headers_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50
        )
        headers_layout.add_widget(Label(text="Name", size_hint_x=0.5, halign="center"))
        headers_layout.add_widget(Label(text="Score", size_hint_x=0.5, halign="center"))
        leaderboard_layout.add_widget(headers_layout)

        # Add filled rows
        for i in range(3):
            row_layout = BoxLayout(
                orientation="horizontal", size_hint_y=None, height=50
            )
            name_label = Label(text=f"Player {i+1}", size_hint_x=0.5, halign="center")
            score_label = Label(text=f"{(i+1)*1000}", size_hint_x=0.5, halign="center")

            # Create colored background for labels
            with name_label.canvas.before:
                Color(0.5, 0.5, 1, 1)  # Light blue
                name_label.rect = Rectangle(pos=name_label.pos, size=name_label.size)
            with score_label.canvas.before:
                Color(0.5, 1, 0.5, 1)  # Light green
                score_label.rect = Rectangle(pos=score_label.pos, size=score_label.size)

            # Bind label properties to update rectangle positions and sizes
            name_label.bind(pos=self.update_rect, size=self.update_rect)
            score_label.bind(pos=self.update_rect, size=self.update_rect)

            row_layout.add_widget(name_label)
            row_layout.add_widget(score_label)
            leaderboard_layout.add_widget(row_layout)

        return leaderboard_layout

    def update_rect(self, instance, value):
        # Update position and size of the rectangle based on label's position and size
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size


if __name__ == "__main__":
    LeaderboardApp().run()
