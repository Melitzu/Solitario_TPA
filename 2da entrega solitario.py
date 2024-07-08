import pygame
import random
import sys

#Iniciar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO, ALTO = 1700, 1000 
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Solitario") #establecer titulo de la interfaz grafica

#Se definen algunos colores
BLANCO = (255, 255, 255)
VERDE = (0, 128, 0)
ROJO = (255, 0, 0)
NEGRO = (0, 0, 0)

# Configuración de fuentes
fuente = pygame.font.SysFont(None, 30)

# Constantes
ANCHO_CARTA = 120
ALTO_CARTA = 160
ESPACIO = 20
ESPACIO_COLUMNAS = 120

# Función para crear la baraja
def crear_baraja():
    palos = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
    valores = ['A','2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',]
    baraja = [{'palo': palo, 'valor': valor} for palo in palos for valor in valores]
    random.shuffle(baraja)
    return baraja

# Función para dibujar una carta
def dibujar_carta(cartas, x, y):
    pygame.draw.rect(PANTALLA, BLANCO, (x, y, ANCHO_CARTA, ALTO_CARTA))
    pygame.draw.rect(PANTALLA, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA), 2)
    texto_valor = fuente.render(cartas['valor'], True, NEGRO)
    texto_palo = fuente.render(cartas['palo'], True, ROJO if cartas['palo'] in ['Corazones', 'Diamantes'] else NEGRO)
    PANTALLA.blit(texto_valor, (x + 5, y + 5))
    PANTALLA.blit(texto_palo, (x + 5, y + 30))

# Variable global para rastrear cuántas cartas se han volteado
cartas_volteadas = 0

# Función para dibujar la baraja
def dibujar_baraja(baraja):
    x_reveladas = ANCHO - ESPACIO - ANCHO_CARTA  # Posición inicial para las cartas reveladas
    y_reveladas = ALTO - ALTO_CARTA - ESPACIO
    for cartas in baraja[:3]:  # Solo se dibujan las primeras tres cartas reveladas
        dibujar_carta(cartas, x_reveladas, y_reveladas)
        x_reveladas -= ESPACIO

    # Dibujar las cartas restantes boca abajo a la izquierda del mazo
    x_volteadas = ESPACIO  # Posición inicial para las cartas volteadas
    y_volteadas = ALTO - ALTO_CARTA - ESPACIO
    for cartas in baraja[3:]:
        dibujar_carta_boca_abajo(x_volteadas, y_volteadas)
        x_volteadas += ESPACIO

# Función para dibujar una carta boca abajo
def dibujar_carta_boca_abajo(x, y):
    pygame.draw.rect(PANTALLA, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA))

# Función para manejar eventos de clic del ratón
def manejar_clic_raton(baraja, columnas):
    global cartas_volteadas
    pos_raton = pygame.mouse.get_pos()
    for columna in columnas:
        if columna['rect'].collidepoint(pos_raton):
            if columna['cartas']:
                carta = columna['cartas'][-1]
                if carta['boca_abajo']:
                    if cartas_volteadas < 3:  # Solo se pueden voltear hasta tres cartas
                        carta['boca_abajo'] = False
                        cartas_volteadas += 1
                else:
                    carta['boca_abajo'] = True
                    cartas_volteadas -= 1
                return

# Función para manejar eventos
def manejar_eventos(baraja, columnas):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            manejar_clic_raton(baraja, columnas)

# Función principal del juego
def main():
    baraja = crear_baraja()
    columnas = [{'cartas': [], 'rect': pygame.Rect(ESPACIO + i * (ANCHO_CARTA + ESPACIO_COLUMNAS), ESPACIO, ANCHO_CARTA, ALTO - 2 * ESPACIO)} for i in range(7)]

    # Distribuir cartas en las columnas
    for i, columna in enumerate(columnas):
        for j in range(i + 1):
            carta = baraja.pop()
            if j == i:
                carta['boca_abajo'] = False
            else:
                carta['boca_abajo'] = True
            columna['cartas'].append(carta)

    # Bucle principal del juego
    while True:
        PANTALLA.fill(VERDE)
        dibujar_baraja(baraja)
        for columna in columnas:
            x, y = columna['rect'].topleft
            for carta in columna['cartas']:
                if carta['boca_abajo']:
                    pygame.draw.rect(PANTALLA, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA))
                else:
                    dibujar_carta(carta, x, y)
                y += ESPACIO // 4
        manejar_eventos(baraja, columnas)
        pygame.display.flip()

if __name__ == "__main__":
    main()
