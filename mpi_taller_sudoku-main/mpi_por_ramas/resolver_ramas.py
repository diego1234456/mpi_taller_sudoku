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

def resolver_un_tablero_por_ramas(matriz_inicial, comm, rank, size):
    # El coordinador busca la primera casilla vacía y genera las ramas (candidatos válidos)
    ramas = []
    if rank == 0:
        vacia = encontrar_primera_vacia(matriz_inicial)
        if vacia is not None:
            r, c = vacia
            for num in range(1, 10):
                if es_valido(matriz_inicial, r, c, num):
                    # Creamos la sub-matriz con esta rama inicial
                    sub_matriz = [fila[:] for fila in matriz_inicial]
                    sub_matriz[r][c] = num
                    ramas.append(sub_matriz)
        else:
            # Si ya venía resuelto
            ramas.append(matriz_inicial)

    # Distribuir las ramas entre los procesos
    ramas = comm.bcast(ramas, root=0)
    
    if not ramas:
        return False, 0.0

    # Repartir las ramas de este tablero de forma cíclica entre los procesos
    mis_ramas = [ramas[i] for i in range(rank, len(ramas), size)]

    resuelto_local = False
    tiempo_local = 0.0
    t0 = time.perf_counter()

    for sub_matriz in mis_ramas:
        if resuelto_local:
            break
        # Resolver esta rama usando el resolvedor secuencial base
        ok, _ = resolver_con_tiempo(sub_matriz)
        if ok:
            resuelto_local = True
            break

    t1 = time.perf_counter()
    tiempo_local = t1 - t0

    # Reducir resultados: ¿Algún proceso encontró la solución?
    resultados = comm.gather(resuelto_local, root=0)
    
    if rank == 0:
        encontro = any(resultados)
        return encontro, tiempo_local
    return False, 0.0

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Parsear argumentos simples (--all o --id N)
    modo = "--all"
    target_id = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--id" and len(sys.argv) > 2:
            modo = "--id"
            target_id = int(sys.argv[2])
        elif sys.argv[1] == "--all":
            modo = "--all"

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
                            tid = int(partes[0])
                            if modo == "--all" or (modo == "--id" and tid == target_id):
                                tableros.append((tid, partes[1]))

    tableros = comm.bcast(tableros, root=0)

    if rank == 0:
        t_inicio = time.perf_counter()

    resultados_finales = []
    for tid, bstr in tableros:
        matriz = convertir_a_matriz(bstr)
        t_parcial_inicio = time.perf_counter()
        
        resuelto, _ = resolver_un_tablero_por_ramas(matriz, comm, rank, size)
        
        t_parcial_fin = time.perf_counter()
        t_parcial = t_parcial_fin - t_parcial_inicio

        if rank == 0:
            resultados_finales.append((tid, resuelto, t_parcial))
            estado = "Resuelto" if resuelto else "Sin solución"
            print(f"ID: {tid} | Estado: {estado} | Tiempo parcial: {t_parcial:.6f} segundos")

    if rank == 0:
        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio
        print(f"\nTiempo total de ejecución: {tiempo_total:.6f} segundos")

if __name__ == '__main__':
    main()