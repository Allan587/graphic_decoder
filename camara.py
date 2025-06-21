import pygame

class Camara:
    def __init__(self):
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.arrastrando = False
        self.ultimo_mouse = (0, 0)

    def aplicar_transformacion(self, x, y):
        return int(x * self.zoom + self.offset_x), int(y * self.zoom + self.offset_y)

    def manejar_eventos(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 4:  # Scroll up
                self.zoom *= 1.1
            elif evento.button == 5:  # Scroll down
                self.zoom /= 1.1
            elif evento.button == 1:  # Click izquierdo
                self.arrastrando = True
                self.ultimo_mouse = pygame.mouse.get_pos()
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1:
                self.arrastrando = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastrando:
            x, y = pygame.mouse.get_pos()
            dx = x - self.ultimo_mouse[0]
            dy = y - self.ultimo_mouse[1]
            self.offset_x += dx
            self.offset_y += dy
            self.ultimo_mouse = (x, y)
