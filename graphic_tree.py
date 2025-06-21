import pygame
from collections import Counter
from camara import Camara
import time

class Arbol:
    def __init__(self, valor):
        pygame.init()
        self.valor = valor
        self.hijo_izquierda: Arbol = None
        self.hijo_derecha: Arbol = None

    def insertar(self, elemento):
        valor = elemento[1]
        if valor >= self.valor[1]:
            if self.hijo_izquierda is None:
                self.hijo_izquierda = Arbol(elemento)
            else:
                self.hijo_izquierda.insertar(elemento)
        else:
            if self.hijo_derecha is None:
                self.hijo_derecha = Arbol(elemento)
            else:
                self.hijo_derecha.insertar(elemento)

    @property
    def altura(self):
        if self.hoja:
            return 1
        altura_hijo_iz = self.hijo_izquierda.altura if self.hijo_izquierda else 0
        altura_hijo_der = self.hijo_derecha.altura if self.hijo_derecha else 0
        return max(altura_hijo_iz, altura_hijo_der) + 1

    @property
    def hoja(self):
        return self.hijo_derecha is None and self.hijo_izquierda is None

    def imprimir_nodo(self, raiz, valor, x, y, color=(0, 0, 255)):
        pygame.draw.circle(raiz.VENTANA, color, (x, y), 20)
        texto = f"{valor[0]} = {valor[1]}" if isinstance(valor[0], str) and len(valor[0]) == 1 else f"{valor[1]}"
        texto_render = raiz.fuente.render(texto, True, (255, 255, 255))
        texto_rect = texto_render.get_rect(center=(x, y))
        raiz.VENTANA.blit(texto_render, texto_rect)

    def mostrar_nodos_adaptativo(self, raiz, x, y, nivel, espacio, camara, animaciones=None, letra_actual=None, decodificado=""):
        x_tr, y_tr = camara.aplicar_transformacion(x, y)
        color = (0, 0, 255)
        if animaciones:
            for nodo, es_correcto in animaciones[:1]:
                if nodo is self:
                    color = (255, 0, 0) if not es_correcto else (0, 255, 0)
                    if es_correcto:
                        animaciones.pop(0)
                        break
        if self.hijo_izquierda:
            nuevo_x = x - espacio; nuevo_y = y + 60
            nuevo_x_tr, nuevo_y_tr = camara.aplicar_transformacion(nuevo_x, nuevo_y)
            pygame.draw.line(raiz.VENTANA, (0, 0, 0), (x_tr, y_tr), (nuevo_x_tr, nuevo_y_tr), 4)
            self.hijo_izquierda.mostrar_nodos_adaptativo(raiz, nuevo_x, nuevo_y, nivel + 1, espacio // 2, camara, animaciones, letra_actual, decodificado)
        if self.hijo_derecha:
            nuevo_x = x + espacio; nuevo_y = y + 60
            nuevo_x_tr, nuevo_y_tr = camara.aplicar_transformacion(nuevo_x, nuevo_y)
            pygame.draw.line(raiz.VENTANA, (0, 0, 0), (x_tr, y_tr), (nuevo_x_tr, nuevo_y_tr), 4)
            self.hijo_derecha.mostrar_nodos_adaptativo(raiz, nuevo_x, nuevo_y, nivel + 1, espacio // 2, camara, animaciones, letra_actual, decodificado)
        self.imprimir_nodo(raiz, self.valor, x_tr, y_tr, color)
        
    @staticmethod
    def obtener_animacion_para_letra(nodo, letra):
        def buscar_codigo(nodo, letra, camino=None, anim=None):
            if camino is None: camino = ""
            if anim is None: anim = []
            if nodo is None:
                return None
            anim.append((nodo, False))
            if nodo.hoja and nodo.valor[0] == letra:
                anim[-1] = (nodo, True)
                return nodo.valor[2], anim
            izquierda = buscar_codigo(nodo.hijo_izquierda, letra, camino + "0", anim[:])
            if izquierda:
                return izquierda
            derecha = buscar_codigo(nodo.hijo_derecha, letra, camino + "1", anim[:])
            if derecha:
                return derecha
            return None
        return buscar_codigo(nodo, letra)

    def mostrar_arbol_grafico(self):
        ancho = 1000; alto = 600
        self.VENTANA = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption("Despliegue de árbol")
        self.fuente = pygame.font.SysFont("Arial", 18)
        camara = Camara()
        corriendo = True
        espacio_inicial = 300
        velocidad = 1.0
        en_pausa = False

        animaciones = getattr(self, "animaciones", [])
        decodificado_total = getattr(self, "decodificado", "")
        decodificado_parcial = ""
        letras_mostradas = 0
        nodo_mostrado = None  

        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        en_pausa = not en_pausa
                    elif evento.key == pygame.K_UP:
                        velocidad = max(0.1, velocidad - 0.1)
                    elif evento.key == pygame.K_DOWN:
                        velocidad += 0.1
                camara.manejar_eventos(evento)
            if not en_pausa and animaciones:
                time.sleep(velocidad)
                nodo_mostrado, es_correcto = animaciones.pop(0)
                
            self.VENTANA.fill((255, 255, 255))
            self.mostrar_nodos_adaptativo(self, 0, 0, 1, espacio_inicial, camara, [(nodo_mostrado, True)] if nodo_mostrado else [], None, decodificado_parcial)
            if nodo_mostrado and nodo_mostrado.hoja:
                letras_mostradas += 1
                decodificado_parcial = decodificado_total[:letras_mostradas]
                nodo_mostrado = None  
                
            texto_render = self.fuente.render(f"Decodificado: {decodificado_parcial}", True, (0, 0, 0))
            self.VENTANA.blit(texto_render, (10, alto - 30))
            pygame.display.flip()
            if not animaciones and not en_pausa:
                en_pausa = True
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return

    @staticmethod
    def estructura_huffman(frecuencias):
        nodos = [Arbol((letra, freq, codigo)) for letra, freq, codigo in frecuencias]
        nodos.sort(key=lambda nodo: nodo.valor[1])
        lista = []
        while len(nodos) > 0:
            if len(lista) < 1:
                derecho = nodos.pop(0)
                izquierdo = nodos.pop(0)
            else:
                derecho = lista.pop(0)
                izquierdo = nodos.pop(0)

            nuevo_valor = (izquierdo.valor[0] + derecho.valor[0], izquierdo.valor[1] + derecho.valor[1])
            nuevo_nodo = Arbol(nuevo_valor)
            nuevo_nodo.hijo_izquierda = izquierdo
            nuevo_nodo.hijo_derecha = derecho
            lista.append(nuevo_nodo)
        return lista[0]
    
    @staticmethod
    def codificador_grafico(texto):
        def tipo_prioridad(char):
            if char.isalpha():
                if char in 'ÁÉÍÓÚÜ': return (0, ord(char))
                if char.isupper(): return (1, ord(char))
                if char.lower() in 'áéíóúü': return (2, ord(char))
                return (3, ord(char))
            if char == ' ': return (4, ord(char))
            return (5, ord(char))
        contador = Counter(texto)
        lista = sorted(contador.items(), key=lambda x: (x[1], tipo_prioridad(x[0])))
        resultado = []
        longitud = len(lista)
        for i, (letra, freq) in enumerate(lista):
            codigo = '1' * (longitud - 1 - i) + '0' if i != 0 else '1' * (longitud - 1)
            resultado.append((letra, freq, codigo))
        return resultado
    
    @staticmethod
    def codificador_grafico_bin(lista_frecuencias):
        def tipo_prioridad(char):
            if char.isalpha():
                if char in 'ÁÉÍÓÚÜ': return (0, ord(char))
                if char.isupper(): return (1, ord(char))
                if char.lower() in 'áéíóúü': return (2, ord(char))
                return (3, ord(char))
            if char == ' ': return (4, ord(char))
            return (5, ord(char))
        lista_ordenada = sorted(lista_frecuencias, key=lambda x: (x[1], tipo_prioridad(x[0])))
        resultado = []
        longitud = len(lista_ordenada)
        for i, (letra, freq) in enumerate(lista_ordenada):
            codigo = '1' * (longitud - 1 - i) + '0' if i != 0 else '1' * (longitud - 1)
            resultado.append((letra, freq, codigo))
        return resultado

    @staticmethod
    def buscar_letra(nodo, codigo):
        if nodo is None:
            return None
        if len(codigo) == 0:
            return nodo.valor[0] if nodo.hoja else None
        bit, resto_codigo = codigo[0], codigo[1:]
        siguiente = nodo.hijo_izquierda if bit == '0' else nodo.hijo_derecha
        return Arbol.buscar_letra(siguiente, resto_codigo)
    
    @staticmethod
    def guardar_en_binario(texto_encryp, raiz):
        def buscar_codigo(nodo, letra, camino=None, anim=None):
            if camino is None: camino = ""
            if anim is None: anim = []
            if nodo is None:
                return None
            anim.append((nodo, False))
            if nodo.hoja and nodo.valor[0] == letra:
                anim[-1] = (nodo, True)
                return nodo.valor[2], anim
            izquierda = buscar_codigo(nodo.hijo_izquierda, letra, camino + "0", anim[:])
            if izquierda:
                return izquierda
            derecha = buscar_codigo(nodo.hijo_derecha, letra, camino + "1", anim[:])
            if derecha:
                return derecha
            return None
        binario_total = ""
        animaciones_globales = []
        letras_decodificadas = ""
        for letra in texto_encryp:
            resultado = buscar_codigo(raiz, letra)
            if resultado:
                codigo, anim = resultado
                binario_total += codigo
                animaciones_globales.extend(anim)
                letras_decodificadas += letra

        padding = (8 - len(binario_total) % 8) % 8
        binario_total = "0" * padding + binario_total
        bytes_lista = [binario_total[i:i + 8] for i in range(0, len(binario_total), 8)]
        raiz.animaciones = animaciones_globales
        raiz.decodificado = letras_decodificadas
        return (padding, bytes_lista)

    @staticmethod
    def crear_archivo_bin(nombre_archivo, frecuencia, codigo):
        padding, codigos_binarios = codigo
        contenido = bytearray()
        contenido.append((padding >> 8) & 0xFF)
        contenido.append(padding & 0xFF)
        for letra, repeticiones, _ in frecuencia:
            ascii_val = ord(letra)
            rep_hi, rep_lo = (repeticiones >> 8) & 0xFF, repeticiones & 0xFF
            contenido.extend([ascii_val, rep_hi, rep_lo])
        for byte_str in codigos_binarios:
            contenido.append(int(byte_str, 2))
        with open(nombre_archivo, 'wb') as f:
            f.write(contenido)

    @staticmethod
    def decodificar(codigo, raiz):
        decodificacion, acumulador = "", ""
        animaciones_globales = []
        for bit in codigo:
            acumulador += bit
            letra = Arbol.buscar_letra(raiz, acumulador)
            if letra is not None:
                resultado = Arbol.obtener_animacion_para_letra(raiz, letra)
                if resultado:
                    _, anim = resultado
                    animaciones_globales.extend(anim)
                decodificacion += letra
                acumulador = ""
        if acumulador != "":
            print(f"Advertencia: código incompleto o inválido restante: '{acumulador}'")
        raiz.animaciones = animaciones_globales
        raiz.decodificado = decodificacion
        return decodificacion

    @staticmethod
    def text_to_bin(texto, archivo_salida="salida.bin"):
        if not texto:
            raise ValueError("El texto de entrada no puede estar vacío.")
        frecuencia = Arbol.codificador_grafico(texto)
        raiz = Arbol.estructura_huffman(frecuencia)
        codigo = Arbol.guardar_en_binario(texto, raiz)
        Arbol.crear_archivo_bin(archivo_salida, frecuencia, codigo)
        return frecuencia

    @staticmethod
    def bin_to_text(lista, codificacion):
        if not lista:
            raise ValueError("La lista de entrada no puede estar vacía.")
        frecuencia = Arbol.codificador_grafico_bin(lista)
        raiz = Arbol.estructura_huffman(frecuencia)
        texto_plano = Arbol.decodificar(codificacion, raiz)
        raiz.mostrar_arbol_grafico()
        return texto_plano

if __name__ == "__main__":
    texto = 'hola alas'
    frecuencia = Arbol.text_to_bin(texto, 'Prueba2')
    print(f'Frecuencia codificar: {frecuencia}')
    lista = [('a', 3), ('l', 2), ('h', 1), ('s', 1), ('o', 1), (' ', 1) ]
    print(Arbol.bin_to_text(lista, '111111111010011001001110'))