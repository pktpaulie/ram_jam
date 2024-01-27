import pygame
import sys
from threading import Thread

 
# Initialize Pygame
pygame.init()

# Create the display surface object of specific dimensions 
win = pygame.display.set_mode((500, 500))

# Set the Pygame window name
pygame.display.set_caption("Ramjam")

# Load the background image 1
background_i = "Background.png"

#Load the sound
soundA=pygame.mixer.Sound("Accerlation-engine.wav")

#Separate thread for the sound effect
def accel_sound_function():
    soundA.play(0)
    pygame.time.delay(1000)
    soundA.stop()
    sys.exit()


def load_background(img_location):
    try:
        background_image = pygame.image.load(img_location)
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        sys.exit(1)

    # Load background
    win.blit(background_image, (0, 0))


# Load the car image
car_image_trex = "TRex_Car2.png"

#TODO: Loading screen for game to start
#TODO: Add this to a function and call in load
#TODO: Background for next scene / loop background for current level then load new bg for new level
#TODO: Bigger images??

car_image_object = pygame.image.load(car_image_trex)
car_rect_orig = car_image_object.get_rect()

#Scale image
car_w, car_h = 100, 75
car_image_object = pygame.transform.scale(car_image_object, (car_w, car_h))
car_rect = car_image_object.get_rect()

# Object current coordinates
# x = 0
# y = 200
x = 0
y = 380 #410

# Initial velocity / speed of movement
initial_vel = 1

# Acceleration factor
acceleration_factor = 1.2

# Current velocity
current_vel = 0

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
                    T=Thread(target=accel_sound_function)
                    T.start()
                     
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

    load_background(background_i)

    # Draw the car image at the updated position
    win.blit(car_image_object, (x, y))

    # Refresh the window
    pygame.display.update()
    timer.tick(30)

# Close the Pygame window
pygame.quit()
sys.exit()




