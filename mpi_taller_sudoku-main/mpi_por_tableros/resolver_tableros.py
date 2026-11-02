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

def run():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../seeds.txt'))
    if not os.path.exists(path):
        path = 'seeds.txt'

    boards = []
    if rank == 0:
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) == 2:
                            boards.append((int(parts[0]), parts[1]))
        t_start = time.perf_counter()
    else:
        t_start = None

    boards = comm.bcast(boards, root=0)

    my_boards = [boards[i] for i in range(rank, len(boards), size)]

    local_results = []
    for bid, bstr in my_boards:
        matriz_tablero = convertir_a_matriz(bstr)
        solved, t_partial = resolver_con_tiempo(matriz_tablero)
        local_results.append((bid, solved, t_partial))

    all_results = comm.gather(local_results, root=0)

    if rank == 0:
        t_end = time.perf_counter()
        total_time = t_end - t_start

        final_list = []
        for sub in all_results:
            final_list.extend(sub)
        final_list.sort(key=lambda x: x[0])

        print(f"\n--- MPI POR TABLEROS (Procesos: {size}) ---")
        for bid, solved, t_partial in final_list:
            status = "Resuelto" if solved else "Sin solución"
            print(f"ID: {bid} | Estado: {status} | Tiempo: {t_partial:.6f}s")

        print(f"\nTiempo total: {total_time:.6f} segundos")

if __name__ == '__main__':
    run()