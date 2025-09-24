import tkinter as tk
from tkinter import filedialog, messagebox
import unicodedata

ALFABETO_27 = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
ALFABETO_191 = ''.join(chr(i) for i in range(32, 223))#ascii extendido

def normalizar_clave(texto_clave, alfabeto):
    texto = texto_clave.upper()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = ''.join(c for c in texto if c in alfabeto)
    return texto

def vigenere_descifrar(texto_cifrado, clave_norm, alfabeto):
    n = len(alfabeto)
    texto_plano = ""
    if len(clave_norm) == 0:
        raise ValueError("Clave vacía tras normalizar. No hay caracteres válidos para el alfabeto seleccionado.")

    for i, ch in enumerate(texto_cifrado):
        if ch in alfabeto:
            key_char = clave_norm[i % len(clave_norm)]
            c = alfabeto.index(ch)
            k = alfabeto.index(key_char)
            p = (c - k) % n
            texto_plano += alfabeto[p]
        else:
            texto_plano += ch

    return texto_plano

def cargar_archivo():
    ruta = filedialog.askopenfilename(title="Seleccionar archivo cifrado", filetypes=[("Text files", "*.txt"), ("All files","*.*")])
    if ruta:
        with open(ruta, "r", encoding="utf-8") as f:
            area_entrada.delete("1.0", tk.END)
            area_entrada.insert(tk.END, f.read())

def descargar_resultado(texto):
    ruta = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files","*.*")], title="Guardar texto descifrado como")
    if ruta:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)
        messagebox.showinfo("Guardado", f"Resultado guardado en:\n{ruta}")

def boton_descifrar():
    texto_cifrado = area_entrada.get("1.0", tk.END).rstrip("\n")
    clave = entry_clave.get().strip()
    if not texto_cifrado:
        messagebox.showwarning("Error", "Ingrese (o cargue) el texto cifrado.")
        return
    if not clave:
        messagebox.showwarning("Error", "Ingrese la clave usada para cifrar.")
        return

    alfabeto = ALFABETO_27 if var_alfabeto.get() == 27 else ALFABETO_191

    clave_norm = normalizar_clave(clave, alfabeto)
    if len(clave_norm) == 0:
        messagebox.showwarning("Error", "La clave no contiene caracteres válidos del alfabeto seleccionado después de normalizar.")
        return

    try:
        texto_a_procesar = texto_cifrado #.upper()


        resultado = vigenere_descifrar(texto_a_procesar, clave_norm, alfabeto)
    except Exception as e:
        messagebox.showerror("Error al descifrar", str(e))
        return

    area_salida.delete("1.0", tk.END)
    area_salida.insert(tk.END, resultado)

    if messagebox.askyesno("Guardar", "¿Deseas guardar el resultado descifrado en un archivo?"):
        descargar_resultado(resultado)

root = tk.Tk()
root.title("Descifrado Vigenère - Ventana independiente")

tk.Label(root, text="PEGA AQUÍ el texto CIFRADO (o carga archivo):").grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=(8,0))
area_entrada = tk.Text(root, height=8, width=70)
area_entrada.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

tk.Button(root, text="Cargar archivo cifrado", command=cargar_archivo).grid(row=2, column=0, sticky="w", padx=5)

tk.Label(root, text="Clave:").grid(row=3, column=0, sticky="w", padx=5)
entry_clave = tk.Entry(root, width=40)
entry_clave.grid(row=3, column=1, padx=5, pady=5, sticky="w")

var_alfabeto = tk.IntVar(value=27)
tk.Radiobutton(root, text="Alfabeto 27 (A-Z + Ñ)", variable=var_alfabeto, value=27).grid(row=4, column=0, sticky="w", padx=5)
tk.Radiobutton(root, text="Alfabeto 191 (ASCII extendido)", variable=var_alfabeto, value=191).grid(row=4, column=1, sticky="w")

tk.Button(root, text="Descifrar", command=boton_descifrar, bg="#88c", width=12).grid(row=5, column=0, pady=10, padx=5)
tk.Button(root, text="Limpiar", command=lambda: (area_entrada.delete("1.0", tk.END), area_salida.delete("1.0", tk.END), entry_clave.delete(0, tk.END))).grid(row=5, column=1, pady=10)

tk.Label(root, text="Texto descifrado:").grid(row=6, column=0, columnspan=3, sticky="w", padx=5)
area_salida = tk.Text(root, height=8, width=70)
area_salida.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
