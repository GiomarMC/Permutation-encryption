import re
import os
import tkinter as tk
import unicodedata
from collections import defaultdict
from itertools import chain
from math import isqrt, log
from tkinter import messagebox, filedialog

# --------------------------------------------
# ALFABETOS
# --------------------------------------------
alphabet_27 = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
alphabet_191 = ''.join(chr(i) for i in range(32, 223)) # no funciona 

ALPHABET = alphabet_27
N = len(ALPHABET)

def make_maps(alphabet):
    return {ch: i for i, ch in enumerate(alphabet)}, dict(enumerate(alphabet))

CHAR_TO_IDX, IDX_TO_CHAR = make_maps(ALPHABET)

freq_map_esp = {
    'A': 0.1226, 'B': 0.0149, 'C': 0.0387, 'D': 0.0467, 'E': 0.1408,
    'F': 0.0069, 'G': 0.0100, 'H': 0.0118, 'I': 0.0598, 'J': 0.0052,
    'K': 0.0011, 'L': 0.0524, 'M': 0.0308, 'N': 0.0683, 'Ñ': 0.0030,
    'O': 0.0920, 'P': 0.0289, 'Q': 0.0111, 'R': 0.0641, 'S': 0.0720,
    'T': 0.0460, 'U': 0.0469, 'V': 0.0105, 'W': 0.0004, 'X': 0.0014,
    'Y': 0.0109, 'Z': 0.0047
}

f_esp = [freq_map_esp.get(ch, 1.0 / len(ALPHABET)) for ch in ALPHABET]

N_TRIES = 7
TEXTO_VISIBLE = 200

# --------------------------------------------
# FUNCIONES AUXILIARES
# --------------------------------------------
def ord_to_index(ch):
    return CHAR_TO_IDX[ch]

def index_to_char(i):
    return IDX_TO_CHAR[i % N]

def normalizar_texto(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.upper()
    return ''.join(ch for ch in texto if ch in ALPHABET)

def es_repetida(s: str) -> bool:
    n = len(s)
    for i in range(1, n // 2 + 1):
        if n % i == 0 and s[:i] * (n // i) == s:
            return True
    return False

def frecuencia(texto: str) -> dict:
    freqs = defaultdict(int)
    for c in texto:
        freqs[c] += 1
    return dict(sorted(freqs.items(),
                       key=lambda item: item[1],
                       reverse=True))

# --------------------------------------------
# FUNCIONES DE SOPORTE
# --------------------------------------------
def trigramas_fuerza_bruta(texto):
    positions = {}
    for i in range(len(texto) - 2):
        tri = texto[i:i + 3]
        if '\n' in tri:
            continue
        if tri not in positions:
            positions[tri] = []
        positions[tri].append(i)

    dist_tri = {}
    for tri, list_pos in positions.items():
        if len(list_pos) > 1:
            dist = [list_pos[i + 1] - list_pos[i] for i in range(len(list_pos) - 1)]
            dist_tri[tri] = {"freq": len(list_pos), "pos": list_pos, "dist": dist}

    return dict(sorted(dist_tri.items(),
                       key=lambda item: item[1]["freq"],
                       reverse=True))

def divisores(n: int) -> list[int]:
    divs = set()
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    return list(divs)

def mcd_max_subconjunto(dists: list[int], max_len: int = 20) -> list[tuple[int, float]]:
    contador = defaultdict(int)
    for num in dists:
        for d in divisores(num):
            if 2 <= d <= max_len:
                contador[d] += 1

    puntuaciones = []
    total = len(dists)
    for d, cnt in contador.items():
        score = (cnt / total) * log(d + 1)
        puntuaciones.append((d, score))

    return sorted(puntuaciones, key=lambda x: x[1], reverse=True)[:N_TRIES]

# --------------------------------------------
# FUNCIONES DE ANÁLISIS
# --------------------------------------------
def analisis_subcriptogramas(subcriptos: list[str], mcd: int) -> list[dict[int, list[tuple[int, float]]]]:
    posible_clave = []
    for i in range(mcd):
        col = subcriptos[i]
        n = len(col)
        counts = [0] * N
        for ch in col:
            counts[ord_to_index(ch)] += 1
        f_obs = [counts[j]/n for j in range(N)] if n > 0 else [0]*N

        mejores = []
        for s in range(N):
            score = sum(f_obs[(j + s) % N] * f_esp[j % N] for j in range(N))
            mejores.append((s, score))
        mejores.sort(key=lambda x: x[1], reverse=True)

        posible_clave.append({
            "columna": i,
            "mejores_desplazamientos": mejores[:N_TRIES]
        })

    return posible_clave

def kasinski(texto_cifrado: str):
    trigramas = trigramas_fuerza_bruta(texto_cifrado)
    distancias = list(chain.from_iterable([info["dist"] for info in trigramas.values()]))
    candidatos_mcd = mcd_max_subconjunto(distancias)
    mcd_vals, _ = zip(*candidatos_mcd) if candidatos_mcd else ([], [])

    posibles_claves = []
    for mcd in mcd_vals:
        subcriptos = [""] * mcd
        for i in range(len(texto_cifrado)):
            subcriptos[i % mcd] += texto_cifrado[i]

        posible_clave = analisis_subcriptogramas(subcriptos, mcd)
        posibles_claves.append(posible_clave)

    return posibles_claves

def score_texto(texto: str) -> float:
    counts = [0] * N
    for ch in texto:
        if ch in CHAR_TO_IDX:
            counts[ord_to_index(ch)] += 1
    n = len(texto)
    if n == 0:
        return 0
    f_obs = [c/n for c in counts]
    return sum(f_obs[i] * f_esp[i % len(f_esp)] for i in range(N))

# --------------------------------------------
# FUNCIONES DE DECODIFICACIÓN
# --------------------------------------------
def vigenere_decrypt(texto_cifrado: str, clave: str) -> str:
    if not clave:
        raise ValueError("Clave vacía")
    plaintext_chars = []
    ki = 0
    for ch in texto_cifrado:
        c_idx = ord_to_index(ch)
        k_idx = ord_to_index(clave[ki % len(clave)])
        p_idx = (c_idx - k_idx) % N
        plaintext_chars.append(index_to_char(p_idx))
        ki += 1
    return ''.join(plaintext_chars)

def autoclave_decrypt(texto_cifrado: str, clave: str) -> str:
    if not clave:
        raise ValueError("Clave vacía")
    plaintext_chars = []
    for ci, ch in enumerate(texto_cifrado):
        c_idx = ord_to_index(ch)
        if ci < len(clave):
            k_idx = ord_to_index(clave[ci])
        else:
            k_idx = ord_to_index(plaintext_chars[ci - len(clave)])
        p_idx = (c_idx - k_idx) % N
        plaintext_chars.append(index_to_char(p_idx))
    return ''.join(plaintext_chars)

def descifrar(texto_cifrado: str) -> str:
    texto_cifrado = normalizar_texto(texto_cifrado)
    des = kasinski(texto_cifrado)
    resultados = []

    for d_ in des:
        for i in range(N_TRIES):
            clave = ""
            chi_sqr = 0
            for d in d_:
                clave += index_to_char(d["mejores_desplazamientos"][i][0])
                chi_sqr = d["mejores_desplazamientos"][i][1]

            if chi_sqr > 0.05:
                texto_vig = vigenere_decrypt(texto_cifrado, clave)
                score_vig = score_texto(texto_vig)

                texto_auto = autoclave_decrypt(texto_cifrado, clave)
                score_auto = score_texto(texto_auto)

                if not es_repetida(clave):
                    resultados.append((clave, "Vigenere", score_vig, texto_vig[:TEXTO_VISIBLE]))
                    resultados.append((clave, "Autoclave", score_auto, texto_auto[:TEXTO_VISIBLE]))

    resultados.sort(key=lambda x: x[2], reverse=True)

    lines = []
    for clave, tipo, score, preview in resultados[:N_TRIES]:
        lines.append(f"\tClave: {clave} ({tipo}) → Score={score:.4f}")
        lines.append(f"\tPreview: {preview}")
        lines.append("")
    return "\n".join(lines)

# --------------------------------------------
# TKINTER
# --------------------------------------------
def ejecutar_descifrado():
    global ALPHABET, N, CHAR_TO_IDX, IDX_TO_CHAR, f_esp

    ALPHABET = alphabet_27

    CHAR_TO_IDX, IDX_TO_CHAR = make_maps(ALPHABET)

    texto = entrada_texto.get("1.0", tk.END).strip()
    texto = normalizar_texto(texto)

    global texto_descifrado
    texto_descifrado = descifrar(texto)

    salida_texto.config(state="normal")
    salida_texto.delete("1.0", tk.END)
    salida_texto.insert(tk.END, texto_descifrado)
    salida_texto.config(state="disabled")

    messagebox.showinfo("Éxito", "Texto descifrado generado correctamente.")

def guardar_archivo():
    if not texto_descifrado:
        messagebox.showerror("Error", "No hay texto descifrado para guardar.")
        return
    try:
        ruta = os.path.join(os.path.dirname(__file__), "cifrado.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto_descifrado)
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
ventana.title("Descifrado Vigenere / Autoclave (no recomendado)")
ventana.geometry("600x600")

texto_descifrado = ""

tk.Label(ventana, text="Texto cifrado (ingrese manualmente o cargue un archivo):").pack()
entrada_texto = tk.Text(ventana, height=6, width=60)
entrada_texto.pack()

tk.Button(ventana, text="Cargar archivo (.txt)", command=cargar_archivo).pack(pady=5)

frame_opts = tk.Frame(ventana)
frame_opts.pack(pady=5)

tk.Button(ventana, text="Descifrar", command=ejecutar_descifrado).pack(pady=10)

tk.Label(ventana, text="Texto descifrado:").pack()
salida_texto = tk.Text(ventana, height=10, width=70, state="disabled")
salida_texto.pack()

tk.Button(ventana, text="Guardar en archivo .txt", command=guardar_archivo).pack(pady=10)

ventana.mainloop()