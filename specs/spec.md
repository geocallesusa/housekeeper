# Especificación de requisitos de CasaCerca

## 1. Propósito

CasaCerca conecta a las personas que necesitan servicios de limpieza para su hogar con quienes los ofrecen. Esta especificación convierte en requisitos verificables las definiciones de `docs/constitution.md`.

## 2. Alcance del producto

La aplicación adaptará el prototipo existente para presentar en un mapa los proveedores cercanos de `PROVIDERS`, prepararse para Streamlit y aceptar audio en la pantalla principal con transcripción visible.

La búsqueda existente por fecha y hora permanece sin cambios cuando ambos campos están completos. Si falta uno o ambos, el usuario puede proporcionar audio para transcribirlo y consultar el RAG existente; la transcripción no modifica los campos manuales ni los resultados del mapa.

## 3. Requisitos funcionales

### RF-01. Ubicación del usuario

La aplicación debe solicitar permiso para acceder a la ubicación del usuario y, si este concede el permiso, determinar la ubicación desde la que se consulta para centrar o contextualizar el mapa. La ubicación se refiere al usuario actual, no a una ubicación fija codificada en la interfaz.

### RF-02. Ubicación alternativa sin permiso

Si el usuario no concede permiso para acceder a su ubicación o esta no está disponible, la aplicación debe cargar el mapa de San Salvador como se muestra actualmente en el prototipo.

### RF-03. Proveedores cercanos en el mapa

La aplicación debe usar como fuente la lista existente `PROVIDERS` de `server.py` y mostrar únicamente los proveedores cuyas coordenadas estén a una distancia de hasta 10 kilómetros, inclusive, de la ubicación actual del usuario. Debe calcular la distancia entre la ubicación del usuario y la de cada proveedor.

No se deben crear proveedores sustitutos ni usar una ubicación fija para el usuario. Ciudad de México es un ejemplo de ubicación, no una ubicación predeterminada.

### RF-04. Compatibilidad con Streamlit

La solución debe adaptarse para su despliegue en Streamlit y cumplir los requisitos de dicha plataforma.

### RF-05. Entrada de audio

La pantalla principal debe incluir un campo o control compatible con Streamlit que permita ingresar audio usando el micrófono.

### RF-06. Duración máxima del audio

La transcripción debe considerar como máximo los primeros 15 segundos de audio. Cualquier contenido posterior debe excluirse.

### RF-07. Instrucciones al usuario

Antes o durante la captura, la interfaz debe informar que solo se consideran los primeros 15 segundos e indicar que el usuario debe mencionar dentro de ese tiempo:

- Una referencia del lugar donde necesita el servicio.
- La fecha.
- La hora.

### RF-08. Transcripción visible

La aplicación debe mostrar en texto lo que se reconoce del audio ingresado.

### RF-09. Búsqueda RAG alternativa con audio

Si falta la fecha o la hora al enviar la búsqueda de disponibilidad, la aplicación debe usar el audio disponible para obtener una transcripción y consultar la cadena RAG existente. La respuesta y las proveedoras recuperadas como contexto se muestran en una sección separada y no cambian los filtros ni los resultados del mapa.

### RF-10. Conservar los filtros actuales

La aplicación debe conservar sin cambios el flujo actual de búsqueda por fecha y hora cuando ambos campos estén completos. El audio y su transcripción nunca deben activar, reemplazar ni modificar esos filtros.

### RF-11. Consentimiento para el micrófono

La aplicación debe solicitar el consentimiento del usuario antes de acceder al micrófono.

### RF-12. Subida de archivo si no hay permiso para el micrófono

Si el usuario no concede permiso para acceder al micrófono, la aplicación no debe grabar audio. Puede subir un archivo WAV, ya que esa acción no accede al micrófono.

### RF-13. Idioma del audio

El audio ingresado será en español. La aplicación no debe validar ni rechazar el audio según su idioma.

### RF-14. No almacenar el audio

La aplicación no debe almacenar el audio ingresado. Al recargar la página, el audio ingresado previamente debe borrarse.

### RF-15. Bibliotecas de código abierto

Las bibliotecas utilizadas para implementar estos requisitos deben ser de código abierto. No se deben utilizar bibliotecas propietarias.

## 4. Criterios de aceptación

1. Se solicita permiso para acceder a la ubicación del usuario.
2. Cuando la ubicación está disponible, el mapa muestra los proveedores de `PROVIDERS` que están a 10 kilómetros o menos de la ubicación actual del usuario.
3. Los proveedores de `PROVIDERS` que están a más de 10 kilómetros no se muestran como resultados cercanos.
4. No se crean proveedores sustitutos y la ubicación del usuario no se fija a una ciudad predeterminada.
5. Si la ubicación no está disponible o el usuario no concede permiso, se carga el mapa de San Salvador como se muestra actualmente en el prototipo.
6. La solución es compatible con los requisitos aplicables de Streamlit para el despliegue acordado.
7. La pantalla principal ofrece una entrada de audio mediante micrófono y comunica claramente que solo se consideran los primeros 15 segundos.
8. La interfaz solicita que se mencione una referencia del lugar, la fecha y la hora.
9. El contenido posterior a los primeros 15 segundos no afecta el texto transcrito.
10. El texto reconocido se muestra al usuario.
11. Cuando fecha y hora están completas, la búsqueda existente por disponibilidad conserva su comportamiento.
12. Si falta la fecha o la hora, el audio disponible se transcribe y se consulta con el RAG existente.
13. La respuesta RAG y las proveedoras recuperadas se muestran por separado y no modifican los campos de fecha/hora ni los resultados del mapa.
14. Se solicita consentimiento antes de acceder al micrófono.
15. Si el usuario no concede permiso al micrófono, no se graba audio; puede subir un archivo WAV.
16. El audio se procesa como audio en español, sin validación automática de idioma.
17. El audio no se persiste y, al recargar la página, ya no está disponible.
18. Las bibliotecas utilizadas son de código abierto y no propietarias.

## 5. Restricciones

- Los proveedores de referencia son los definidos en `PROVIDERS` en `server.py`; se muestran únicamente si están a 10 kilómetros o menos del usuario.
- Se deben conservar los filtros actuales de fecha y hora para la búsqueda de proveedores; el audio y su transcripción no deben activar ni modificar esos filtros.
- Para la transcripción se consideran como máximo los primeros 15 segundos; cualquier contenido posterior se descarta.
- Si falta la fecha o la hora, el texto transcrito se utiliza únicamente como consulta al RAG existente y la respuesta se muestra separada.
- Se debe solicitar permiso para acceder a la ubicación; si no se concede, se carga el mapa actual de San Salvador.
- El usuario debe consentir antes de que la aplicación acceda al micrófono.
- Si no se concede permiso al micrófono, no se graba audio. La subida de archivos WAV no usa el micrófono.
- El audio esperado es español y no se debe validar su idioma.
- El audio no debe almacenarse; recargar la página debe borrar el audio previamente ingresado.
- Solo se permiten bibliotecas de código abierto.
- Para el prototipo se eligió Vosk con el modelo pequeño de español, descargado por separado y procesado localmente. El audio posterior a los primeros 15 segundos se descarta antes de transcribir.

## 6. Aspectos no especificados

La constitución no define los requisitos concretos del entorno de alojamiento de Streamlit ni un umbral de precisión para la ubicación. El prototipo muestra un estado vacío cuando no hay proveedores disponibles y notifica errores si faltan coordenadas o el modelo local no está configurado.
