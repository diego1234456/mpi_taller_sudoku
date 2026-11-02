# Tarea 3: combinar tableros y ramas

Implementa una versión MPI en esta carpeta. Reparte los IDs entre grupos de procesos y permite que los procesos de cada grupo exploren ramas distintas del tablero asignado.

Registra el tiempo total de los 30 IDs y explica cómo elegiste el tamaño de los grupos. Añade aquí el comando para ejecutar tu implementación con el contenedor. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, como en la calibración.


# MPI Híbrido

## Descripción
Enfoque combinado que agrupa los procesos para repartir los tableros globales y paraleliza simultáneamente las ramas internas dentro de cada grupo.

## Instrucciones de Ejecución
Ejecuta el modelo híbrido con el contenedor Docker usando el siguiente comando:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec -n 4 --allow-run-as-root --use-hwthread-cpus --oversubscribe python /app/mpi_hibrido/resolver_hibrido.py
