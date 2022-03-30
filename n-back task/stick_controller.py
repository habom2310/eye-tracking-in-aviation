import pygame
import sys
import datetime
import time
from pygame_button import PygameButton
import sound_sequences
import glob 
import os

soundfile_paths = glob.glob(os.path.join(os.path.dirname(__file__),'sound_samples/*.wav'))
pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
pygame.mixer.init()
pygame.joystick.init()

print(pygame.joystick.get_count())
_joystick = pygame.joystick.Joystick(0)
_joystick.init()
print(_joystick.get_init())
print(_joystick.get_id())
print(_joystick.get_name())
clock = pygame.time.Clock()

# logging variables settings
data = []


# pynput settings
from pynput import keyboard
from pynput.keyboard import Key, Controller
keyboard_controller = Controller()

def on_press(key):
    try: k = key.char # single-char keys
    except: k = key.name # other keys
    if 'char' in dir(key):     
        if key.char == 'q':
            timestamp = round(time.time() * 1000)
            datapoint = {"event": "pressed", "time": timestamp}
            try: 
                screen.fill(green)
            except:
                pass
            print(datapoint)
            data.append(datapoint)
            print("q pressed")

lis = keyboard.Listener(on_press=on_press)
lis.start() # start to listen on a separate thread
# lis.join() # no this if main thread is polling self.keys

# background
white = (255, 255, 255)
# text color
black = (0, 0, 0)
#green
green = (0, 255, 0)
# light shade of the button
color_light = (200,200,200)  
# dark shade of the button
color_dark = (140,140,140)

# -------- Set up the Window -----------
# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
width = SCREEN_WIDTH
height = SCREEN_HEIGHT

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("N-Back Task")

# program text settings
label_text_font = pygame.font.SysFont("Calibri", 50)
label_text = label_text_font.render('N-Back Task', True, black)
label_text_center = (int(width/2),int(height/5))

def display_number(number, screen):
    nback_text_font = pygame.font.SysFont("Calibri", 70)
    nback_text = nback_text_font.render(str(number), True, black)
    screen.blit(nback_text, screen.blit(nback_text, nback_text.get_rect(center = (width/2,height/2))))

# button set 1-back sequence
btnSet1_text = "1-back"
btnSet1_textsize = 40
btnSet1_textcolor = (0,0,0)
btnSet1_size = (120,120)
btnSet1_center = (int(width/5),int(2*height/5))
btnSet1 = PygameButton(btnSet1_center, btnSet1_size, color_light, color_dark, btnSet1_text, btnSet1_textsize, btnSet1_textcolor)

# button set 2-back sequence
btnSet2_text = "2-back"
btnSet2_textsize = 40
btnSet2_textcolor = (0,0,0)
btnSet2_size = (120,120)
btnSet2_center = (int(4*width/5),int(2*height/5))
btnSet2 = PygameButton(btnSet2_center, btnSet2_size, color_light, color_dark, btnSet2_text, btnSet2_textsize, btnSet2_textcolor)

# button text setting 
btnStart_text = "Start"
btnStart_textsize = 40
btnStart_textcolor = (0,0,0)
btnStart_size = (200,120)
btnStart_center = (int(width/2),int(3*height/4))
btnStart = PygameButton(btnStart_center, btnStart_size, color_light, color_dark, btnStart_text, btnStart_textsize, btnStart_textcolor)

# ------- Status bar settings -----------
def status_bar(text, screen):
    # status bar
    text_font = pygame.font.SysFont("Calibri", 20)
    text_screen = text_font.render(text, True, black)
    screen.blit(text_screen, (5,height-20))

# -------- Playing sound sequence -----------
def play_sound(number):
    filepath = soundfile_paths[number-1]
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

# -------- Logging data to file -----------
def logging(data):
    save_path = os.path.join(os.path.dirname(__file__), f"data/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(save_path, "w+") as f:
        f.write("time,event\n")
        for datapoint in data:
            f.write(str(datapoint["time"]) + "," + str(datapoint["event"]) + "\n")


# -------- Main Program Loop -----------
done = False
is_running = False
is_statusbar = False
n_task = 0
statusbar_counter = 0
sound_counter = 0
time_between_number = 2
clock_rate = 10
current_index = 0
number_sequence = []
is_btnSet1_selected = False
is_btnSet2_selected = False
while not done:
    screen.fill(white)

    # print(_joystick.get_button(0))

    # --- Sound playing -----
    
    if is_running:
        if sound_counter == 0:
            number = number_sequence[current_index]
            play_sound(number)
            timestamp = round(time.time() * 1000)
            sound_counter = clock_rate*time_between_number
            datapoint = {"event": number, "time": timestamp}
            print(datapoint)
            data.append(datapoint)
        else:
            sound_counter -= 1

        if sound_counter == 0:
            if current_index == len(number_sequence)-1:
                is_running = False
                sound_counter = 0
                current_index = 0
                logging(data)
                data = []
            else:
                current_index += 1


    # --- Event handler -----
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.

        elif event.type == pygame.JOYBUTTONDOWN:
            # if is_running == True: # any button press
            if _joystick.get_button(0) == 1 and is_running == True: # only button 1 is accepted
                timestamp = round(time.time() * 1000)
                datapoint = {"event": "pressed", "time": timestamp}
                screen.fill(green)
                print(datapoint)
                data.append(datapoint)

        #checks if a mouse is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and is_running == False:
            #if the mouse is clicked on the
            mouse_pos = pygame.mouse.get_pos()
            # print(mouse_pos)

            # button the game is terminated
            if btnStart.check_click(mouse_pos):
                print("Start button is clicked")
                if n_task == 0:
                    status_text = "Please select a task."
                    statusbar_counter = clock_rate * 3
                    is_statusbar = True
                    is_running = False
                else:
                    is_running = True
                    if n_task == 1:
                        number_sequence = sound_sequences.SET1
                    elif n_task == 2:
                        number_sequence = sound_sequences.SET2

                    timestamp = round(time.time() * 1000)
                    datapoint = {"event": "Start", "time": timestamp}
                    print(datapoint)
                    data.append(datapoint)
                    
            elif btnSet1.check_click(mouse_pos):
                print("1-back")
                n_task = 1
                status_text = "1-back chosen"
                statusbar_counter = clock_rate * 3
                is_statusbar = True
                is_btnSet1_selected = True
                is_btnSet2_selected = False

            elif btnSet2.check_click(mouse_pos):
                print("2-back")
                n_task = 2
                status_text = "2-back chosen"
                statusbar_counter = clock_rate * 3
                is_statusbar = True
                is_btnSet1_selected = False
                is_btnSet2_selected = True

    # ------------ Start drawing ---------------            

    if is_statusbar == True:
        status_bar(status_text, screen)
        statusbar_counter -= 1
        if statusbar_counter == 0:
            is_statusbar = False
            status_text = ""
    if is_running == False:
        screen.blit(label_text, label_text.get_rect(center = label_text_center))
        btnSet1.draw(screen, is_btnSet1_selected)
        btnSet2.draw(screen, is_btnSet2_selected)
        btnStart.draw(screen)
    else:
        number = number_sequence[current_index]
        display_number(number, screen)

    # updates the frames of the game
    pygame.display.update()

    clock.tick(clock_rate)
pygame.quit()