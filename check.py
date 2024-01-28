#Audio recording and fft came from the example at
#https://gist.github.com/ZWMiller/53232427efc5088007cab6feee7c6e4c

"""
The following installations are required for the ram
"""
# pip install pygame
# pip install pyaudio
# pip install seaborn
# pip install pydub


import sys
from threading import Thread
import os
import pygame
from pygame.locals import *
from pydub import AudioSegment
import random

try:
    import pyaudio
    import numpy as np
    import pylab
    from scipy.io import wavfile
    import time
    import seaborn as sns
    from ctypes import c_int64
    
except:
    print("Something didn't import")


# Initialize Pygame
pygame.init()

# Create the display surface object of specific dimensions 
screen_width = 500
screen_height = 500
win = pygame.display.set_mode((screen_width, screen_height))

# Set the Pygame window name
pygame.display.set_caption("Ramjam")

# Load and transform the background image 1
#background_1 = os.path.abspath("Background/Background.png")
background_images = [
    pygame.image.load("Background1.png"),
    pygame.image.load("Background2.png"),
    pygame.image.load("Background3.png"),
    pygame.image.load("Background4.png"),
]

#check image loaded and transform it
def check_image_loading(img):
    try:
        background_image = pygame.image.load(img)
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        sys.exit(1)
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    

# background_1 = "Background1.png"
# background_2 = "Background2.png"
# background_3 = "Background3.png"
# background_4 = "Background4.png"
# background_1 = os.path.abspath("Background/Background1.png")
# background_2 = os.path.abspath("Background/Background2.png")
# background_3 = os.path.abspath("Background/Background3.png")
# background_4 = os.path.abspath("Background/Background4.png")

# Set initial background image
#current_background = background_1

# Variable to iterate over the background image  
iterator = 0    # Start at 0 and iterate along width of screen
# Set the initial background image and iterator
current_background_index = 0

# Variable to control background change
background_change_timer = 0

# Variable to control background scrolling speed
background_scroll_speed = 2


# Current velocity
current_vel = 0

# skid variables
skid_active = False
skid_duration = 40  # Skid duration in frames
skid_timer = 0

skid_rotation_angle = 0


#Load the in all sound effects
soundAccel=pygame.mixer.Sound("./Effects/Acceleration.wav")
soundIdle=pygame.mixer.Sound("./Effects/idleEngine.wav")
soundStart=pygame.mixer.Sound("./Effects/startEngine.wav")
soundStop=pygame.mixer.Sound("./Effects/stopEngine.wav")
soundBanana=pygame.mixer.Sound("./Effects/banana.wav")
soundMonkey=pygame.mixer.Sound("./Effects/monkey_sounds.wav")
soundBounce=pygame.mixer.Sound("./Effects/bounce_tires.wav")
#soundSkid=pygame.mixer.Sound("./Effects/car_skids.wav")
soundScream=pygame.mixer.Sound("./Effects/screaming.wav")


# Load the audio file
audio_path = "./Effects/car_skids.wav"
audio = AudioSegment.from_file(audio_path)

# Set the duration you want to keep
duration_to_keep = 3 * 1000  # Keep the first 3 seconds (convert to milliseconds)

# Shorten the audio
shortened_audio = audio[duration_to_keep:]

# Export the shortened audio to a new file
output_path = "./Effects/shortened_skids.wav"
shortened_audio.export(output_path, format="wav")

# Update the soundSkid variable to use the shortened audio
soundSkid = pygame.mixer.Sound(output_path)

soundSkid.play()