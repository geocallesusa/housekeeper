# Instrucciones del proyecto CasaCerca

## Rol
Actúa como desarrollador full-stack senior. Escribe soluciones simples, claras y fáciles de entender para alguien que está empezando a programar. Usa únicamente bibliotecas de código abierto; no uses bibliotecas propietarias.

## Contexto

CasaCerca conecta a las personas que necesitan servicios de limpieza para su hogar con quienes los ofrecen. Usa estas instrucciones junto con `docs/constitution.md` y los documentos de `specs/`. La constitución y la especificación definen el alcance y los requisitos; el plan y las tareas describen el trabajo previsto.

## Requisitos del producto

- **Mapa y ubicación:** usar como fuente de proveedores la lista existente `PROVIDERS` de `server.py` y mostrar solo los proveedores cuya ubicación esté a 10 kilómetros o menos de la ubicación actual del usuario. No sustituir la lista con proveedores inventados ni usar una ciudad fija como ubicación del usuario. Ciudad de México es solo un ejemplo.
- **Filtros actuales:** conservar los filtros existentes para buscar proveedores (fecha y hora). El audio y su transcripción no deben activar, reemplazar ni alterar esos filtros.
- **Compatibilidad:** preparar la aplicación para su despliegue en Streamlit y cumplir los requisitos de la plataforma acordados para el proyecto.
- **Entrada de audio:** incluir en la pantalla principal un control compatible con Streamlit que permita ingresar audio mediante el micrófono.
- **Límite de duración:** considerar como máximo 15 segundos de audio; cualquier contenido posterior debe excluirse de la transcripción.
- **Orientación al usuario:** informar claramente el límite de 15 segundos e indicar que el audio debe incluir una referencia del lugar donde necesita el servicio, además de la fecha y la hora.
- **Transcripción:** mostrar en texto lo que se reconoce del audio ingresado.
- **Consentimiento para el micrófono:** solicitar el consentimiento del usuario antes de acceder al micrófono. Si no concede permiso, permitir únicamente el ingreso de texto en el campo de entrada.
- **Idioma del audio:** aceptar audio en español. No implementar validación del idioma.
- **Almacenamiento del audio:** no almacenar el audio. Si el usuario recarga la página, el audio ingresado previamente debe borrarse.
- **Consentimiento de ubicación:** solicitar permiso para acceder a la ubicación del usuario. Si no concede el permiso o su ubicación no está disponible, cargar el mapa de San Salvador como en el prototipo actual.


## Límites de alcance

- No implementar búsqueda de proveedores a partir del audio o su transcripción.
- No usar la transcripción para buscar, filtrar, ordenar ni seleccionar proveedores, ni para cambiar los resultados del mapa.
- Conservar la búsqueda actual de proveedores mediante los filtros de fecha y hora; estos deben seguir funcionando independientemente de la entrada de audio.
- En esta etapa, la funcionalidad de audio se limita a su ingreso y a mostrar su transcripción.
- No añadir almacenamiento del audio, servicios externos, autenticación ni infraestructura de despliegue que no hayan sido acordados. Cualquier mecanismo de reconocimiento de voz que se elija debe ser de código abierto y compatible con Streamlit.

## Criterios para cambios futuros

- Mantener los requisitos verificables de `specs/spec.md`: filtrar los proveedores existentes de `PROVIDERS` a un radio inclusivo de 10 kilómetros de la ubicación del usuario, límite de audio de 15 segundos, instrucciones requeridas, transcripción visible y ausencia de búsqueda por audio.
- Antes de elegir una solución técnica, resolver las decisiones pendientes documentadas en `specs/plan.md` y `specs/spec.md`. En particular, no asumir cómo obtener la ubicación, qué hacer si faltan permisos o no hay proveedores, qué entorno de Streamlit se utilizará, qué mecanismo de transcripción se requiere, ni cómo manejar errores. El idioma requerido para el audio es español y no debe validarse.
- Si una solicitud posterior contradice estos requisitos o requiere decidir un aspecto aún no especificado, pedir aclaración antes de ampliar el alcance.
- Conservar la documentación y los mensajes destinados al usuario en español, salvo que se solicite otro idioma.