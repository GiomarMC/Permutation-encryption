import tkinter as tk
from tkinter import messagebox, filedialog
import re
import os

def normalizar_texto(texto, grupo):
    texto = texto.upper()
    texto = re.sub(r'[^A-Z]', '', texto)

    while len(texto) % grupo != 0:
        texto += 'X'

    return texto

def cifrar(texto, grupo, permutacion):
    bloques = []
    for i in range(0, len(texto), grupo):
        bloque = texto[i:i+grupo]
        nuevo = "".join(bloque[permutacion[j]-1] for j in range(grupo))
        bloques.append(nuevo)
    return "".join(bloques)

def ejecutar_cifrado():
    texto = entrada_texto.get("1.0", tk.END).strip()

    try:
        grupo = int(entrada_grupo.get())
    except ValueError:
        messagebox.showerror("Error", "El tamaño de grupo debe ser un número entero.")
        return

    try:
        perm = list(map(int, entrada_permutacion.get().split()))
    except ValueError:
        messagebox.showerror("Error", "La permutación debe contener solo números separados por espacio.")
        return

    if sorted(perm) != list(range(1, grupo+1)):
        messagebox.showerror("Error", f"La permutación debe ser una reordenación de 1 a {grupo}.")
        return

    texto = normalizar_texto(texto, grupo)

    global texto_cifrado
    texto_cifrado = cifrar(texto, grupo, perm)

    salida_texto.config(state="normal")
    salida_texto.delete("1.0", tk.END)
    salida_texto.insert(tk.END, texto_cifrado)
    salida_texto.config(state="disabled")

    messagebox.showinfo("Éxito", "Texto cifrado generado correctamente. Ahora puedes guardarlo.")

def guardar_archivo():
    if not texto_cifrado:
        messagebox.showerror("Error", "No hay texto cifrado para guardar. Primero genera el cifrado.")
        return

    try:
        ruta = os.path.join(os.path.dirname(__file__), "cifrado.txt")

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto_cifrado)

        messagebox.showinfo("Éxito", f"Archivo guardado en:\n{ruta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

def cargar_archivo():
    archivo = filedialog.askopenfile(
        title="Seleccionar archivo",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if archivo:
        try:
            with open(archivo.name, 'r', encoding='utf-8') as f:
                contenido = f.read()
            entrada_texto.delete("1.0", tk.END)
            entrada_texto.insert(tk.END, contenido)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

ventana = tk.Tk()
ventana.title("Cifrado por Permutación de Grupos")
ventana.geometry("550x550")

texto_cifrado = ""

tk.Label(ventana, text="Texto claro (ingrese manualmente o cargue un archivo):").pack()
entrada_texto = tk.Text(ventana, height=6, width=60)
entrada_texto.pack()

tk.Button(ventana, text="Cargar archivo .txt", command=cargar_archivo).pack(pady=5)

tk.Label(ventana, text="Tamaño del grupo:").pack()
entrada_grupo = tk.Entry(ventana)
entrada_grupo.pack()

tk.Label(ventana, text="Permutación (ejemplo: 3 1 4 2):").pack()
entrada_permutacion = tk.Entry(ventana)
entrada_permutacion.pack()

tk.Button(ventana, text="Cifrar", command=ejecutar_cifrado).pack(pady=10)

tk.Label(ventana, text="Texto cifrado:").pack()
salida_texto = tk.Text(ventana, height=6, width=60, state="disabled")
salida_texto.pack()

tk.Button(ventana, text="Guardar en archivo .txt", command=guardar_archivo).pack(pady=10)

ventana.mainloop()