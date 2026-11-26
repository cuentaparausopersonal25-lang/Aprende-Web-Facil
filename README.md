# Aprende Web Fácil 2.0

Academia de programación en español construida con Flask, SQLite, Jinja, HTML, CSS y JavaScript. Incluye un tema oscuro y una ruta de aprendizaje para principiantes.

## Funciones
- 21 cursos con 4 clases cada uno (84 clases).
- Ejemplos de código y explicaciones por tema.
- Registro e inicio de sesión de estudiantes.
- Seguimiento de clases completadas.
- Experiencia (XP), insignias, rachas de estudio y ranking.
- Evaluaciones por curso con guardado de resultados y XP por primera aprobación.
- Apuntes privados por lección y lista personal de cursos favoritos.
- Buscador de cursos y filtros por categoría.
- Certificado de finalización imprimible al completar un curso.
- Laboratorio de HTML, CSS y JavaScript con vista previa aislada.
- Retos semanales editables desde el panel administrador.
- 10 herramientas de práctica para desarrollo web.
- Proyectos guiados, comentarios y vitrina pública de proyectos de estudiantes.\n- Perfil editable de estudiante con presentación, tecnologías y portfolio.\n- Centro de notificaciones con base de datos preparado para avisos.\n- Tutor de programación opcional compatible con API de chat; se activa configurando una clave privada en Render.
- Biblioteca práctica ampliable con recursos, ejemplos y categorías.\n- Plan personal de estudio con metas, fechas y seguimiento.\n- Panel administrador para publicar y retirar recursos de la biblioteca.\n- Panel de administración para publicar el reto semanal, moderar comentarios y entregas, y consultar estadísticas de aprendizaje.
- Pruebas automatizadas con GitHub Actions.

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

## Ejecutar pruebas
Ejecutá `python -m unittest discover -s tests -v`. GitHub Actions también corre estas pruebas automáticamente al actualizar la rama principal.

## Variables de entorno en Render
- SECRET_KEY: clave larga, aleatoria y privada. Render puede generarla desde render.yaml.
- ADMIN_USER: usuario del panel de administración (el archivo render.yaml propone admin).
- ADMIN_PASSWORD: contraseña privada del panel. Configurala en Environment en Render; no la subas a GitHub.
- DATABASE_PATH (opcional): ruta del archivo SQLite.
- COOKIE_SECURE: dejala en true en producción HTTPS.\n- AI_API_KEY: clave privada del proveedor de IA; no la subas a GitHub.\n- AI_API_URL (opcional): endpoint compatible con Chat Completions.\n- AI_MODEL (opcional): modelo habilitado en tu proveedor; por defecto gpt-4o-mini.

## Rutas principales
- / inicio
- /aprender-programar ruta de aprendizaje
- /curso/html ejemplo de curso
- /registro crear cuenta
- /ingresar iniciar sesión
- /mi-aprendizaje panel del estudiante
- /laboratorio editor de práctica
- /proyectos proyectos guiados\n- /comunidad/proyectos vitrina pública de proyectos\n- /mi-perfil perfil del estudiante\n- /tutor tutor de IA (requiere AI_API_KEY)\n- /notificaciones bandeja de avisos
- /retos desafío comunitario
- /ranking tabla de experiencia
- /admin/login acceso administrador

## Importante sobre los datos
La aplicación usa SQLite. En un servicio Render sin disco persistente o base de datos externa, los datos guardados en el archivo local pueden perderse cuando el servicio se reinicia o se vuelve a desplegar. Para conservar cuentas y progreso de forma confiable, configurá un disco persistente o migrá a PostgreSQL antes de usarla con muchos estudiantes.

Los certificados son constancias internas de finalización de Aprende Web Fácil, no acreditaciones oficiales.