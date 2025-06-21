def analizar_binario(ruta_archivo):
    datos_letras = []
    mensaje_binario = ""
    
    with open(ruta_archivo, 'rb') as archivo:
        contenido = archivo.read()

    if len(contenido) < 2: #Leer los primeros dos bytes como número entero sin signo (cantidad de ceros agregados al inicio)
        raise ValueError("El archivo no contiene los primeros dos bytes requeridos.")
    
    n_zeros = int.from_bytes(contenido[:2], byteorder='big')  # puede ser 'little' si se especifica
    i = 2  # índice actual

    while i + 3 <= len(contenido): #Leer las parejas de ASCII + repeticiones
        byte_actual = contenido[i]

        if 32 <= byte_actual <= 126:# Verificar si el byte actual es un carácter ASCII imprimible (ej. entre 32 y 126)
            letra = chr(byte_actual)
            repeticiones = int.from_bytes(contenido[i+1:i+3], byteorder='big')
            datos_letras.append((letra, repeticiones))
            i += 3
        else:
            # No es un carácter ASCII válido, entonces el resto es binario puro
            break

    binario_crudo = contenido[i:]#El resto es el mensaje binario codificado

    bin_str = ''.join(f'{byte:08b}' for byte in binario_crudo)#Convertir los bytes restantes a una cadena binaria

    if n_zeros > len(bin_str):# Eliminar los ceros añadidos al inicio
        raise ValueError("La cantidad de ceros a eliminar excede la longitud del mensaje binario.")
    
    binario_limpio = bin_str[n_zeros:]

    return datos_letras, binario_limpio