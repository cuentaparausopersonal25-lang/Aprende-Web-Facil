# Aprende Web Fácil 2.0

Academia de programación en español construida con Flask, SQLite, Jinja, HTML, CSS y JavaScript. Incluye un tema oscuro y una ruta de aprendizaje para principiantes.

## Funciones
- 21 cursos con 4 clases cada uno (84 clases).
- Ejemplos de código y explicaciones por tema.
- Registro e inicio de sesión de estudiantes.
- Seguimiento de clases completadas.
- Experiencia (XP), insignias y ranking.
- Certificado de finalización imprimible al completar un curso.
- Laboratorio de HTML, CSS y JavaScript con vista previa aislada.
- Retos semanales editables desde el panel administrador.
- 10 herramientas de práctica para desarrollo web.
- Proyectos guiados y comunidad con comentarios.
- Comunidad con comentarios.
- Panel de administración para publicar el reto semanal, moderar comentarios y revisar estudiantes y entregas.

## Ejecutar localmente
1. Instalá Python 3.11 o superior.
2. Abrí una terminal en la carpeta del proyecto.
3. Instalá dependencias:
   bash: pip install -r requirements.txt
4. Configurá una clave secreta y desactivá cookies Secure para localhost:
   - Windows CMD: set SECRET_KEY=una-clave-larga-y-privada
   - Windows CMD: set COOKIE_SECURE=false
   - PowerShell: $env:SECRET_KEY="una-clave-larga-y-privada"
   - PowerShell: $env:COOKIE_SECURE="false"
5. Iniciá Flask: python app.py
6. Abrí http://127.0.0.1:5000

## Variables de entorno en Render
- SECRET_KEY: clave larga, aleatoria y privada. Render puede generarla desde render.yaml.
- ADMIN_USER: usuario del panel de administración (el archivo render.yaml propone admin).
- ADMIN_PASSWORD: contraseña privada del panel. Configurala en Environment en Render; no la subas a GitHub.
- DATABASE_PATH (opcional): ruta del archivo SQLite.
- COOKIE_SECURE: dejala en true en producción HTTPS.

## Rutas principales
- / inicio
- /aprender-programar ruta de aprendizaje
- /curso/html ejemplo de curso
- /registro crear cuenta
- /ingresar iniciar sesión
- /mi-aprendizaje panel del estudiante
- /laboratorio editor de práctica
- /proyectos proyectos
- /retos desafío comunitario
- /ranking tabla de experiencia
- /admin/login acceso administrador

## Importante sobre los datos
La aplicación usa SQLite. En un servicio Render sin disco persistente o base de datos externa, los datos guardados en el archivo local pueden perderse cuando el servicio se reinicia o se vuelve a desplegar. Para conservar cuentas y progreso de forma confiable, configurá un disco persistente o migrá a PostgreSQL antes de usarla con muchos estudiantes.

Los certificados son constancias internas de finalización de Aprende Web Fácil, no acreditaciones oficiales.