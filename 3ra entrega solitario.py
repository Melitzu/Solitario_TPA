import pygame
import random
import sys

# Definir clase carta
class Carta:
    def __init__(self, palo, valor, boca_abajo=True):
        self.palo = palo
        self.valor = valor
        self.boca_abajo = boca_abajo

    def __repr__(self):
        return f"Carta({self.palo}, {self.valor}, boca_abajo={self.boca_abajo})"

# Definir clase columna
class Columna:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.cartas = []

    def agregar_carta(self, carta):
        self.cartas.append(carta)

    def quitar_carta(self):
        return self.cartas.pop() if self.cartas else None

    def voltear_ultima(self):
        if self.cartas and self.cartas[-1].boca_abajo:
            self.cartas[-1].boca_abajo = False

    def __repr__(self):
        return f"Columna({self.rect}, {self.cartas})"

# Definir clase solitario
class Solitario:
    def __init__(self, ancho, alto, titulo):
        self.ancho = ancho
        self.alto = alto
        self.pantalla = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption(titulo)
        self.columnas = []
        self.mazo = []
        self.cartas_reveladas = []
        self.carta_arrastrada = None
        self.pos_inicial = None
        self.columna_origen = None

    def agregar_columna(self, columna): #Agrega una columna al juego
        self.columnas.append(columna)

    def agregar_mazo(self, mazo): #Agrega el mazo de cartas al juego
        self.mazo = mazo

    def dibujar(self): #Dibuja el estado actual del juego en la pantalla.
        self.pantalla.fill(VERDE)
        for columna in self.columnas:
            x, y = columna.rect.topleft
            for carta in columna.cartas:
                if carta.boca_abajo:
                    pygame.draw.rect(self.pantalla, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA))
                else:
                    dibujar_carta(carta, x, y)
                y += ESPACIO // 1  #este es el numero que indica el espaciado de las cartas
        self.dibujar_mazo()
        pygame.display.flip()

    def dibujar_mazo(self):
        # Dibujar las cartas reveladas
        x_reveladas = ESPACIO  # Posición para las cartas reveladas
        y_reveladas = ALTO - ALTO_CARTA - ESPACIO
        for i, carta in enumerate(self.cartas_reveladas):
            dibujar_carta(carta, x_reveladas + i * (ANCHO_CARTA + ESPACIO), y_reveladas)
        
        # Dibujar las cartas boca abajo del mazo
        x_volteadas = ESPACIO + 3 * (ANCHO_CARTA + ESPACIO)  # Posición para las cartas boca abajo del mazo
        for carta in self.mazo:
            dibujar_carta_boca_abajo(x_volteadas, y_reveladas)
            x_volteadas += ESPACIO // 2

    def manejar_eventos(self): #:Maneja los eventos del mouse y del teclado
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.manejar_clic_boton_down()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.manejar_clic_boton_up()
            elif event.type == pygame.MOUSEMOTION:
                self.manejar_mouse_motion()

#drag and drop // Detecta cuando se hace clic en una carta para comenzar a arrastrarla

    def manejar_clic_boton_down(self):
        pos_raton = pygame.mouse.get_pos()
        for columna in self.columnas:
            if columna.rect.collidepoint(pos_raton):
                for i, carta in enumerate(columna.cartas):
                    carta_rect = pygame.Rect(columna.rect.x, columna.rect.y + i * (ESPACIO // 4), ANCHO_CARTA, ALTO_CARTA) #espaciado 4 sirve para saber donde puedo agarrar la carta //divide la carta
                    if carta_rect.collidepoint(pos_raton) and not carta.boca_abajo:
                        self.carta_arrastrada = columna.quitar_carta()
                        self.columna_origen = columna
                        self.pos_inicial = pos_raton
                        return
        for i, carta in enumerate(self.cartas_reveladas):
            carta_rect = pygame.Rect(ESPACIO + i * (ANCHO_CARTA + ESPACIO), ALTO - ALTO_CARTA - ESPACIO, ANCHO_CARTA, ALTO_CARTA)
            if carta_rect.collidepoint(pos_raton):
                self.carta_arrastrada = self.cartas_reveladas.pop(i)
                self.pos_inicial = pos_raton
                return
        if self.mazo and pygame.Rect(ESPACIO + 3 * (ANCHO_CARTA + ESPACIO), ALTO - ALTO_CARTA - ESPACIO, ANCHO_CARTA, ALTO_CARTA).collidepoint(pos_raton):
            self.revelar_cartas_del_mazo()

#drag and drop // Coloca la carta arrastrada en una nueva ubicación cuando se suelta el botón del mouse

    def manejar_clic_boton_up(self):
        if not self.carta_arrastrada:
            return
        carta = self.carta_arrastrada
        pos_raton = pygame.mouse.get_pos()
        for columna in self.columnas:
            if columna.rect.collidepoint(pos_raton):
                columna.agregar_carta(carta)
                if self.columna_origen:
                    self.columna_origen.voltear_ultima()
                elif self.cartas_reveladas:
                    self.rellenar_cartas_reveladas()
                break
        else:
            if self.columna_origen:
                self.columna_origen.agregar_carta(carta)
            else:
                self.cartas_reveladas.append(carta)
        self.carta_arrastrada = None
        self.columna_origen = None

#Drag and drop // Permite el seguimiento del movimiento del mouse mientras se arrastra una carta

    def manejar_mouse_motion(self):
        if self.carta_arrastrada:
            pos_raton = pygame.mouse.get_pos()
            dx, dy = pos_raton[0] - self.pos_inicial[0], pos_raton[1] - self.pos_inicial[1] #//estas líneas calculan cuánto ha movido el mouse desde la última posición registrada a traves de coordenadas
            self.pos_inicial = pos_raton

#Estas funciones juntas permiten seleccionar una carta al hacer clic, moverla mientras se mantiene el botón del mouse presionado y soltarla al liberar el botón del mouse

    def revelar_cartas_del_mazo(self):
        while len(self.cartas_reveladas) < 3 and self.mazo: #el mazo revela 3 cartas
            self.cartas_reveladas.append(self.mazo.pop())
        for carta in self.cartas_reveladas:
            carta.boca_abajo = False

    def rellenar_cartas_reveladas(self):
        if len(self.cartas_reveladas) < 3 and self.mazo:
            self.cartas_reveladas.append(self.mazo.pop())
        for carta in self.cartas_reveladas:
            carta.boca_abajo = False

#Iniciar Pygame
pygame.init()

#Configuración de la pantalla
ANCHO, ALTO = 1700, 1000 
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Solitario")

#definir colores
BLANCO = (255, 255, 255)
VERDE = (0, 128, 0)
ROJO = (255, 0, 0)
NEGRO = (0, 0, 0)

#Configuración de fuentes
fuente = pygame.font.SysFont(None, 30)

#Constantes
ANCHO_CARTA = 120
ALTO_CARTA = 160
ESPACIO = 20
ESPACIO_COLUMNAS = 120

#Función para crear la baraja
def crear_baraja():
    palos = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
    valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    baraja = [Carta(palo, valor) for palo in palos for valor in valores]
    random.shuffle(baraja)
    return baraja

#Función para dibujar una carta // los diamantes y corazones lo pusimos rojo y los trebol y picas negros
def dibujar_carta(carta, x, y):
    pygame.draw.rect(PANTALLA, BLANCO, (x, y, ANCHO_CARTA, ALTO_CARTA))
    pygame.draw.rect(PANTALLA, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA), 2)
    color = ROJO if carta.palo in ['Corazones', 'Diamantes'] else NEGRO
    texto_valor = fuente.render(carta.valor, True, color)
    texto_palo = fuente.render(carta.palo, True, color)
    PANTALLA.blit(texto_valor, (x + 5, y + 5))
    PANTALLA.blit(texto_palo, (x + 5, y + 30))

#Función para dibujar una carta boca abajo
def dibujar_carta_boca_abajo(x, y):
    pygame.draw.rect(PANTALLA, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA))

#Función principal del juego
def main():
    baraja = crear_baraja()
    solitario = Solitario(ANCHO, ALTO, "Solitario")
    columnas = [Columna(ESPACIO + i * (ANCHO_CARTA + ESPACIO_COLUMNAS), ESPACIO, ANCHO_CARTA, ALTO - 2 * ESPACIO) for i in range(7)]
    for i, columna in enumerate(columnas):
        for j in range(i + 1):
            carta = baraja.pop()
            if j == i:
                carta.boca_abajo = False
            columna.agregar_carta(carta)
        solitario.agregar_columna(columna)
    solitario.agregar_mazo(baraja)
    while True:
        solitario.manejar_eventos()
        solitario.dibujar()

if __name__ == "__main__":
    main() #Configura el juego, crea las columnas, distribuye las cartas y entra en el bucle principal del juego