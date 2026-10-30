# Plan de adaptación de CasaCerca

## Objetivo

Registrar el enfoque elegido para adaptar el prototipo a Streamlit, implementar los requisitos acordados y validar los criterios de aceptación de `spec.md`.

## Alcance

- Usar la lista existente `PROVIDERS` como fuente de datos y, cuando se obtiene la ubicación del usuario, mostrar únicamente proveedores ubicados a 10 kilómetros o menos.
- Cuando la ubicación no está disponible, mostrar el mapa de San Salvador con los proveedores del prototipo.
- Conservar los filtros existentes de fecha y hora y mantenerlos independientes de la transcripción.
- Solicitar consentimiento antes de mostrar el control de micrófono.
- Procesar localmente con Vosk, considerar solo los primeros 15 segundos y mostrar la transcripción sin iniciar una búsqueda.
- No guardar el audio en archivos ni enviarlo a un servicio de transcripción.

## Decisiones adoptadas

- La interfaz se implementa en Streamlit y obtiene la ubicación del navegador mediante un componente interactivo de Streamlit v2.
- Si no se obtiene la ubicación, se centra el mapa en San Salvador y se muestran los proveedores del prototipo, como en la experiencia actual.
- El mapa se presenta con `st.map`, con marcadores para proveedores y la ubicación del usuario, sin dibujar el círculo del radio. Streamlit usa mosaicos de CARTO, por lo que se requiere conexión a Internet.
- La transcripción utiliza Vosk con el modelo pequeño de español. El modelo se descarga por separado y se carga desde `models\vosk-model-small-es-0.42` o desde la ruta indicada por `VOSK_MODEL_PATH`.
- El control de audio solo se presenta después de que el usuario marca su consentimiento. Sin consentimiento, queda disponible la entrada de texto alternativa.
- El audio se procesa en memoria; se descarta todo lo posterior a los primeros 15 segundos. El formulario limpia el control de audio después de enviarlo.
- Si faltan coordenadas válidas, se muestra un error y no se presentan resultados cercanos. Si no hay proveedores para la ubicación y horario seleccionados, se muestra el estado vacío.

## Etapas

1. **Revisar el prototipo y sus datos.** Completado: se reutilizan `PROVIDERS` y los filtros existentes; la aplicación Streamlit no requiere inicio de sesión.
2. **Implementar ubicación y mapa.** Completado: se solicitan las coordenadas del navegador, se aplica el radio inclusivo de 10 km y se conserva el mapa de respaldo de San Salvador.
3. **Adaptar la aplicación a Streamlit.** Completado para ejecución local. El entorno de alojamiento de producción aún no está especificado.
4. **Implementar entrada y transcripción de audio.** Completado: consentimiento, entrada alternativa de texto, procesamiento local con Vosk, recorte de audio a 15 segundos y transcripción visible, sin búsqueda por audio.
5. **Validar la adaptación.** Las pruebas automatizadas y la comprobación local de la aplicación están completadas. Las verificaciones que requieren permisos reales del navegador, una grabación hablada y un despliegue de producción siguen pendientes; se detallan en `tasks.md`.

## Validación pendiente

- Probar en un navegador el permiso de ubicación concedido y denegado.
- Probar una grabación hablada en español, la autorización del micrófono y el comportamiento al recargar la página.
- Verificar el despliegue en el entorno de producción cuando este se defina.

## Resultado esperado

La aplicación presenta los proveedores existentes ubicados a 10 kilómetros o menos cuando la ubicación del usuario está disponible, y conserva el mapa de San Salvador cuando no lo está. Mantiene los filtros manuales de fecha y hora. Permite, con consentimiento, ingresar audio, transcribir localmente solo los primeros 15 segundos y mostrar el texto reconocido sin utilizarlo para buscar, filtrar ni cambiar los resultados.
