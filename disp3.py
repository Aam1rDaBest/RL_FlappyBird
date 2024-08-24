import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futuristic Screen")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 128, 255)
SILVER = (192, 192, 192)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 120, 0)

# Define the alphabet characters
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

# Define font
font = pygame.font.Font(None, 40)

# Define arrow parameters
arrow_width = 20
arrow_height = 10
arrow_padding = 5

# Define arrow rectangles
arrow_up_rects = []
arrow_down_rects = []
for i in range(6):
    cell_rect = pygame.Rect(160 + i * (320 // 6), 125, 320 // 6, 245)
    arrow_up_rect = pygame.Rect(
        cell_rect.centerx - arrow_width // 2,
        cell_rect.centery - arrow_height - arrow_padding - 30,
        arrow_width,
        arrow_height,
    )
    arrow_down_rect = pygame.Rect(
        cell_rect.centerx - arrow_width // 2,
        cell_rect.centery + arrow_padding + arrow_height + 20,
        arrow_width,
        arrow_height,
    )
    arrow_up_rects.append(arrow_up_rect)
    arrow_down_rects.append(arrow_down_rect)

# Define submit button parameters
submit_button_width = 130
submit_button_height = 45
submit_button_rect = pygame.Rect(
    (WIDTH - submit_button_width) // 2, 310, submit_button_width, submit_button_height
)
button_radius = 10

# Main loop
running = True
current_char_indices = [0, 0, 0, 0, 0, 0]  # Store current character index for each cell
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse is clicked on the arrows
            mouse_pos = pygame.mouse.get_pos()
            for i in range(6):
                if arrow_up_rects[i].collidepoint(mouse_pos):
                    current_char_indices[i] = (current_char_indices[i] + 1) % len(
                        alphabet
                    )
                elif arrow_down_rects[i].collidepoint(mouse_pos):
                    current_char_indices[i] = (current_char_indices[i] - 1) % len(
                        alphabet
                    )
            # Check if the mouse is clicked on the submit button
            if submit_button_rect.collidepoint(mouse_pos):
                print("Contents of the 6 cells:")
                for i in range(6):
                    print(alphabet[current_char_indices[i]], end=" ")
                print()

    # Clear the screen
    screen.fill(WHITE)

    # Draw the futuristic screen
    pygame.draw.rect(screen, BLUE, (100, 50, 440, 380))  # Main background rectangle
    pygame.draw.rect(screen, SILVER, (110, 60, 420, 360))  # Inner rectangle

    # Draw border around the screen
    pygame.draw.rect(screen, BLACK, (100, 50, 440, 380), width=6)

    # Draw decorative elements
    # Add diagonal lines based on the inner rectangle
    pygame.draw.line(screen, BLACK, (110, 60), (530, 420), width=2)
    pygame.draw.line(screen, BLACK, (530, 60), (110, 420), width=2)

    # Add circles based on the inner rectangle
    pygame.draw.circle(screen, BLACK, (110, 60), 10)
    pygame.draw.circle(screen, BLACK, (530, 60), 10)
    pygame.draw.circle(screen, BLACK, (110, 420), 10)
    pygame.draw.circle(screen, BLACK, (530, 420), 10)

    # Draw diamond-shaped content area
    diamond_width = 420
    diamond_height = 360
    diamond_center_x = 100 + 440 // 2
    diamond_center_y = 50 + 380 // 2
    diamond_points = [
        (diamond_center_x, diamond_center_y - diamond_height // 2),  # Top point
        (diamond_center_x + diamond_width // 2, diamond_center_y),  # Right point
        (diamond_center_x, diamond_center_y + diamond_height // 2),  # Bottom point
        (diamond_center_x - diamond_width // 2, diamond_center_y),  # Left point
    ]
    pygame.draw.polygon(screen, BLUE, diamond_points)

    # Draw alphabet cells with scrolling logic
    cell_width = 320 // 6
    cell_height = 360 // 6
    for i in range(6):
        cell_rect = pygame.Rect(
            160 + i * cell_width,
            125 + (245 - cell_height) // 2,  # Center vertically within content area
            cell_width,
            cell_height,
        )
        pygame.draw.rect(screen, SILVER, cell_rect, 2)

        # Draw arrow above cell
        arrow_up_rect = arrow_up_rects[i]
        arrow_up_points = [
            (arrow_up_rect.left, arrow_up_rect.bottom),
            (arrow_up_rect.centerx, arrow_up_rect.top),
            (arrow_up_rect.right, arrow_up_rect.bottom),
        ]
        arrow_up_color = (
            GREEN if arrow_up_rects[i].collidepoint(pygame.mouse.get_pos()) else BLACK
        )
        pygame.draw.polygon(screen, arrow_up_color, arrow_up_points)

        # Draw arrow below cell
        arrow_down_rect = arrow_down_rects[i]
        arrow_down_points = [
            (arrow_down_rect.left, arrow_down_rect.top),
            (arrow_down_rect.centerx, arrow_down_rect.bottom),
            (arrow_down_rect.right, arrow_down_rect.top),
        ]
        arrow_down_color = (
            RED if arrow_down_rects[i].collidepoint(pygame.mouse.get_pos()) else BLACK
        )
        pygame.draw.polygon(screen, arrow_down_color, arrow_down_points)

        # Draw the alphabet character based on current index
        char_surface = font.render(alphabet[current_char_indices[i]], True, BLACK)
        char_rect = char_surface.get_rect(center=(cell_rect.centerx, cell_rect.centery))
        screen.blit(char_surface, char_rect)

    # Draw the submit button
    if submit_button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(
            screen, BLACK, submit_button_rect.move(5, 5), border_radius=button_radius
        )  # Shadow
        pygame.draw.rect(
            screen, DARK_GREEN, submit_button_rect, border_radius=button_radius
        )
    else:
        pygame.draw.rect(screen, GREEN, submit_button_rect, border_radius=button_radius)
    submit_text = font.render("Submit", True, WHITE)
    submit_text_rect = submit_text.get_rect(center=submit_button_rect.center)
    screen.blit(submit_text, submit_text_rect)

    # Draw the "Enter Name:" text
    enter_name_text = font.render("Enter Name:", None, BLACK)
    enter_name_text_rect = enter_name_text.get_rect(center=(WIDTH // 2, 150))
    screen.blit(enter_name_text, enter_name_text_rect)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
