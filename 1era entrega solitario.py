import pygame
import sys

# Inicializar Pygame
pygame.init()

# Definir colores
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)

# Definir dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 70, 100

# Crear la ventana del juego
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solitario")

# Clase para representar una carta
class Card:
    def __init__(self, value, suit, x, y):
        self.value = value
        self.suit = suit
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.dragging = False

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(f"{self.value} {self.suit}", True, GREEN)
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))

# Función para manejar los eventos del juego
def handle_events(cards):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for card in cards:
                    if card.rect.collidepoint(event.pos):
                        card.dragging = True
                        offset_x = card.rect.x - event.pos[0]
                        offset_y = card.rect.y - event.pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for card in cards:
                    card.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            for card in cards:
                if card.dragging:
                    card.rect.x = event.pos[0] + offset_x
                    card.rect.y = event.pos[1] + offset_y

# Función principal del juego
def main():
    # Crear cartas
    cards = []
    x, y = 50, 50
    for value in range(1, 6):
        for suit in ['Spades', 'Hearts', 'Diamonds', 'Clubs']:
            card = Card(value, suit, x, y)
            cards.append(card)
            x += CARD_WIDTH + 20
        y += CARD_HEIGHT + 20
        x = 50

    # Bucle principal del juego
    while True:
        screen.fill((0, 0, 0))
        handle_events(cards)
        for card in cards:
            card.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()
