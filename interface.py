import pygame
import sys
import tkinter as tk
from tkinter import filedialog

# Inicialización
tk.Tk().withdraw()
pygame.init()

# Constantes
ANCHO, ALTO = 800, 600
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Programa de Encriptado")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 150, 255)
GRIS = (200, 200, 200)
HOVER = (100, 200, 255)

# Fuentes
titulo_font = pygame.font.SysFont("Forte", 60)
fuente = pygame.font.SysFont("Arial", 28)

# Estados
pantalla_actual = "inicio"
texto_input = ""
texto_output = ""
binario_cargado = ""
scroll_output = 0
scroll_binario = 0
activo = False

# Rectángulos de botones grandes
boton_inicio_encriptar = pygame.Rect(250, 200, 300, 60)
boton_inicio_desencriptar = pygame.Rect(250, 300, 300, 60)
boton_volver = pygame.Rect(20, 20, 120, 40)
boton_salir = pygame.Rect(ANCHO//2 - 100, 400, 200, 60)
input_rect = pygame.Rect(150, 140, 500, 150)
binario_rect = pygame.Rect(150, 140, 500, 150)
output_rect = pygame.Rect(150, 340, 500, 150)
boton_rect = pygame.Rect(150, 510, 130, 40)
boton_guardar_bin = pygame.Rect(300, 510, 230, 40)
boton_cargar_bin = pygame.Rect(150, 510, 130, 40)
boton_desencriptar = pygame.Rect(300, 510, 150, 40)

def dividir_texto(texto, fuente, max_ancho, max_lineas=None):
    palabras = texto.split(' ')
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        prueba = linea_actual + palabra + " "
        if fuente.size(prueba)[0] <= max_ancho:
            linea_actual = prueba
        else:
            lineas.append(linea_actual)
            linea_actual = palabra + " "
        if max_lineas and len(lineas) >= max_lineas:
            break

    if linea_actual and (not max_lineas or len(lineas) < max_lineas):
        lineas.append(linea_actual)

    return lineas

def dividir_binario(texto, fuente, max_ancho):
    chars_por_linea = max_ancho // fuente.size("1")[0]  # calcula cuántos bits caben
    return [texto[i:i+chars_por_linea] for i in range(0, len(texto), chars_por_linea)]


def dibujar_caja_input(texto, activo):
    color = GRIS if activo else AZUL
    pygame.draw.rect(VENTANA, color, input_rect, 2)
    etiqueta = fuente.render("Insertar mensaje:", True, BLANCO)
    VENTANA.blit(etiqueta, (input_rect.x, input_rect.y - 30))

    lineas = dividir_texto(texto, fuente, input_rect.width - 10)
    for i, linea in enumerate(lineas):
        linea_surface = fuente.render(linea, True, BLANCO)
        VENTANA.blit(linea_surface, (input_rect.x + 5, input_rect.y + 5 + i * (fuente.get_height() + 2)))

def dibujar_caja_output(texto):
    global scroll_output
    pygame.draw.rect(VENTANA, GRIS, output_rect, 2)
    etiqueta = fuente.render("Resultado:", True, BLANCO)
    VENTANA.blit(etiqueta, (output_rect.x, output_rect.y - 30))

    lineas = dividir_binario(texto, fuente, output_rect.width - 10)
    line_height = fuente.get_height() + 2
    max_lineas_visibles = output_rect.height // line_height

    for i, linea in enumerate(lineas[scroll_output:scroll_output + max_lineas_visibles]):
        salida_surface = fuente.render(linea, True, BLANCO)
        VENTANA.blit(salida_surface, (output_rect.x + 5, output_rect.y + 5 + i * line_height))

def dibujar_caja_binario(texto):
    global scroll_binario
    pygame.draw.rect(VENTANA, GRIS, binario_rect, 2)
    etiqueta = fuente.render("Contenido en binario:", True, BLANCO)
    VENTANA.blit(etiqueta, (binario_rect.x, binario_rect.y - 30))

    lineas = dividir_binario(texto, fuente, binario_rect.width - 10)
    max_lineas_visibles = (binario_rect.height - 10) // (fuente.get_height() + 2)

    scroll_binario = max(0, min(scroll_binario, max(0, len(lineas) - max_lineas_visibles)))

    for i, linea in enumerate(lineas[scroll_binario:scroll_binario + max_lineas_visibles]):
        bin_surface = fuente.render(linea, True, BLANCO)
        VENTANA.blit(bin_surface, (binario_rect.x + 5, binario_rect.y + 5 + i * (fuente.get_height() + 2)))

def procesar_texto(texto):
    from graphic_tree import Arbol
    global binario_codificado

    if not texto or texto.strip() == "":
        return "No hay texto válido para codificar."
    
    binario_codificado, raiz, archivo_generado = Arbol.text_to_bin(texto)
    return binario_codificado

def guardar_bin():
    from tkinter import messagebox
    from graphic_tree import Arbol
    global binario_codificado, texto_input

    if not binario_codificado:
        messagebox.showerror("Error", "No hay datos binarios para guardar.")
        return

    ruta_destino = filedialog.asksaveasfilename(
        defaultextension=".bin",
        filetypes=[("Archivos binarios", "*.bin")],
        title="Guardar archivo binario como..."
    )

    if not ruta_destino:
        return

    try:
        # Volver a codificar desde cero, usando el generador de archivo con encabezado
        frecuencia = Arbol.codificador_grafico(texto_input)
        raiz = Arbol.estructura_huffman(frecuencia)
        codigo = Arbol.guardar_en_binario(texto_input, raiz)
        Arbol.crear_archivo_bin(ruta_destino, frecuencia, codigo)

        print(f"Archivo guardado correctamente: {ruta_destino}")
    except Exception as e:
        messagebox.showerror("Error al guardar", str(e))

def cargar_binario():#Se encarga de cargar un archivo x en formato .bin y almacenar la ruta actual por si se ocupa para otras acciones
    global binario_cargado, ruta_binario_actual
    try:
        ruta = filedialog.askopenfilename(filetypes=[("Archivos binarios", "*.bin")])
        if ruta:
            with open(ruta, "rb") as archivo:
                contenido = archivo.read()
                binario_cargado = ''.join(format(byte, '08b') for byte in contenido)
                ruta_binario_actual = ruta  
    except Exception as e:
        binario_cargado = f"Error al leer archivo: {e}"

def desencripatar(ruta_binario):
    from extract import analizar_binario
    from graphic_tree import Arbol
    global texto_output, binario_cargado

    if not ruta_binario:
        texto_output = "No se ha cargado un archivo .bin"
        return

    try:
        letras, binario = analizar_binario(ruta_binario)
        texto_output = Arbol.bin_to_text(letras, binario)
        binario_cargado = binario
    except Exception as e:
        texto_output = f"Error al desencriptar: {e}"

# --- DIBUJOS POR PANTALLA --- #
def dibujar_inicio():
    VENTANA.fill(NEGRO)
    titulo = titulo_font.render("Encriptador", True, BLANCO)
    VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 80))

    mouse = pygame.mouse.get_pos()
    for rect, texto in [(boton_inicio_encriptar, "Encriptar"), (boton_inicio_desencriptar, "Desencriptar")]:
        color = HOVER if rect.collidepoint(mouse) else AZUL
        pygame.draw.rect(VENTANA, color, rect)
        txt_surface = fuente.render(texto, True, NEGRO)
        VENTANA.blit(txt_surface, (rect.x + (rect.width - txt_surface.get_width()) // 2, rect.y + 10))
        
    color_salir = HOVER if boton_salir.collidepoint(mouse) else AZUL
    pygame.draw.rect(VENTANA, color_salir, boton_salir)
    VENTANA.blit(fuente.render("Salir", True, NEGRO), (boton_salir.x + 70, boton_salir.y + 15))

def dibujar_encriptar():
    VENTANA.fill(NEGRO)
    titulo = titulo_font.render("Encriptar", True, BLANCO)
    VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 20))
    pygame.draw.rect(VENTANA, AZUL, boton_volver)
    VENTANA.blit(fuente.render("Volver", True, NEGRO), (boton_volver.x + 10, boton_volver.y + 5))
    dibujar_caja_input(texto_input, activo)
    dibujar_caja_output(texto_output)

    mouse = pygame.mouse.get_pos()
    color_procesar = HOVER if boton_rect.collidepoint(mouse) else AZUL
    color_guardar_bin = HOVER if boton_guardar_bin.collidepoint(mouse) else AZUL

    pygame.draw.rect(VENTANA, color_procesar, boton_rect)
    pygame.draw.rect(VENTANA, color_guardar_bin, boton_guardar_bin)

    VENTANA.blit(fuente.render("Encriptar", True, NEGRO), (boton_rect.x + 10, boton_rect.y + 5))
    VENTANA.blit(fuente.render("Guardar archivo .bin", True, NEGRO), (boton_guardar_bin.x + 5, boton_guardar_bin.y + 5))

    # Aquí dibujarías input_rect, output_rect, botones encriptar, guardar...
    # Por ahora lo dejamos así para avanzar en navegación

def dibujar_desencriptar():
    VENTANA.fill(NEGRO)
    titulo = titulo_font.render("Desencriptar", True, BLANCO)
    VENTANA.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 20))
    pygame.draw.rect(VENTANA, AZUL, boton_volver)
    VENTANA.blit(fuente.render("Volver", True, NEGRO), (boton_volver.x + 10, boton_volver.y + 5))
    dibujar_caja_binario(binario_cargado)
    dibujar_caja_output(texto_output)

    mouse = pygame.mouse.get_pos()

    color_cargar = HOVER if boton_cargar_bin.collidepoint(mouse) else AZUL
    color_decencriptar = HOVER if boton_desencriptar.collidepoint(mouse) else AZUL

    pygame.draw.rect(VENTANA, color_cargar, boton_cargar_bin)
    pygame.draw.rect(VENTANA, color_decencriptar, boton_desencriptar)

    VENTANA.blit(fuente.render("Cargar .bin", True, NEGRO), (boton_cargar_bin.x + 5, boton_cargar_bin.y + 5))
    VENTANA.blit(fuente.render("Desencriptar", True, NEGRO), (boton_desencriptar.x + 5, boton_desencriptar.y + 5))

    # Aquí irán cargar binario, mostrar resultado, etc.

# --- EVENTOS --- #
def manejar_eventos():
    global texto_input, texto_output, activo, pantalla_actual

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if pantalla_actual == "inicio":
                if boton_inicio_encriptar.collidepoint(evento.pos):
                    pantalla_actual = "encriptar"
                elif boton_inicio_desencriptar.collidepoint(evento.pos):
                    pantalla_actual = "desencriptar"
                elif boton_salir.collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()

            elif pantalla_actual == "encriptar":
                if input_rect.collidepoint(evento.pos):
                    activo = True
                else:
                    activo = False

                if boton_rect.collidepoint(evento.pos):
                    binario_codificado = procesar_texto(texto_input)
                    texto_output = binario_codificado
                elif boton_guardar_bin.collidepoint(evento.pos):
                    guardar_bin()
                
                elif boton_volver.collidepoint(evento.pos):
                    pantalla_actual = "inicio"
                    texto_input = ""
                    texto_output = ""

            elif pantalla_actual == "desencriptar":
                if boton_cargar_bin.collidepoint(evento.pos):
                    cargar_binario()
                elif boton_desencriptar.collidepoint(evento.pos):
                    desencripatar(ruta_binario_actual)

                if boton_volver.collidepoint(evento.pos):
                    pantalla_actual = "inicio"
                    texto_output = ""
                    binario_cargado = ""
        
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 4:  # Scroll arriba
                if pantalla_actual == "encriptar":
                    scroll_output = max(0, scroll_output - 1)
                elif pantalla_actual == "desencriptar":
                    scroll_binario = max(0, scroll_binario - 1)
            elif evento.button == 5:  # Scroll abajo
                if pantalla_actual == "encriptar":
                    scroll_output += 1
                elif pantalla_actual == "desencriptar":
                    scroll_binario += 1

        elif evento.type == pygame.KEYDOWN and pantalla_actual == "encriptar" and activo:
            if evento.key == pygame.K_RETURN:
                texto_output = procesar_texto(texto_input)
            elif evento.key == pygame.K_BACKSPACE:
                texto_input = texto_input[:-1]
            else:
                texto_input += evento.unicode

# --- CICLO PRINCIPAL --- #
def main():
    clock = pygame.time.Clock()
    while True:
        manejar_eventos()

        if pantalla_actual == "inicio":
            dibujar_inicio()
        elif pantalla_actual == "encriptar":
            dibujar_encriptar()
        elif pantalla_actual == "desencriptar":
            dibujar_desencriptar()

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
