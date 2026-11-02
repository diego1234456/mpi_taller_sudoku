# Informe de resultados

Completa este informe después de implementar las tres tareas MPI. Ejecuta las comparaciones con el mismo archivo `seeds.txt`, en el equipo y con el contenedor del taller.

## Entorno

* **Equipo:** Windows 10 (con contenedor Docker)
* **Versión del contenedor:** augustosalazar/slim-mpi:2[cite: 2]
* **Cantidad de repeticiones por medición:** 3
* **Valor común de N elegido:** 4

## Comparación final con el mismo N

Repite tres veces cada ejecución y registra la mediana. Mantén fijo el N elegido en todas las filas MPI. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en mpiexec, igual que en la calibración, para permitir valores de N mayores que los slots detectados.

| Implementación | Caso | Procesos | Mediana del tiempo total (s) | Aceleración frente a secuencial |
| :--- | :--- | :---: | :---: | :---: |
| Secuencial | Todos los IDs | 1 | 182.23 | 1,00 |
| MPI por tableros | Todos los IDs | 4 | 112.65 | 1,62 |
| MPI por ramas | Todos los IDs, uno después de otro | 4 | 201.67 | 0,90 |
| MPI híbrido | Todos los IDs | 4 | 213.93 | 0,85 |

Calcula la aceleración como `tiempo secuencial / tiempo MPI`. Mide el tiempo MPI desde el inicio del reparto hasta recibir todos los resultados necesarios.

## Conclusiones

* **¿Qué estrategia obtuvo el menor tiempo para los 30 tableros? ¿Cuánto mejoró respecto a la versión secuencial?**
  A los 30 tableros les fue mucho mejor con la estrategia de **MPI por tableros**, que marcó un tiempo total de 112.65 segundos. Al compararlo con los 182.23 segundos que tarda la versión secuencial, conseguimos una aceleración de **1.62x**, recortando bastante el tiempo de procesamiento.

* **¿Cómo afectaron la comunicación y las diferencias de duración entre tableros?**
  Aquí se nota claramente que los tableros no son iguales de difíciles; hay unos que se resuelven en un par de segundos y otros que exigen un backtracking pesado de más de 25 segundos. Cuando intentamos paralelizar a nivel de ramas o con el esquema híbrido, este desbalance de carga golpea duro porque los procesos que terminan rápido se quedan bloqueados esperando a los demás, a lo que se le suma el peso de estar comunicando y sincronizando datos a cada rato.

* **¿Cómo se comparó repartir tableros con resolverlos en orden y repartir las ramas de cada uno?**
  Repartir los tableros completos de entrada resulta ser la mejor opción porque cada proceso trabaja de forma independiente con un bloque asignado, reduciendo al mínimo las rondas de comunicación. En cambio, ir uno por uno y ponerse a repartir las ramas de la primera casilla vacía genera un cuello de botella terrible: la coordinación constante frena tanto el proceso que termina tardando incluso más que la versión secuencial pura.
