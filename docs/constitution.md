# Constitución del proyecto

**CasaCerca** conecta a las personas que necesitan servicios de limpieza para su hogar con quienes los ofrecen.

## 1. Propósito

El objetivo del proyecto es facilitar el contacto entre quienes necesitan servicios de limpieza y las personas que los ofrecen. El sistema actual es un prototipo que requiere adaptaciones.

## 2. Misión

Adaptar la solución actual para cumplir con los siguientes requisitos:

- **Mostrar proveedores cercanos en un mapa.** Usar como fuente de datos la lista existente `PROVIDERS` de `housekeeper\server.py` y mostrar únicamente los proveedores que estén a una distancia de hasta 10 kilómetros, inclusive, de la ubicación actual del usuario. No reemplazar la lista con proveedores inventados ni usar una ubicación fija para el usuario. Ciudad de México es solo un ejemplo.

- **Solicitar permiso para usar la ubicación.** Pedir permiso al usuario para acceder a su ubicación. Si no concede el permiso o la ubicación no está disponible, cargar el mapa de San Salvador como se muestra actualmente en el prototipo.

- **Preparar la aplicación para Streamlit.** La aplicación se desplegará en [Streamlit](https://streamlit.io/) y deberá cumplir con sus requisitos.

- **Permitir búsquedas por audio.** Incluir en la pantalla principal un campo compatible con Streamlit que permita ingresar una búsqueda mediante el micrófono. El audio tendrá una duración máxima de 15 segundos; cualquier contenido posterior deberá ignorarse. Se debe informar este límite al usuario e indicarle que incluya en esos 15 segundos una referencia del lugar donde necesita el servicio, así como la fecha y la hora.

- **Limitar la funcionalidad inicial del audio.** Por ahora, no desarrollar la búsqueda por audio. Solo permitir que el usuario ingrese el audio y mostrar en texto lo que se escuche.

- **Conservar los filtros actuales.** Mantener los filtros existentes de fecha y hora para buscar proveedores. La entrada de audio y su transcripción no deben activar ni modificar esos filtros.

- **Solicitar permiso para usar el micrófono.** Pedir el consentimiento del usuario antes de acceder al micrófono. Si no concede el permiso, permitir únicamente el ingreso de texto en el campo de entrada.

- **Aceptar audio en español.** El audio será en español. No se debe implementar validación del idioma.

- **No almacenar el audio.** El audio no debe persistirse. Si el usuario recarga la página, se debe borrar el audio ingresado previamente.

- **Usar bibliotecas de código abierto.** Las bibliotecas utilizadas para la solución deben ser de código abierto; no se deben incorporar bibliotecas propietarias.
