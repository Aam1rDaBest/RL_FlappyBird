import pygame
import os
from PIL import Image

# Initialize pygame
pygame.init()

# Set up the display
screen_width = 400
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Animated GIF")

# Load the GIF image
current_dir = os.path.dirname(__file__)
image_dir = os.path.join(current_dir, "images")
image_path = os.path.join(image_dir, "party_popper.gif")
gif_image = Image.open(image_path)

# Extract frames from the GIF
frames = []
try:
    while True:
        frames.append(gif_image.copy())
        gif_image.seek(len(frames))
except EOFError:
    pass

# Display frames sequentially
clock = pygame.time.Clock()
frame_duration = 100  # Adjust the frame duration as needed
frame_index = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Display the current frame
    screen.fill((0, 0, 0))  # Clear the screen
    frame = frames[frame_index].convert("RGBA")  # Convert frame to RGBA format
    pygame_image = pygame.image.fromstring(
        frame.tobytes(), frame.size, frame.mode
    ).convert_alpha()  # Convert to pygame surface
    screen.blit(pygame_image, (0, 0))

    pygame.display.flip()
    clock.tick(1000 // frame_duration)  # Control frame rate

    # Update frame index
    frame_index = (frame_index + 1) % len(frames)

# Quit pygame
pygame.quit()
