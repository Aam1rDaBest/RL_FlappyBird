import sqlite3


class GameDatabase:
    def __init__(self, db_name="game_scores.db"):
        self.db_name = db_name

    def create_database(self):
        # Connect to SQLite database
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Create User Information table
        c.execute(
            """CREATE TABLE IF NOT EXISTS UserInformation (
                    UserID TEXT PRIMARY KEY,
                    Username TEXT NOT NULL
                    )"""
        )

        # Create AI Information table
        c.execute(
            """CREATE TABLE IF NOT EXISTS AiInformation (
                    AiID TEXT PRIMARY KEY,
                    UserID TEXT NOT NULL,
                    FOREIGN KEY (UserID) REFERENCES UserInformation(UserID)
                    )"""
        )

        # Create Game Scores table
        c.execute(
            """CREATE TABLE IF NOT EXISTS GameScores (
                    ScoreID TEXT PRIMARY KEY,
                    UserID TEXT,
                    AiID TEXT,
                    Score INTEGER,
                    GameMode TEXT,
                    Difficulty TEXT,
                    FOREIGN KEY (UserID) REFERENCES UserInformation(UserID),
                    FOREIGN KEY (AiID) REFERENCES AiInformation(AiID),
                    CHECK (
                        (UserID IS NOT NULL AND AiID IS NULL) OR
                        (UserID IS NULL AND AiID IS NOT NULL)
                        )
                    )"""
        )

        # Commit changes and close connection
        conn.commit()
        conn.close()

    def check_username_existence(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Gets username from userID
        c.execute("SELECT UserID FROM UserInformation WHERE Username = ?", (username,))
        result = c.fetchone()

        conn.close()

        return result is not None

    def generate_id(self, prefix):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Determine the table and column name based on the prefix
        table_name = ""
        column_name = ""
        if prefix == "U":
            table_name = "UserInformation"
            column_name = "UserID"
        elif prefix == "S":
            table_name = "GameScores"
            column_name = "ScoreID"
        elif prefix == "A":
            table_name = "AiInformation"
            column_name = "AiID"

        # Retrieve the highest ID with the given prefix from the corresponding table
        c.execute(
            f"SELECT MAX(CAST(substr({column_name}, 2) AS INTEGER)) FROM {table_name} WHERE {column_name} LIKE ?",
            (f"{prefix}%",),
        )
        max_id = c.fetchone()[0]

        # Increments ID for next user
        if max_id:
            next_id = int(max_id) + 1
        else:
            next_id = 1

        conn.close()

        return f"{prefix}{next_id}"

    def insert_new_user(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Generate UserID
        user_id = self.generate_id("U")

        # Insert new user
        c.execute(
            "INSERT INTO UserInformation (UserID, Username) VALUES (?, ?)",
            (user_id, username),
        )
        conn.commit()

        conn.close()

    def insert_new_ai(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Get UserID using username
        c.execute("SELECT UserID FROM UserInformation WHERE Username = ?", (username,))
        user_id = c.fetchone()
        ai_id = self.generate_id("A")

        if user_id is not None:
            user_id = user_id[0]

            # Insert new AI
            c.execute(
                "INSERT INTO AiInformation (AiID, UserID) VALUES (?, ?)",
                (ai_id, user_id),
            )
            conn.commit()

            return ai_id
        else:
            pass

        conn.close()

    def insert_new_game_score(self, id, score, game_mode, difficulty):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Generate ScoreID
        score_id = self.generate_id("S")

        # Check if the ID prefix is 'A' (indicating AiID)
        is_ai_id = id[0] == "A"

        # Insert new game score
        c.execute(
            "INSERT INTO GameScores (ScoreID, UserID, AiID, Score, GameMode, Difficulty) VALUES (?, ?, ?, ?, ?, ?)",
            (
                score_id,
                id if not is_ai_id else None,
                id if is_ai_id else None,
                score,
                game_mode,
                difficulty,
            ),
        )
        conn.commit()

        conn.close()

    def check_new_high_score(self, user_id, score, game_mode, difficulty):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Check if the provided score is a new high score
        c.execute(
            "SELECT MAX(Score) FROM GameScores WHERE GameMode = ? AND Difficulty = ?",
            (game_mode, difficulty),
        )
        highest_score = c.fetchone()[0]

        conn.close()

        return highest_score

    def get_highest_score(self, game_mode, difficulty):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Retrieve the highest score for the specified game mode and difficulty
        c.execute(
            "SELECT MAX(Score) FROM GameScores WHERE GameMode = ? AND Difficulty = ?",
            (game_mode, difficulty),
        )
        highest_score = c.fetchone()[0]

        conn.close()

        return highest_score

    def get_user_id(self, username):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Retrieve the UserID for the provided username
        c.execute("SELECT UserID FROM UserInformation WHERE Username = ?", (username,))
        user_id = c.fetchone()[0]

        conn.close()

        return user_id

    def get_top_scores(self, game_mode, difficulty):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Retrieve the top 5 scores for the specified game mode and difficulty
        c.execute(
            """
            SELECT Score
            FROM GameScores
            WHERE GameMode = ? AND Difficulty = ?
            ORDER BY Score DESC
            LIMIT 5
        """,
            (game_mode, difficulty),
        )

        top_scores = c.fetchall()

        conn.close()

        return top_scores

    def get_top_scores_leaderboard(self, game_mode, difficulty):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Retrieve the top 5 scores along with AiID and UserID
        c.execute(
            """
            SELECT Score, AiID, UserID
            FROM GameScores
            WHERE GameMode = ? AND Difficulty = ?
            ORDER BY Score DESC
            LIMIT 5
        """,
            (game_mode, difficulty),
        )

        top_scores = c.fetchall()

        conn.close()

        return top_scores

    def get_username_from_userid(self, user_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Retrieve the username associated with the provided UserID
        c.execute("SELECT Username FROM UserInformation WHERE UserID = ?", (user_id,))
        result = c.fetchone()

        conn.close()

        # Return the username if found, otherwise return None
        return result[0] if result else None

    def get_username_from_ai_ID(self, ai_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Retrieve the UserID associated with the provided AiID
        c.execute("SELECT UserID FROM AiInformation WHERE AiID = ?", (ai_id,))
        result = c.fetchone()

        if result:
            # If a UserID is found, retrieve the corresponding username
            user_id = result[0]
            username = self.get_username_from_userid(user_id)
        else:
            username = None  # Return None if AiID is not found or doesn't have a corresponding user

        conn.close()

        return username
