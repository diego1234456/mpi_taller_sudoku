from mpi4py import MPI
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sudoku import resolver_con_tiempo

def convertir_a_matriz(texto):
    matriz = []
    for i in range(9):
        fila = []
        for j in range(9):
            val = texto[i * 9 + j]
            fila.append(0 if val in ('0', '.') else int(val))
        matriz.append(fila)
    return matriz

def encontrar_primera_vacia(matriz):
    for r in range(9):
        for c in range(9):
            if matriz[r][c] == 0:
                return r, c
    return None

def es_valido(matriz, fila, col, num):
    if num in matriz[fila]:
        return False
    if num in [matriz[r][col] for r in range(9)]:
        return False
    start_r, start_c = (fila // 3) * 3, (col // 3) * 3
    for r in range(3):
        for c in range(3):
            if matriz[start_r + r][start_c + c] == num:
                return False
    return True

def resolver_ramas_grupo(matriz_inicial, sub_comm):
    rank_g = sub_comm.Get_rank()
    size_g = sub_comm.Get_size()
    
    ramas = []
    if rank_g == 0:
        vacia = encontrar_primera_vacia(matriz_inicial)
        if vacia is not None:
            r, c = vacia
            for num in range(1, 10):
                if es_valido(matriz_inicial, r, c, num):
                    sub_matriz = [fila[:] for fila in matriz_inicial]
                    sub_matriz[r][c] = num
                    ramas.append(sub_matriz)
        else:
            ramas.append(matriz_inicial)

    ramas = sub_comm.bcast(ramas, root=0)
    if not ramas:
        return False, 0.0

    mis_ramas = [ramas[i] for i in range(rank_g, len(ramas), size_g)]
    
    resuelto_local = False
    t0 = time.perf_counter()
    for sub_matriz in mis_ramas:
        if resuelto_local:
            break
        ok, _ = resolver_con_tiempo(sub_matriz)
        if ok:
            resuelto_local = True
            break
    t1 = time.perf_counter()
    
    resultados = sub_comm.gather(resuelto_local, root=0)
    if rank_g == 0:
        encontro = any(resultados)
        return encontro, t1 - t0
    return False, 0.0

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Dividimos los 4 procesos en 2 grupos de 2 procesos cada uno
    num_grupos = 2 if size >= 2 else 1
    grupo_id = rank % num_grupos
    sub_comm = comm.Split(color=grupo_id, key=rank)

    ruta_seeds = os.path.abspath(os.path.join(os.path.dirname(__file__), '../seeds.txt'))
    if not os.path.exists(ruta_seeds):
        ruta_seeds = 'seeds.txt'

    tableros = []
    if rank == 0:
        if os.path.exists(ruta_seeds):
            with open(ruta_seeds, 'r') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#'):
                        partes = linea.split('|')
                        if len(partes) == 2:
                            tableros.append((int(partes[0]), partes[1]))
        t_inicio = time.perf_counter()
    else:
        t_inicio = None

    tableros = comm.bcast(tableros, root=0)

    # Cada grupo toma un subconjunto de tableros de forma cíclica
    mis_tableros = [tableros[i] for i in range(grupo_id, len(tableros), num_grupos)]

    resultados_locales = []
    for tid, bstr in mis_tableros:
        matriz = convertir_a_matriz(bstr)
        t_p0 = time.perf_counter()
        resuelto, _ = resolver_ramas_grupo(matriz, sub_comm)
        t_p1 = time.perf_counter()
        t_parcial = t_p1 - t_p0
        
        if sub_comm.Get_rank() == 0:
            resultados_locales.append((tid, resuelto, t_parcial))

    resultados_totales = comm.gather(resultados_locales, root=0)

    if rank == 0:
        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio

        todos = []
        for sublist in resultados_totales:
            todos.extend(sublist)
        todos.sort(key=lambda x: x[0])

        print(f"\n--- MPI HÍBRIDO (Procesos: {size}, Grupos: {num_grupos}) ---")
        for tid, resuelto, t_parcial in todos:
            estado = "Resuelto" if resuelto else "Sin solución"
            print(f"ID: {tid} | Estado: {estado} | Tiempo parcial: {t_parcial:.6f} segundos")

        print(f"\nTiempo total de ejecución: {tiempo_total:.6f} segundos")

if __name__ == '__main__':
    main()