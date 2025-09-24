import re
import unicodedata
from collections import defaultdict
from itertools import chain
from math import isqrt, log

f_esp = [ 0.1226, 0.0149, 0.0387, 0.0467, 0.1408, 0.0069, 0.010, 0.0118, 0.0598, 0.0052, 0.0011, 0.0524, 0.0308, 0.0683, 0.0920, 0.0289, 0.0111, 0.0641, 0.0720, 0.0460, 0.0469, 0.0105, 0.0004, 0.0014, 0.0109, 0.0047 ] # Obtenido de https://es.sttmedia.com/frecuencias-de-letras-espanol

N = len(f_esp)
N_TRIES = 7
TEXTO_VISIBLE = 200

def ord_to_index(ch):
    """Convierte un carácter a un índice (A = 0 -> Z = 25)"""
    return ord(ch) - ord('A')

def index_to_char(i):
    """Convierte un índice a un carácter (A = 0 -> Z = 25)"""
    return chr(i + ord('A'))

def normalizar_texto(texto):
    """Elimina signos de puntuación y tildes de un texto y convierte todos sus caracteres a mayúsculas"""
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')

    texto = texto.upper()
    texto = re.sub(r'[^A-Z]', '', texto)

    return texto

def es_repetida(s: str) -> bool:
    """Detecta si una cadena está conformada de la repetición de una subcadena."""
    n = len(s)
    for i in range(1, n // 2 + 1):
        if n % i == 0:
            patron = s[:i]
            if patron * (n // i) == s:
                return True
    return False

def frecuencia(texto: str) -> dict:
    """Devuelve la frecuencia de las letras en el texto (A = 0 -> Z = 25)"""
    freqs = defaultdict(int)

    for c in texto:
        freqs[c] += 1
    
    return dict(sorted(freqs.items(),
                       key=lambda item: item[1],
                       reverse=True))

def trigramas_fuerza_bruta(texto):
    """Halla la frecuencia de los trigramas de un texto. Devuelve una lista ordenada por frecuencia."""
    positions = {}

    for i in range(len(texto) - 2):
        tri = texto[i:i + 3]
        # sin salto de línea
        if '\n' in tri:
            continue

        if tri not in positions:
            positions[tri] = []
        positions[tri].append(i)

    # distancias
    dist_tri = {}
    for tri, list_pos in positions.items():
        if len(list_pos) > 1:
            dist = [list_pos[i + 1] - list_pos[i] for i in range(len(list_pos) - 1)]
            dist_tri[tri] = {
                "freq": len(list_pos),
                "pos": list_pos,
                "dist": dist
            }

    return dict(sorted(dist_tri.items(),
                       key=lambda item: item[1]["freq"],
                       reverse=True))

def divisores(n: int) -> list[int]:
    """Devuelve todos los divisores de n."""
    divs = set()
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    return list(divs)

def mcd_max_subconjunto(dists: list[int], max_len: int = 20) -> list[tuple[int, float]]:
    """Halla los valores más probables a ser la longitud de la clave según el máximo común divisor.
    Devuelve el valor más un puntaje de acercamiento."""
    contador = defaultdict(int)

    for num in dists:
        for d in divisores(num):
            if 2 <= d <= max_len:
                contador[d] += 1

    puntuaciones = []
    total = len(dists)
    for d, cnt in contador.items():
        # correlacion
        score = (cnt / total) * log(d + 1)
        puntuaciones.append((d, score))

    return sorted(puntuaciones, key=lambda x: x[1], reverse=True)[:N_TRIES]

def analisis_subcriptogramas(subcriptos: list[str], mcd: int) -> list[dict[int, list[tuple[int, float]]]]:
    """Halla el índice del carácter mejor posicionado para ser parte de la clave.
    Devuelve el índice más un puntaje de acercamiento."""
    posible_clave = []
    for i in range(mcd):
        col = subcriptos[i]
        n = len(col)
        counts = [0] * N
        for ch in col:
            counts[ord_to_index(ch)] += 1
        f_obs = [counts[j]/n for j in range(N)]

        mejores = []
        for s in range(N):
            # correlacion
            score = sum(f_obs[(j + s) % N] * f_esp[j] for j in range(N))
            mejores.append((s, score))
        mejores.sort(key=lambda x: x[1], reverse=True)

        posible_clave.append({
            "columna": i,
            "mejores_desplazamientos": mejores[:N_TRIES]
        })

    return posible_clave

def kasinski(texto_cifrado: str):
    """"""
    # Trigramas
    trigramas = trigramas_fuerza_bruta(texto_cifrado)
    
    # Desempaquetado
    distancias = list(chain.from_iterable([info["dist"] for info in trigramas.values()]))
    
    candidatos_mcd = mcd_max_subconjunto(distancias)
    mcd_vals, _ = zip(*candidatos_mcd)

    # Pruebas con valores de longitud
    posibles_claves = []

    for mcd in mcd_vals:
        # Subcriptogramas
        subcriptos = [""] * mcd
        for i in range(len(texto_cifrado)):
            subcriptos[i % mcd] += texto_cifrado[i]

        frecuencias_texto = [{}]
        frecuencias_texto.append(frecuencia(texto_cifrado))

        # Frecuencia de subcriptogramas
        for sub in subcriptos:
            frecuencias_texto.append(frecuencia(sub))

        posible_clave = analisis_subcriptogramas(subcriptos, mcd)

        posibles_claves.append(posible_clave)

    return posibles_claves

def vigenere_decrypt(texto_cifrado: str, clave: str) -> str:
    """"""
    if not clave:
        raise ValueError("Clave vacía después de limpiar. Provee una clave válida A-Z.")
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
    """Descifra un texto cifrado con autoclave dado un texto cifrado y una clave inicial.
    Dado que el programa no detecta una autoclave, es muy probable que falle."""
    if not clave:
        raise ValueError("Clave vacía después de limpiar. Provee una clave válida A-Z.")
    
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

def score_texto(texto: str) -> float:
    """Calcula la correlación del texto con la distribución del español.
    Devuelve el puntaje obtenido con respecto a la correlación."""
    counts = [0] * N
    for ch in texto:
        counts[ord_to_index(ch)] += 1
    n = len(texto)
    if n == 0:
        return 0
    f_obs = [c/n for c in counts]
    return sum(f_obs[i] * f_esp[i] for i in range(N))

def ejecutar_descifrado(texto_cifrado: str):
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
                # Vigenère
                texto_vig = vigenere_decrypt(texto_cifrado, clave)
                score_vig = score_texto(texto_vig)

                # Autoclave (al menos intentar)
                texto_auto = autoclave_decrypt(texto_cifrado, clave)
                score_auto = score_texto(texto_auto)

                if not es_repetida(clave):
                    resultados.append((clave, "Vigenere", score_vig, texto_vig[:TEXTO_VISIBLE]))
                    resultados.append((clave, "Autoclave", score_auto, texto_auto[:TEXTO_VISIBLE]))

    resultados.sort(key=lambda x: x[2], reverse=True)

    for clave, tipo, score, preview in resultados[:N_TRIES]:
        print(f"\tClave: {clave} ({tipo}) → Score={score:.4f}")
        print(f"\tPreview: {preview}\n")

texto_cifrado = "LNUDVMUYRMUDVLLPXAFZUEFAIOVWVMUOVMUEVMUEZCUDVSYWCIVCFGUCUNYCGALLGRCYTIJTRNNPJQOPJEMZITYLIAYYKRYEFDUDCAMAVRMZEAMBLEXPJCCQIEHPJTYXVNMLAEZTIMUOFRUFC"
texto_cifrado = texto_cifrado.replace(' ', '')
clave = "HOLAAMIGOS"

ejecutar_descifrado(texto_cifrado)