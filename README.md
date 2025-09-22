# Cifrado por Permutación de Grupos

## Descripción

Esta herramienta implementa un sistema de cifrado basado en permutación de grupos, donde el texto se divide en bloques de tamaño fijo y las posiciones de los caracteres dentro de cada bloque se reorganizan según una permutación específica.

## Características

- **Interfaz gráfica intuitiva** desarrollada con Tkinter
- **Normalización automática** del texto (convierte a mayúsculas y elimina caracteres especiales)
- **Relleno automático** con 'X' para completar el último bloque
- **Carga de archivos** de texto desde el sistema
- **Guardado automático** del resultado en `cifrado.txt`

## Requisitos del Sistema

- Python 3.x
- Tkinter (incluido en la mayoría de instalaciones de Python)

## Instalación y Ejecución

1. Asegúrate de tener Python instalado en tu sistema
2. Descarga el archivo `permutacion.py`
3. Ejecuta el programa:
   ```bash
   python permutacion.py
   ```

## Uso de la Interfaz

### 1. Entrada de Texto

**Opción A: Escritura Manual**
- Escribe o pega el texto que deseas cifrar en el área de texto superior
- El texto puede contener cualquier carácter (espacios, números, signos de puntuación)

**Opción B: Carga de Archivo**
- Haz clic en "Cargar archivo .txt"
- Selecciona un archivo de texto desde tu sistema
- El contenido se cargará automáticamente en el área de texto

### 2. Configuración del Cifrado

**Tamaño del Grupo:**
- Introduce un número entero que representa el tamaño de cada bloque
- Ejemplo: Si introduces `4`, el texto se dividirá en bloques de 4 caracteres

**Permutación:**
- Introduce los números de la permutación separados por espacios
- Debe ser una reordenación completa de los números del 1 al tamaño del grupo
- Ejemplo para grupo de tamaño 4: `3 1 4 2`

### 3. Proceso de Cifrado

1. Haz clic en el botón "Cifrar"
2. El programa validará que:
   - El tamaño del grupo sea un número válido
   - La permutación contenga todos los números del 1 al tamaño del grupo
3. Si todo es correcto, el texto cifrado aparecerá en el área inferior

### 4. Guardado del Resultado

- Haz clic en "Guardar en archivo .txt"
- El texto cifrado se guardará automáticamente como `cifrado.txt` en la misma carpeta del programa

## Ejemplo de Uso

### Entrada:
- **Texto:** "Hola mundo secreto"
- **Tamaño del grupo:** 4
- **Permutación:** 3 1 4 2

### Proceso:
1. **Normalización:** "HOLAMUNDOSECRETO"
2. **Relleno:** "HOLAMUNDOSECRETO" (se añade X para completar el último bloque)
3. **División en bloques:** ["HOLA", "MUND", "OSEC", "RETO"]
4. **Aplicación de permutación (3 1 4 2):**
   - "HOLA" → "LAOH" (posición 3→1, 1→2, 4→3, 2→4)
   - "MUND" → "NDUM"
   - "OSEC" → "SCOE"
   - "RETO" → "TERO"

### Resultado:
```
LAOH NDUM SCOE TERO
```

## Algoritmo de Cifrado

### Normalización
```python
def normalizar_texto(texto, grupo):
    texto = texto.upper()                    # Convierte a mayúsculas
    texto = re.sub(r'[^A-Z]', '', texto)    # Elimina caracteres no alfabéticos
    
    while len(texto) % grupo != 0:           # Rellena con 'X' hasta completar bloques
        texto += 'X'
    
    return texto
```

### Cifrado por Permutación
```python
def cifrar(texto, grupo, permutacion):
    bloques = []
    for i in range(0, len(texto), grupo):
        bloque = texto[i:i+grupo]
        # Aplica la permutación: nuevo[j] = original[permutacion[j]-1]
        nuevo = "".join(bloque[permutacion[j]-1] for j in range(grupo))
        bloques.append(nuevo)
    return " ".join(bloques)
```

## Validaciones del Sistema

El programa incluye las siguientes validaciones:

1. **Tamaño del grupo:** Debe ser un número entero válido
2. **Formato de permutación:** Solo números separados por espacios
3. **Completitud de permutación:** Debe contener todos los números del 1 al tamaño del grupo
4. **Existencia de texto:** Verifica que hay contenido para cifrar antes de guardar

## Archivos Generados

- **`cifrado.txt`:** Contiene el resultado del último cifrado realizado
- Se sobrescribe automáticamente en cada nueva operación de cifrado

## Limitaciones

- Solo procesa caracteres alfabéticos (A-Z)
- El relleno con 'X' puede afectar la legibilidad del texto descifrado
- No incluye funcionalidad de descifrado en la interfaz actual

## Seguridad

Este es un cifrado clásico con propósitos educativos. Para aplicaciones reales de seguridad, se recomienda usar algoritmos criptográficos modernos y probados.

## Solución de Problemas

**Error: "El tamaño de grupo debe ser un número entero"**
- Verifica que hayas introducido solo números en el campo "Tamaño del grupo"

**Error: "La permutación debe contener solo números separados por espacio"**
- Asegúrate de usar solo números y espacios en la permutación
- Ejemplo correcto: `3 1 4 2`

**Error: "La permutación debe ser una reordenación de 1 a N"**
- Verifica que tu permutación contenga todos los números del 1 al tamaño del grupo
- No debe haber números repetidos ni faltantes

**Error: "No hay texto cifrado para guardar"**
- Primero debes cifrar un texto antes de intentar guardarlo