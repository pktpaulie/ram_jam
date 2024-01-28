#Audio recording and fft came from the example at
#https://gist.github.com/ZWMiller/53232427efc5088007cab6feee7c6e4c

"""
The following installations are required for the ramjam game to run
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
    #import pylab
    from scipy.io import wavfile
    import time
    import seaborn as sns
    #from ctypes import c_int64
    
except:
    print("Something didn't import")


# GLOBAL VARIABLES



banana_w, banana_h = 50, 50
#banana_peel_active = False  # Flag to indicate if the banana peel is active
banana_peel_timer = 5 * 30  # Timer for 5 seconds (30 frames per second)
banana_peel = [True]

screen_width = 500
screen_height = 500

# Object current coordinates
#x = 0
y = [380] #410
start_y = y[0]

# Initial velocity / speed of movement
initial_vel = 1

# Acceleration factor
acceleration_factor = 1.2

# Indicates Pygame is running/ not crashed

is_jumping = [False]
jump_val = [5]



# Set skid variables
skid = [False]
skid_duration = 40  # Skid duration in frames
skid_rotation_angle = 0
duration_to_keep = 3 * 1000  # Keep the first 3 seconds (convert to milliseconds)

#Set up the microphone recording 
FORMAT = pyaudio.paInt16 # We use 16bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 1024 # 1024bytes of data red from a buffer
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

#The next two variables are globals used for debounce of the microphone.
#I'm using a list with one element because lists are mutable, and
#mutable globals are passed by reference into functions.
soundTimeOne=[0]
soundTimeTwo=[0]




# LOADING ASSETS 
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

# Load the car image
car_image_bee = os.path.abspath("Character_Sprites/Bee_Car2.png")
banana_peel_image = os.path.abspath("Effects/Banana_Peel.png")
car_image_trex = os.path.abspath("Character_Sprites/TRex_Car2.png")
car_image_chicken=os.path.abspath("Character_Sprites/Chicken_Car2.png")
monkey_image = os.path.abspath("Enemies_And_Obstacles/Monkey1.png")



# Start and Finish Images
background_title = os.path.abspath("Background/Title.png")
background_finish = os.path.abspath("Enemies_And_Obstacles/Checkered_Flag.png")
background_explosion = os.path.abspath("Character_Sprites/Explosion.png")
title_image = pygame.image.load(background_title)
title_image = pygame.transform.scale(title_image, (120, 120))
finish_image = pygame.image.load(background_finish)
finish_image = pygame.transform.scale(finish_image, (100, 100))
Explosion_image = pygame.image.load(background_explosion)
Explosion_image = pygame.transform.scale(Explosion_image, (120, 130))


# Load the audio file
audio_path = "./Effects/car_skids.wav"




# FUNCTIONS

def startStopAction(current_speed): #Accelerate
    current_speed = accelerate(current_speed)
    print("Soup")
    return current_speed

def jumpAction():
    is_jumping[0] = True
    jumping(is_jumping, y, jump_val)
    print("Chime")

def slowAction(current_speed):
    current_speed = deccelerate(current_speed)
    print("Cold")
    return current_speed

# Function for mic in
def micFunction(in_data, soundOne, soundTwo, current_vel):
    soundOne[0]=pygame.time.get_ticks()
    audio_data = np.fromstring(in_data, np.int16)
    max_vol = np.argmax(audio_data)
    dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))
    maxLocation=np.argmax(dfft)
    volume_threshold = 650
    #maxLocation corresponds to the frequency of the most intense sound
    #of the word spoken in to the microphone. The word Cold has a low frequency
    #starting sound. Chime has a medium frequency, and Soup starts with a high
    #frequency.
    
    #The if statement is for the debouncing of the mic.
    #Only go on if it is more than 200ms since the last sound.
    if(soundOne[0]>(soundTwo[0]+200)):
        soundTwo[0]=pygame.time.get_ticks()
        soundTimeTwo[0]=soundTwo[0]
        
        if((maxLocation>12) and (maxLocation<40 ) and (max_vol>volume_threshold)):
            current_vel = slowAction(current_vel)
        elif((maxLocation>40) and (maxLocation<90) and (max_vol>volume_threshold)):
            jumpAction()
        elif ((maxLocation>90) and (max_vol>volume_threshold)):
            current_vel = startStopAction(current_vel)
            #print(max_vol)
    return current_vel


# def load_background(img_location, index, iterator):
#     current_background = img_location[index]
#     win.blit(current_background, (screen_width+iterator, 0))

# Load the start up menu
def draw_start_menu(win):
    win.fill((0, 0, 0))
    font = pygame.font.SysFont("arial", 40)
    start_button = font.render("START JAMMING", True, (255, 255, 255))
    win.blit(title_image, (screen_width/2 - title_image.get_width()/2, screen_height/2 - title_image.get_height()/2))
    win.blit(start_button, (screen_width/2 - start_button.get_width()/2, screen_height/2 + start_button.get_height()/2))
    #win.blit(start_image, (0, 0))
    pygame.display.update()


def jumping(jumping, y_cord, jump_count):
    
     # Jumping mechanism
    if jumping[0]:
        if jump_count[0] >= -5:
            neg = 1
            if jump_count[0] < 0:
                neg = -1
            y_cord[0] -= (jump_count[0] ** 2) * 0.5 * neg
            jump_count[0] -= 1
        else:
            jumping[0] = False
            jump_count[0] = 5
    # Simulated gravity when not jumping
    if not jumping[0] and y_cord[0] < start_y: #screen_height - car_rect.height:
        y_cord[0] += 2

def banana_function(skid_active, banana_peel_active, win, x, car_image_object, car_h, car_w, soundSkid, soundAccel):
        skid_timer = 0
        if skid_active[0]:
            skid_timer += 1
            if skid_timer >= skid_duration:
                skid_active[0] = False
                skid_timer = 0
                current_vel = 0  # Stop the car after skid
                soundAccel.play()  # Resume acceleration sound

        if banana_peel_active[0]:
            win.blit(pygame.image.load(banana_peel_image), (240, 420))  # Keep y-coordinate as 420

            # Check for skid initiation
            if 240 - x <= 80 and not skid_active[0]:
                skid_active[0] = True
                skid_timer = 0
                skid_rotation_angle = 60  # Set an initial rotation angle
                print("Skid initiated!!")
                banana_peel_active[0] = False  # Deactivate the banana peel
                print("banana peel deactivated!!")
                #banana_peel_x = random.randint(0, screen_width - banana_w)
                #banana_peel_timer = 5 * 30  # Reset the timer
                soundSkid.play()  # Play skid sound when skid is initiated

            # Draw the rotating skid effect if a skid is active
            if skid_active[0]:
                print("I am there!!")
                for _ in range(5):  # Rotate the car 5 times for a short duration
                    rotated_car = pygame.transform.rotate(car_image_object, skid_rotation_angle)
                    rotated_car_rect = rotated_car.get_rect(center=(x + car_w / 2, y[0] + car_h / 2))
                    win.blit(rotated_car, rotated_car_rect.topleft)
                    pygame.display.update()  # Update the display to show the rotated image
                    pygame.time.delay(50)  # Delay to control the speed of rotation

                # Update the total skid rotation angle for the next frame
                skid_rotation_angle += 5  # Increase the rotation speed

                # Check for the end of skid effect
                if skid_rotation_angle >= 360 * 4:  # Rotate 4 times (adjust as needed)
                    skid_active[0] = False
                    soundSkid.stop()  # Stop skid sound when skid effect ends
                    soundAccel.play()  # Resume acceleration sound
                skid_active[0] = False
                print(skid_active[0])

            else:
                # Draw the car image at the updated position without rotation
                win.blit(car_image_object, (x, y[0]))
                # Check for skid initiation
                if 300 - x <= 80 and not skid_active[0]:
                    skid_active[0] = True
                    skid_timer = 0
                    print("Skid initiated!!")
                    banana_peel_active[0] = False  # Deactivate the banana peel
                    print("banana peel deactivated!!")
                    #banana_peel_x = random.randint(0, screen_width - banana_w)
                    #banana_peel_timer = 5 * 30  # Reset the timer
                    soundSkid.play()  # Play skid sound when skid is initiated

                elif skid_timer < 5000:  # Adjust the duration as needed
                    skid_timer += 1
                else:
                    skid_active[0] = False
                    soundSkid.stop()  # Stop skid sound when skid effect ends
                    soundAccel.play()

def deccelerate(current_vel):
    if current_vel > 0:
        current_vel -= acceleration_factor
        print("Deccelerating*****")
        print(current_vel)
    else:
        current_vel = 0
    return current_vel

def accelerate(speed):
    if speed >= 15:
        speed = 15
    else:
        print("Accelerating*****")
        speed += acceleration_factor
        print(speed)
    return speed


# MAIN
def __main__():
    monkey_active = False
    # Object current coordinates
    x = 0
    car_w, car_h = 100, 75
    crashed = False
    car_number = 0

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

    # Initialize Pygame
    pygame.init()

    start_time = pygame.time.get_ticks()
    current_time = start_time
    # Create the display surface object of specific dimensions 
    win = pygame.display.set_mode((screen_width, screen_height))
    
    # Set the Pygame window name
    pygame.display.set_caption("Ramjam")


    game_state = "start_up"

    # # Load the start up menu
    # def draw_start_menu():
    #     win.fill((0, 0, 0))
    #     font = pygame.font.SysFont("arial", 40)
    #     title = font.render("Ramjam", True, (255, 255, 255))
    #     start_button = font.render("Start", True, (255, 255, 255))
    #     win.blit(title, (screen_width/2 - title.get_width()/2, screen_height/2 - title.get_height()/2))
    #     win.blit(start_button, (screen_width/2 - start_button.get_width()/2, screen_height/2 + start_button.get_height()/2))
    #     pygame.display.update()

    # #check image loaded and transform it
    # def check_image_loading(img):
    #     try:
    #         background_image = pygame.image.load(img)
    #     except pygame.error as e:
    #         print(f"Error loading background image: {e}")
    #         sys.exit(1)
    #     background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
        

    # Load the in all sound effects
    soundAccel=pygame.mixer.Sound("./Effects/Acceleration.wav")
    soundIdle=pygame.mixer.Sound("./Effects/idleEngine.wav")
    soundStart=pygame.mixer.Sound("./Effects/startEngine.wav")
    soundStop=pygame.mixer.Sound("./Effects/stopEngine.wav")
    soundBanana=pygame.mixer.Sound("./Effects/banana.wav")
    soundMonkey=pygame.mixer.Sound("./Effects/monkey_sounds.wav")
    soundBounce=pygame.mixer.Sound("./Effects/bounce_tires.wav")
    #soundSkid=pygame.mixer.Sound("./Effects/car_skids.wav")
    soundScream=pygame.mixer.Sound("./Effects/screaming.wav")

    """
    Shorten the skid sound
    """
    audio1 = AudioSegment.from_file(audio_path)
    shortened_audio = audio1[duration_to_keep:]      # Shorten the audio
    output_path = "./Effects/shortened_skids.wav"   # Export the shortened audio to a new file
    shortened_audio.export(output_path, format="wav")
    soundSkid = pygame.mixer.Sound(output_path)     # Update the soundSkid variable to use the shortened audio

    audio = pyaudio.PyAudio()
    # start Recording
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True)
    stream.start_stream()
        
    #Separate thread for the sound effect
    def accel_sound_function():
        soundAccel.play(50000)
        pygame.time.delay(1000)  #Play the sound for 1000 milliseconds
        # soundAccel.stop()
        soundIdle.stop()
        sys.exit()

    """
    Load and scale the car image
    """
    car_image_object = pygame.image.load(car_image_trex)
    car_rect_orig = car_image_object.get_rect()
    car_image_object = pygame.transform.scale(car_image_object, (car_w, car_h))
    car_rect = car_image_object.get_rect()   
    monkey_image_object = pygame.image.load(monkey_image)
    monkey_image_object = pygame.transform.scale(monkey_image_object, (120, 120))

    timer = pygame.time.Clock()

    draw_start_menu(win)
    pygame.time.delay(1000)

    # Infinite loop
    while not crashed:
        current_time = pygame.time.get_ticks()

        pygame.time.delay(10)
        # Clear the screen  #win.fill((0, 0, 0))
       
        if current_time > (start_time + 10000) and current_time < (start_time + 15000):
            pygame.time.delay(10)
            #print("gorilla")
            win.blit(monkey_image_object, (400, 310))
            monkey_active = True
            print("Monkey is activated")
            pygame.display.update()
        
        if monkey_active ==True:
            if 400-x<=20 and x>0:
                print("Car is closer!!")   
                monkey_active=False
                #crashed = True
                win.fill((0,0,0))
                win.blit(Explosion_image,(screen_width/2,screen_height/2)) 
                pygame.display.update()
                pygame.time.delay(1000)
                pygame.quit()
                quit()

        win.blit(background_images[0], (iterator, 0))

        #Start the mic recording. (You can comment the next line out to ignore)
        current_vel = micFunction(stream.read(CHUNK), soundTimeOne, soundTimeTwo, current_vel)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_vel = initial_vel
                elif event.key == pygame.K_RIGHT:
                    current_vel = accelerate(current_vel)
                elif event.key == pygame.K_LEFT:
                    current_vel = deccelerate(current_vel)
                elif event.key == pygame.K_q:
                    win.fill((0,0,0))
                    win.blit(finish_image, (screen_width*0.75,screen_height*0.75))  
                    pygame.display.update()
                    pygame.time.delay(1000)
                    pygame.quit()
                    quit()
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

                if current_vel != 0 and not skid[0]:
                    T = Thread(target=accel_sound_function)
                    T.start()
                    # soundAccel.play()
                    # soundIdle.stop()


        # Store keys pressed
        keys = pygame.key.get_pressed()

        if current_vel == 0:
            soundAccel.stop()
            soundIdle.play()

        # Move the car continuously in the positive x-direction
        x += current_vel
        # Ensure the car stays within the screen boundaries
        #x = max(0, min(x, screen_width*2/3 - car_rect.width))
        # If the car goes off the right side of the window, reset its position
        if x > screen_width + 50:
            x = 0 - car_rect.width
         
        if keys[pygame.K_UP] and not is_jumping[0]:   
            is_jumping[0] = True
        
        jumping(is_jumping, y, jump_val) # Car jump
        banana_function(skid, banana_peel, win, x, car_image_object, car_h, car_w, soundSkid, soundAccel)
    
        #load_background(background_1, iterator)
        if current_vel > 0:
            iterator -= background_scroll_speed
            current_background = background_images[current_background_index]
            win.blit(current_background, (screen_width+iterator, 0))
            if monkey_active:
                win.blit(monkey_image_object, (400, 310))
            #load_background(background_images, current_background_index, iterator)

        # Draw the car image at the updated position
        win.blit(car_image_object, (x, y[0]))

        # Refresh the window
        pygame.display.update()

        # Check if it's time to change the background
        if iterator <= -screen_width:
            current_background_index = (current_background_index + 1) % len(background_images)
            iterator = 0

        timer.tick(30)
    # Close up mic recording
    stream.stop_stream()
    stream.close()          # Close the mic stream
    audio.terminate()       # Stop all audio output  
    pygame.quit()           # Close the Pygame window
    sys.exit()

if __name__ == "__main__":
    __main__()

