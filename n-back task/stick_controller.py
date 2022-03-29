import pygame
import sys
import datetime

pygame.init()
pygame.joystick.init()

print(pygame.joystick.get_count())
_joystick = pygame.joystick.Joystick(0)
_joystick.init()
print(_joystick.get_init())
print(_joystick.get_id())
print(_joystick.get_name())
print(_joystick.get_numaxes())
print(_joystick.get_numballs())
print(_joystick.get_numbuttons())
print(_joystick.get_numhats())
print(_joystick.get_axis(0))
clock = pygame.time.Clock()

# background
white = (255, 255, 255)
# text color
black = (0, 0, 0)
# light shade of the button
color_light = (200,200,200)  
# dark shade of the button
color_dark = (140,140,140)

class TextPrint(object):
    def __init__(self):
        self.reset()

    def tprint(self, screen, textString):
        self.font = pygame.font.Font(None, 20)
        textBitmap = self.font.render(textString, True, black)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def number_display(self, screen, number):
        self.font = pygame.font.Font(None, 36)
        textBitmap = self.font.render(str(number), True, black)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 300
        self.y = 300
        self.line_height = 20

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

# button text setting 
btnStart_font = pygame.font.SysFont(None,30)
btnStart_text = btnStart_font.render('Start' , True , black)
btnStart_size = (200,120)
btnStart_topleft = (width/2 - btnStart_size[0]/2, height/2 - btnStart_size[1]/2)
btnStart_bottomright = (width/2 + btnStart_size[0]/2, height/2 + btnStart_size[1]/2)

# -------- Main Program Loop -----------
done = False
is_running = False
while not done:
    print(_joystick.get_button(0))

    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
        # elif event.type == pygame.JOYBUTTONDOWN:
        #     print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

        #checks if a mouse is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            #if the mouse is clicked on the
            # button the game is terminated
            if btnStart_topleft[0] <= mouse[0] <= btnStart_bottomright[0] and btnStart_topleft[1]<= mouse[1] <= btnStart_bottomright[1]:
                pygame.quit()
                sys.exit()

    screen.fill(white)

    # set the button hover

    # stores the (x,y) coordinates into
    # the variable as a tuple
    mouse = pygame.mouse.get_pos()
    print(mouse)
      
    # if mouse is hovered on a button it
    # changes to lighter shade 
    if btnStart_topleft[0] <= mouse[0] <= btnStart_bottomright[0] and btnStart_topleft[1]<= mouse[1] <= btnStart_bottomright[1]:
        pygame.draw.rect(screen,color_light,[btnStart_topleft[0],btnStart_topleft[1],btnStart_size[0],btnStart_size[1]])
    else:
        pygame.draw.rect(screen,color_dark,[btnStart_topleft[0],btnStart_topleft[1],btnStart_size[0],btnStart_size[1]])
        
    # superimposing the text onto our button
    screen.blit(btnStart_text , (width/2-25,height/2-7))
      
    # updates the frames of the game
    pygame.display.update()

    clock.tick(10)
pygame.quit()