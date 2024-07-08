import pygame
import random
import sys
import time
import json

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

    def quitar_cartas(self, indice):
        if 0 <= indice < len(self.cartas):
            cartas_movidas = self.cartas[indice:]
            self.cartas = self.cartas[:indice]
            return cartas_movidas
        return []

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
        self.cartas_arrastradas = []
        self.pos_inicial = None
        self.columna_origen = None
        self.puntaje = 0
        self.inicio_tiempo = time.time()
        self.boton_reinicio = pygame.Rect(ancho - 150, 80, 100, 30)
        self.boton_revelar_mazo = pygame.Rect(ancho - 150, 120, 100, 30)
        self.datos_guardados = "solitario_datos.json"

        # Intentar cargar el estado guardado
        self.cargar_estado()

    def agregar_columna(self, columna):
        self.columnas.append(columna)

    def agregar_mazo(self, mazo):
        self.mazo = mazo

    def guardar_estado(self):
        estado = {
            "puntaje": self.puntaje,
            "inicio_tiempo": self.inicio_tiempo,
        }
        with open(self.datos_guardados, "w") as archivo:
            json.dump(estado, archivo)

    def cargar_estado(self):
        try:
            with open(self.datos_guardados, "r") as archivo:
                estado = json.load(archivo)
                self.puntaje = estado.get("puntaje", 0)
                self.inicio_tiempo = estado.get("inicio_tiempo", time.time())
        except FileNotFoundError:
            pass

    def dibujar(self):
        self.pantalla.fill(VERDE)
        for columna in self.columnas:
            x, y = columna.rect.topleft
            for carta in columna.cartas:
                if carta.boca_abajo:
                    pygame.draw.rect(self.pantalla, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA))
                else:
                    dibujar_carta(carta, x, y)
                y += ESPACIO
        self.dibujar_mazo()
        self.dibujar_puntaje_y_tiempo()
        self.dibujar_botones()
        pygame.display.flip()

    def dibujar_mazo(self):
        x_reveladas = ESPACIO
        y_reveladas = ALTO - ALTO_CARTA - ESPACIO
        for i, carta in enumerate(self.cartas_reveladas):
            dibujar_carta(carta, x_reveladas + i * (ANCHO_CARTA + ESPACIO), y_reveladas)

        x_volteadas = ESPACIO + 3 * (ANCHO_CARTA + ESPACIO)
        for carta in self.mazo:
            dibujar_carta_boca_abajo(x_volteadas, y_reveladas)
            x_volteadas += ESPACIO // 2

    def dibujar_puntaje_y_tiempo(self):
        tiempo_transcurrido = int(time.time() - self.inicio_tiempo)
        minutos = tiempo_transcurrido // 60
        segundos = tiempo_transcurrido % 60
        tiempo_texto = fuente.render(f"Tiempo: {minutos:02}:{segundos:02}", True, BLANCO)
        puntaje_texto = fuente.render(f"Puntaje: {self.puntaje}", True, BLANCO)
        self.pantalla.blit(tiempo_texto, (ANCHO - 150, 10))
        self.pantalla.blit(puntaje_texto, (ANCHO - 150, 40))

    def dibujar_botones(self):
        pygame.draw.rect(self.pantalla, ROJO, self.boton_reinicio)
        texto_reinicio = fuente.render("Reiniciar", True, BLANCO)
        self.pantalla.blit(texto_reinicio, (self.boton_reinicio.x + 10, self.boton_reinicio.y + 5))

        pygame.draw.rect(self.pantalla, ROJO, self.boton_revelar_mazo)
        texto_revelar = fuente.render("Revelar 3", True, BLANCO)
        self.pantalla.blit(texto_revelar, (self.boton_revelar_mazo.x + 10, self.boton_revelar_mazo.y + 5))

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.guardar_estado()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.manejar_clic_boton_down()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.manejar_clic_boton_up()
            elif event.type == pygame.MOUSEMOTION:
                self.manejar_mouse_motion()

    def manejar_clic_boton_down(self):
        pos_raton = pygame.mouse.get_pos()
        if self.boton_reinicio.collidepoint(pos_raton):
            self.reiniciar_juego()
            return
        elif self.boton_revelar_mazo.collidepoint(pos_raton):
            self.revelar_nuevas_cartas_del_mazo()
            return
        for columna in self.columnas:
            if columna.rect.collidepoint(pos_raton):
                for i, carta in enumerate(columna.cartas):
                    carta_rect = pygame.Rect(columna.rect.x, columna.rect.y + i * ESPACIO, ANCHO_CARTA, ALTO_CARTA)
                    if carta_rect.collidepoint(pos_raton) and not carta.boca_abajo:
                        self.cartas_arrastradas = columna.quitar_cartas(i)
                        self.columna_origen = columna
                        self.pos_inicial = pos_raton
                        return
        for i, carta in enumerate(self.cartas_reveladas):
            carta_rect = pygame.Rect(ESPACIO + i * (ANCHO_CARTA + ESPACIO), ALTO - ALTO_CARTA - ESPACIO, ANCHO_CARTA, ALTO_CARTA)
            if carta_rect.collidepoint(pos_raton):
                self.cartas_arrastradas = [self.cartas_reveladas.pop(i)]
                self.pos_inicial = pos_raton
                return
        if self.mazo and pygame.Rect(ESPACIO + 3 * (ANCHO_CARTA + ESPACIO), ALTO - ALTO_CARTA - ESPACIO, ANCHO_CARTA, ALTO_CARTA).collidepoint(pos_raton):
            self.revelar_cartas_del_mazo()

    def manejar_clic_boton_up(self):
        if not self.cartas_arrastradas:
            return
        cartas = self.cartas_arrastradas
        pos_raton = pygame.mouse.get_pos()
        for columna in self.columnas:
            if columna.rect.collidepoint(pos_raton):
                if self.puede_mover_cartas(cartas, columna):
                    columna.cartas.extend(cartas)
                    self.puntaje += 50 * len(cartas)
                    if self.columna_origen:
                        self.columna_origen.voltear_ultima()
                    elif self.cartas_reveladas:
                        self.rellenar_cartas_reveladas()
                    break
        else:
            if self.columna_origen:
                self.columna_origen.cartas.extend(cartas)
            else:
                self.cartas_reveladas.extend(cartas)
        self.cartas_arrastradas = []
        self.columna_origen = None

    def manejar_mouse_motion(self):
        if self.cartas_arrastradas:
            pos_raton = pygame.mouse.get_pos()
            dx, dy = pos_raton[0] - self.pos_inicial[0], pos_raton[1] - self.pos_inicial[1]
            self.pos_inicial = pos_raton

    def puede_mover_cartas(self, cartas, columna):
        if not columna.cartas:
            return True
        carta_destino = columna.cartas[-1]
        if carta_destino.boca_abajo:
            return False
        color_carta = 'rojo' if cartas[0].palo in ['Corazones', 'Diamantes'] else 'negro'
        color_destino = 'rojo' if carta_destino.palo in ['Corazones', 'Diamantes'] else 'negro'
        if color_carta == color_destino:
            return False
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return valores.index(cartas[0].valor) + 1 == valores.index(carta_destino.valor)

    def revelar_cartas_del_mazo(self):
        if not self.mazo:
            return
        self.cartas_reveladas.extend(self.mazo[-3:])
        self.mazo = self.mazo[:-3]
        for carta in self.cartas_reveladas[-3:]:
            carta.boca_abajo = False

    def revelar_nuevas_cartas_del_mazo(self):
        if not self.mazo:
            return
        self.mazo = self.cartas_reveladas + self.mazo
        self.cartas_reveladas = []
        self.revelar_cartas_del_mazo()

    def reiniciar_juego(self):
        baraja = crear_baraja()
        self.columnas = [Columna(ESPACIO + i * (ANCHO_CARTA + ESPACIO_COLUMNAS), ESPACIO, ANCHO_CARTA, ALTO - 2 * ESPACIO) for i in range(7)]
        for i, columna in enumerate(self.columnas):
            for j in range(i + 1):
                carta = baraja.pop()
                if j == i:
                    carta.boca_abajo = False
                columna.agregar_carta(carta)
        self.agregar_mazo(baraja)
        self.cartas_reveladas = []
        self.cartas_arrastradas = []
        self.pos_inicial = None
        self.columna_origen = None
        self.puntaje = 0
        self.inicio_tiempo = time.time()
        self.guardar_estado()

    def rellenar_cartas_reveladas(self):
        # Define lo que debe hacer este método. Por ejemplo, si quieres reponer el mazo con cartas reveladas.
        if not self.mazo:
            self.mazo = self.cartas_reveladas
            self.cartas_reveladas = []
            for carta in self.mazo:
                carta.boca_abajo = True

# Iniciar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO, ALTO = 1400, 800 
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Solitario")

# Definir colores
BLANCO = (255, 255, 255)
VERDE = (0, 128, 0)
ROJO = (255, 0, 0)
NEGRO = (0, 0, 0)

# Configuración de fuentes
fuente = pygame.font.SysFont(None, 30)

# Constantes
ANCHO_CARTA = 120
ALTO_CARTA = 160
ESPACIO = 40
ESPACIO_COLUMNAS = 120

# Función para crear la baraja
def crear_baraja():
    palos = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
    valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    baraja = [Carta(palo, valor) for palo in palos for valor in valores]
    random.shuffle(baraja)
    return baraja

# Función para dibujar una carta
def dibujar_carta(carta, x, y):
    pygame.draw.rect(PANTALLA, BLANCO, (x, y, ANCHO_CARTA, ALTO_CARTA))
    pygame.draw.rect(PANTALLA, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA), 2)
    color = ROJO if carta.palo in ['Corazones', 'Diamantes'] else NEGRO
    texto_valor = fuente.render(carta.valor, True, color)
    texto_palo = fuente.render(carta.palo, True, color)
    PANTALLA.blit(texto_valor, (x + 5, y + 5))
    PANTALLA.blit(texto_palo, (x + 5, y + 30))

# Función para dibujar una carta boca abajo
def dibujar_carta_boca_abajo(x, y):
    pygame.draw.rect(PANTALLA, NEGRO, (x, y, ANCHO_CARTA, ALTO_CARTA))

# Función principal del juego
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
    main()  # Configura el juego, crea las columnas, distribuye las cartas y entra en el bucle principal del juego

