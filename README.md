# Aprende Web Fácil

Plataforma educativa creada con Python y Flask.

## Ejecutar en tu computadora

1. Instalá Python.
2. Abrí una terminal en esta carpeta.
3. Ejecutá `pip install -r requirements.txt`.
4. Ejecutá `python app.py`.
5. Abrí http://127.0.0.1:5000

## Administrador

- Dirección: `/admin/login`
- Usuario inicial: `admin`
- Contraseña inicial local: `cambiar123`

Antes de publicar, configurá en Render las variables `ADMIN_USER`, `ADMIN_PASSWORD` y `SECRET_KEY`. Cambiá la contraseña inicial por una propia y segura. También podés usar `ADMIN_PASSWORD_HASH` con un hash generado mediante Werkzeug.

## Publicación en Render

Conectá el repositorio de GitHub como Web Service. Render puede detectar `render.yaml`. Si configurás las variables manualmente, usá:
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

**Importante sobre comentarios:** la base SQLite se crea automáticamente. En servicios con disco efímero, los comentarios pueden perderse al reiniciar o desplegar. Para conservarlos, agregá un Persistent Disk en Render y configurá `DATABASE_PATH` con una ruta dentro del disco, por ejemplo `/var/data/aprende_web.db`.
