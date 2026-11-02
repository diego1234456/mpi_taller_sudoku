# Tarea 1: repartir tableros

Implementa una versión MPI en esta carpeta. Al ejecutar todos los tableros, cada ID debe ser una tarea que pueda asignarse a un proceso. Reutiliza el resolvedor de `../sudoku.py` y reúne los estados en el proceso coordinador.

Registra el tiempo total de ejecución y confirma que se procesaron los 30 IDs. Añade aquí el comando para ejecutar tu implementación con el contenedor. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, como en la calibración.


# MPI por Tableros

## Descripción
Estrategia que reparte los IDs de los 30 tableros de forma equitativa entre los procesos disponibles para procesar lotes completos de manera independiente.

## Instrucciones de Ejecución
Ejecuta la implementación con el contenedor Docker utilizando el siguiente comando en PowerShell:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec -n 4 --allow-run-as-root --use-hwthread-cpus --oversubscribe python /app/mpi_por_tableros/resolver_tableros.py
