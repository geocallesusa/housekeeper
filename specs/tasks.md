# Tareas de adaptación de CasaCerca

Este archivo refleja el estado de implementación y validación del prototipo.

## Implementación completada

- [x] Reutilizar `PROVIDERS` de `server.py` como fuente de proveedores.
- [x] Solicitar la ubicación del usuario desde el navegador y filtrar proveedores a un radio inclusivo de 10 kilómetros.
- [x] Mostrar el mapa de San Salvador y los proveedores del prototipo cuando no se obtiene la ubicación.
- [x] Mantener los filtros actuales de fecha y hora y aplicarlos de forma independiente de la entrada de audio.
- [x] Adaptar la interfaz a Streamlit y documentar la ejecución local.
- [x] Abrir la pantalla principal directamente, sin inicio de sesión.
- [x] Mostrar un mapa geográfico real con marcadores de proveedores y ubicación del usuario, sin dibujar el círculo del radio.
- [x] Solicitar consentimiento antes de grabar con el micrófono y permitir subir WAV sin acceder al micrófono.
- [x] Configurar Vosk con el modelo pequeño de español para transcripción local.
- [x] Considerar únicamente los primeros 15 segundos para la transcripción y descartar el contenido posterior.
- [x] Mostrar la transcripción y consultar el RAG existente cuando falta fecha o hora, sin modificar filtros ni mapa.
- [x] Procesar el audio en memoria y conservarlo únicamente durante la sesión necesaria para enviar la búsqueda.
- [x] Mostrar errores de coordenadas, audio o carga del modelo en la interfaz.

## Validación completada

- [x] Ejecutar las pruebas automatizadas de ubicación, distancia, filtros de disponibilidad y preparación del audio.
- [x] Verificar la selección entre búsqueda habitual, búsqueda RAG alternativa y aviso cuando faltan datos.
- [x] Verificar que el límite de 15 segundos también se aplica al audio enviado al reconocedor.
- [x] Compilar los módulos Python modificados.
- [x] Iniciar Streamlit localmente y comprobar su estado de salud.
- [x] Comprobar la pantalla principal y el mensaje de respaldo de San Salvador cuando no se obtiene ubicación.
- [x] Comprobar que, sin consentimiento para el micrófono, se muestra la entrada de texto y no el control de audio.
- [x] Cargar el modelo local de Vosk y ejecutar el flujo de transcripción con un archivo WAV de prueba silencioso.

## Validación pendiente

- [ ] Probar con el navegador el permiso de ubicación concedido y denegado.
- [ ] Probar una grabación hablada en español y comprobar la transcripción visible.
- [ ] Probar el permiso real del micrófono y la grabación desde un dispositivo compatible.
- [ ] Comprobar en el navegador que al recargar la página el audio previo ya no está disponible.
- [ ] Verificar el despliegue en el entorno de producción cuando se defina.
