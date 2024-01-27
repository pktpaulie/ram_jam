#Audio recording and fft came from the example at
#https://gist.github.com/ZWMiller/53232427efc5088007cab6feee7c6e4c

"""
The following installations are required for the ram
"""
# pip install pygame
# pip install pyaudio
# pip install seaborn

import sys
from threading import Thread
import os
import pygame
from pygame.locals import *

try:
    import pyaudio
    import numpy as np
    import pylab
    from scipy.io import wavfile
    import time
    import seaborn as sns
except:
    print("Something didn't import")
 
# Initialize Pygame
pygame.init()

# Create the display surface object of specific dimensions 
win = pygame.display.set_mode((500, 500))

# Set the Pygame window name
pygame.display.set_caption("Ramjam")

# Load and transform the background image 1
#background_1 = os.path.abspath("Background/Background.png")
background_1 = "Background.png"

#Load the sound
#soundA_path = os.path.abspath("Effects/Accerlation-engine.wav")
soundA=pygame.mixer.Sound("Accerlation-engine.wav")

#Set up the microphone recording 
FORMAT = pyaudio.paInt16 # We use 16bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 1024 # 1024bytes of data red from a buffer
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()
# start Recording
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True)
stream.start_stream()

#Function for mic in
def micFunction(in_data):
    audio_data = np.fromstring(in_data, np.int16)
    dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))
    maxLocation=np.argmax(dfft)
    print("MAX=", maxLocation)


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
car_image_trex = os.path.abspath("Character_Sprites/Bee_Car2.png")

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

    #Start the mic recording. (You can comment the next line out to ignore)
    micFunction(stream.read(CHUNK))

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

    load_background(background_1)

    # Draw the car image at the updated position
    win.blit(car_image_object, (x, y))

    # Refresh the window
    pygame.display.update()
    timer.tick(30)
# Close up mic recording
stream.stop_stream()
stream.close()

audio.terminate()
# Close the Pygame window
pygame.quit()
sys.exit()




