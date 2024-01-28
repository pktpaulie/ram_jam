#Audio recording and fft came from the example at
#https://gist.github.com/ZWMiller/53232427efc5088007cab6feee7c6e4c

"""
The following installations are required for the ramjam to run
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

# Load and transform the background images
background_1 = os.path.abspath("Background/Background1.png")
background_2 = os.path.abspath("Background/Background2.png")
background_3 = os.path.abspath("Background/Background3.png")
background_4 = os.path.abspath("Background/Background4.png")
background_5 = os.path.abspath("Background/Background5.png")
background_6 = os.path.abspath("Background/Background6.png")

background_images = [
    pygame.image.load(background_1),
    pygame.image.load(background_2),
    pygame.image.load(background_3),
    pygame.image.load(background_4),
    pygame.image.load(background_5),
    pygame.image.load(background_6),
]

background_start = os.path.abspath("Background/Start.jpg")
background_title = os.path.abspath("Background/Title.png")
background_finish = os.path.abspath("Enemies_And_Obstacles/Checkered_Flag.png")
title_image = pygame.image.load(background_title)
title_image = pygame.transform.scale(title_image, (120, 120))
start_image = pygame.image.load(background_start)

game_state = "start_up"

# Load the start up menu
def draw_start_menu():
    win.fill((0, 0, 0))
    font = pygame.font.SysFont("arial", 40)
    start_button = font.render("START JAMMING", True, (255, 255, 255))
    win.blit(title_image, (screen_width/2 - title_image.get_width()/2, screen_height/2 - title_image.get_height()/2))
    win.blit(start_button, (screen_width/2 - start_button.get_width()/2, screen_height/2 + start_button.get_height()/2))
    #win.blit(start_image, (0, 0))
    pygame.display.update()

# Load the gamer over screen
def draw_game_over_screen():
   win.fill((0, 0, 0))
   font = pygame.font.SysFont('arial', 40)
   title = font.render('Game Over', True, (255, 255, 255))
   restart_button = font.render('R - Restart', True, (255, 255, 255))
   quit_button = font.render('Q - Quit', True, (255, 255, 255))
   win.blit(title, (screen_width/2 - title.get_width()/2, screen_height/2 - title.get_height()/3))
   win.blit(restart_button, (screen_width/2 - restart_button.get_width()/2, screen_height/1.9 + restart_button.get_height()))
   win.blit(quit_button, (screen_width/2 - quit_button.get_width()/2, screen_height/2 + quit_button.get_height()/2))
   pygame.display.update()

#check image loaded and transform it
def check_image_loading(img):
    try:
        background_image = pygame.image.load(img)
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        sys.exit(1)
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    
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

# Acceleration factor
acceleration_factor = 1.2

crashed = False
jumping = False
jump_count = [5]
banana_peel_active = True
gaming = False

# Object current coordinates
x = 0
y = 380
start_y = y

# Initial velocity / speed of movement
initial_vel = 1

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
#The next two variables are globals used for debounce of the microphone.
#I'm using a list with one element because lists are mutable, and
#mutable globals are passed by reference into functions.
soundTimeOne=[0]
soundTimeTwo=[0]
 
# Function for mic in
def micFunction(in_data, soundOne, soundTwo):
    soundOne[0]=pygame.time.get_ticks()
    audio_data = np.fromstring(in_data, np.int16)
    max_vol = np.argmax(audio_data)
    dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))
    maxLocation=np.argmax(dfft)
    #maxLocation corresponds to the frequency of the most intense sound
    #of the word spoken in to the microphone. The word Cold has a low frequency
    #starting sound. Chime has a medium frequency, and Soup starts with a high
    #frequency.
    
    #The if statement is for the debouncing of the mic.
    #Only go on if it is more than 200ms since the last sound.
    if(soundOne[0]>(soundTwo[0]+200)):

        soundTwo[0]=pygame.time.get_ticks()
        soundTimeTwo[0]=soundTwo[0]
        
        if((maxLocation>15) and (maxLocation<40 ) and (max_vol>800)):
            slowAction()
        elif((maxLocation>40) and (maxLocation<90) and (max_vol>800)):
            jumpAction(jump_count)
        elif ((maxLocation>90) and (max_vol>800)):
            startStopAction()
            print(max_vol)
     
#Separate thread for the sound effect
def accel_sound_function():
    soundAccel.play(10000)
    pygame.time.delay(1000)  #Play the sound for 1000 milliseconds
    # soundAccel.stop()
    sys.exit()

def startStopAction():
    print("Soup")


def jumpAction(jump_val):
    print("Chime")
    if jump_val[0] >= -5:
        neg = 1
        if jump_val[0] < 0:
            neg = -1
        y -= (jump_val[0] ** 2) * 0.5 * neg
        jump_val[0] -= 1
    else:
        jumping = False
        jump_val[0] = 5

def slowAction():
    print("Cold")

def load_background(img_location, index, iterator):
    current_background = img_location[index]
    win.blit(current_background, (screen_width+iterator, 0))

# Load the car image
car_image_bee = os.path.abspath("Character_Sprites/Bee_Car2.png")
banana_peel_image = os.path.abspath("Effects/Banana_Peel.png")
car_image_trex = os.path.abspath("Character_Sprites/TRex_Car2.png")
car_image_chicken=os.path.abspath("Character_Sprites/Chicken_Car2.png")


car_image_object = pygame.image.load(car_image_trex)
car_rect_orig = car_image_object.get_rect()
car_number=0

#Scale car image
car_w, car_h = 100, 75
car_image_object = pygame.transform.scale(car_image_object, (car_w, car_h))
car_rect = car_image_object.get_rect()

banana_w, banana_h = 50, 50
banana_peel_active = False  # Flag to indicate if the banana peel is active
banana_peel_timer = 5 * 30  # Timer for 5 seconds (30 frames per second)

timer = pygame.time.Clock()

# Infinite loop
while not crashed:
    pygame.time.delay(10)    
    #Start the mic recording. (You can comment the next line out to ignore)
    micFunction(stream.read(CHUNK), soundTimeOne, soundTimeTwo)

    for event in pygame.event.get():
        # Store keys pressed
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if game_state == "start_up":
            #pygame.time.delay(10)
            
            draw_start_menu()
            
            if event.type == pygame.KEYDOWN:
                # Store keys pressed
                keys = pygame.key.get_pressed()
                if event.key == pygame.K_SPACE:
                    # Clear the screen
                    #win.fill((0, 0, 0))
                    #win.blit(background_images[0], (iterator, 0))
                    print("***********starting************")
                    #current_vel = initial_vel
                    game_state = "game"
                    game_over = False
                elif event.key == pygame.QUIT:
                    quit()
                    
                
        elif game_state == "game_over":
            
            draw_game_over_screen()
            print("***********game over************")
            # Store keys pressed
            keys = pygame.key.get_pressed()
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_r]:
                    game_state = "start_up"
                if keys[pygame.K_q]:
                    pygame.quit()
                    quit()

        elif game_state == "game": 
            #pygame.time.delay(10)   
            
            win.blit(background_images[0], (iterator, 0))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_state = "game_over"
                    gaming = False
                else:
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
                    # change car style if user presses C
                    elif event.key == pygame.K_c:
                        car_w, car_h = 100, 75
                        if(car_number==0):
                            car_image_object = pygame.image.load(car_image_bee)
                            car_image_object = pygame.transform.scale(car_image_object, (car_w, car_h))
                            car_rect = car_image_object.get_rect()
                        elif(car_number==1):
                            car_image_object = pygame.image.load(car_image_chicken)
                            car_image_object = pygame.transform.scale(car_image_object, (car_w, car_h))
                            car_rect = car_image_object.get_rect()
                        elif(car_number==2):
                            car_image_object = pygame.image.load(car_image_trex)
                            car_image_object = pygame.transform.scale(car_image_object, (car_w, car_h))
                            car_rect = car_image_object.get_rect()
                        car_number=(car_number+1)%3

                    if current_vel != 0 and not skid_active:
                        T = Thread(target=accel_sound_function)
                        T.start()         

            gaming = True
        elif game_over:
            game_state = "game_over"
            game_over = False

    if gaming and not game_over:    
        # Move the car continuously in the positive x-direction
        x += current_vel

        if current_vel == 0:
            soundAccel.stop()
            soundIdle.play()

        # Ensure the car stays within the screen boundaries
        #x = max(0, min(x, screen_width*2/3 - car_rect.width))

        # If the car goes off the right side of the window, reset its position
        if x > screen_width + 50:
            x = 0 - car_rect.width

        # Store keys pressed
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and not jumping:   
            jumping = True

        # Jumping mechanism
        if jumping:
            jumpAction(jump_count)
            """ if jump_count >= -5:
                neg = 1
                if jump_count < 0:
                    neg = -1
                y -= (jump_count ** 2) * 0.5 * neg
                jump_count -= 1
            else:
                jumping = False
                jump_count = 5 """

        # Simulated gravity when not jumping
        if not jumping and y < start_y: #screen_height - car_rect.height:
            y += 2

        #load_background(background_1, iterator)
        if current_vel > 0:
            iterator -= background_scroll_speed
            load_background(background_images, current_background_index, iterator)

        # Draw the car image at the updated position
        win.blit(car_image_object, (x, y))

        if skid_active:
            skid_timer += 1
            if skid_timer >= skid_duration:
                skid_active = False
                skid_timer = 0
                current_vel = 0  # Stop the car after skid
                soundAccel.play()  # Resume acceleration sound

        if banana_peel_active:
            #print("banana peel active!!")
            win.blit(pygame.image.load(banana_peel_image), (240, 420))  # Keep y-coordinate as 420

            # Check for skid initiation
            if 240 - x <= 80 and not skid_active:
                skid_active = True
                skid_timer = 0
                skid_rotation_angle = 60  # Set an initial rotation angle
                print("Skid initiated!!")
                banana_peel_active = False  # Deactivate the banana peel
                print("banana peel deactivated!!")
                print("I am here")
                banana_peel_x = random.randint(0, screen_width - banana_w)
                banana_peel_timer = 5 * 30  # Reset the timer
                soundSkid.play()  # Play skid sound when skid is initiated

            # Draw the rotating skid effect if a skid is active
            if skid_active:
                print("I am there!!")
                for _ in range(5):  # Rotate the car 5 times for a short duration
                    rotated_car = pygame.transform.rotate(car_image_object, skid_rotation_angle)
                    rotated_car_rect = rotated_car.get_rect(center=(x + car_w / 2, y + car_h / 2))
                    win.blit(rotated_car, rotated_car_rect.topleft)
                    pygame.display.update()  # Update the display to show the rotated image
                    pygame.time.delay(50)  # Delay to control the speed of rotation

                # Update the total skid rotation angle for the next frame
                skid_rotation_angle += 5  # Increase the rotation speed

                # Check for the end of skid effect
                if skid_rotation_angle >= 360 * 4:  # Rotate 4 times (adjust as needed)
                    skid_active = False
                    soundSkid.stop()  # Stop skid sound when skid effect ends
                    soundAccel.play()  # Resume acceleration sound
                skid_active = False
                print(skid_active)

            else:
                # Draw the car image at the updated position without rotation
                win.blit(car_image_object, (x, y))
                # Check for skid initiation
                if 300 - x <= 80 and not skid_active:
                    skid_active = True
                    skid_timer = 0
                    print("Skid initiated!!")
                    banana_peel_active = False  # Deactivate the banana peel
                    print("banana peel deactivated!!")
                    banana_peel_x = random.randint(0, screen_width - banana_w)
                    banana_peel_timer = 5 * 30  # Reset the timer
                    soundSkid.play()  # Play skid sound when skid is initiated

                elif skid_timer < 5000:  # Adjust the duration as needed
                    skid_timer += 1
                else:
                    skid_active = False
                    soundSkid.stop()  # Stop skid sound when skid effect ends
                    soundAccel.play()       

        # Refresh the window
        pygame.display.update()

        # Check if it's time to change the background
        if iterator <= -screen_width:
            current_background_index = (current_background_index + 1) % len(background_images)
            iterator = 0  

        timer.tick(30)
# Close up mic recording
stream.stop_stream()
stream.close()

audio.terminate()


# Close the Pygame window
pygame.quit()
sys.exit()




