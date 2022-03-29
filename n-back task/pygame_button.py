import pygame

class PygameButton(object):
    def __init__(self, center, size, color=(255,255,255), selected_color=(200,200,200), text='', text_size = 18, text_color = (0,0,0)):
        btn_topleft = (center[0] - size[0]/2, center[1] - size[1]/2)

        self.rect = pygame.Rect(btn_topleft, size)
        self.color = color
        self.selected_color = selected_color
        self.text = pygame.font.SysFont("Calibri", text_size).render(text, True, text_color)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

    def draw(self, screen, is_selected=False):
        if is_selected:
            color = self.selected_color
        else:
            color = self.color
        pygame.draw.rect(screen, color, self.rect)
        screen.blit(self.text, self.text.get_rect(center = self.rect.center))
