import pygame
import sys

# Initialize Pygame
pygame.init()

# Create the display surface object of specific dimensions (600, 600)
win = pygame.display.set_mode((600, 600))

# Set the Pygame window name
pygame.display.set_caption("Ramjam")

# Load the background image
background_image = pygame.image.load("background_image.jpg")  # Replace with your background image file path


# Load the car image
image = "TRex_Car2.png"
car_image_object = pygame.image.load(image)
car_rect = car_image_object.get_rect()

# Object current coordinates
x = 0
y = 200

# Initial velocity / speed of movement
initial_vel = 1

# Acceleration factor
acceleration_factor = 1.2

# Current velocity
current_vel = initial_vel

# Indicates Pygame is running
crashed = False

timer = pygame.time.Clock()

# Infinite loop
while not crashed:
    pygame.time.delay(10)
    # Clear the screen
    win.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_vel = initial_vel
            elif event.key == pygame.K_RIGHT:
                if current_vel >= 10:
                    current_vel = 10
                else:
                    current_vel += acceleration_factor
            elif event.key == pygame.K_LEFT:
                if current_vel > 0:
                    current_vel -= acceleration_factor
                else:
                    current_vel = 0

    # Move the car continuously in the positive x-direction
    x += current_vel

    # If the car goes off the right side of the window, reset its position
    if x > 600:
        x = 0 - car_rect.width

    # Store keys pressed
    keys = pygame.key.get_pressed()

    # Move up
    if keys[pygame.K_UP] and y > 0:
        y -= current_vel

    # Move down
    if keys[pygame.K_DOWN] and y < 600 - car_rect.height:
        y += current_vel

    # Draw the car image at the updated position
    win.blit(car_image_object, (x, y))

    # Refresh the window
    pygame.display.update()
    timer.tick(30)

# Close the Pygame window
pygame.quit()
sys.exit()


