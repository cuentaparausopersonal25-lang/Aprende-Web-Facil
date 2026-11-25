import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave-secreta-antes-de-publicar")
DATABASE = os.environ.get("DATABASE_PATH", "aprende_web.db")

COURSES = [
    {"slug":"primeros-pasos","title":"Primeros pasos en la web","level":"Principiante","duration":"30 min","description":"Entendé cómo funciona una página web y qué herramientas necesitás.","icon":"🌐"},
    {"slug":"html","title":"HTML desde cero","level":"Principiante","duration":"2 horas","description":"Aprendé a construir la estructura y el contenido de una página.","icon":"🧱"},
    {"slug":"css","title":"CSS desde cero","level":"Principiante","duration":"2 horas","description":"Dale estilo, colores, espacios y diseño adaptable a tu sitio.","icon":"🎨"},
    {"slug":"javascript","title":"JavaScript básico","level":"Inicial","duration":"2 horas","description":"Agregá interacción y comportamiento a tus páginas web.","icon":"⚡"},
    {"slug":"pagina-completa","title":"Tu primera página completa","level":"Inicial","duration":"1 hora","description":"Uní HTML, CSS y JavaScript en un pequeño proyecto.","icon":"🛠️"},
    {"slug":"github","title":"GitHub y tus proyectos","level":"Inicial","duration":"1 hora","description":"Guardá tu código y aprendé a subir proyectos a GitHub.","icon":"🐙"},
    {"slug":"render","title":"Publicar con Render","level":"Inicial","duration":"1 hora","description":"Publicá tu proyecto para que otras personas puedan visitarlo.","icon":"🚀"},
]

LESSONS = {
"primeros-pasos": {
 "intro":"Una página web es un conjunto de archivos que el navegador interpreta para mostrar información, imágenes, botones y otras funciones.",
 "sections":[
  ("¿Qué necesitamos?", "Para comenzar alcanza con una computadora, un navegador como Chrome y un editor de código. También vamos a usar Python y Flask cuando creemos páginas dinámicas."),
  ("¿Cómo llega una página a tu pantalla?", "El navegador solicita los archivos a un servidor. El servidor los envía y el navegador interpreta HTML, CSS y JavaScript para mostrar el resultado."),
  ("Los tres lenguajes principales", "HTML organiza el contenido; CSS controla su apariencia; JavaScript permite responder a acciones de las personas.")
 ],
 "code":'mi-proyecto/\\n├── app.py\\n├── templates/\\n│   └── index.html\\n└── static/\\n    └── css/\\n        └── style.css',
 "exercise":"Creá una carpeta llamada mi-primer-sitio. Dentro, imaginá qué archivos usarías para separar el contenido y el diseño.",
 "result":"Separar los archivos ayuda a mantener el proyecto ordenado y facilita encontrar errores."
},
"html": {
 "intro":"HTML significa HyperText Markup Language. Es el lenguaje de marcado que define la estructura de una página: títulos, párrafos, enlaces, imágenes y listas.",
 "sections":[
  ("La estructura básica", "Un documento HTML comienza con DOCTYPE. Luego se abre html, se define la información de la pestaña dentro de head y el contenido visible dentro de body."),
  ("Etiquetas y elementos", "Las etiquetas indican qué tipo de contenido estamos escribiendo. Por ejemplo, h1 representa el título principal y p representa un párrafo."),
  ("Atributos", "Los atributos agregan información a una etiqueta. En un enlace, href indica a qué dirección debe llevarnos.")
 ],
 "code":'<!DOCTYPE html>\\n<html lang="es">\\n<head>\\n  <meta charset="UTF-8">\\n  <title>Mi primera página</title>\\n</head>\\n<body>\\n  <h1>¡Hola, mundo!</h1>\\n  <p>Estoy aprendiendo HTML.</p>\\n  <a href="https://www.google.com">Visitar Google</a>\\n</body>\\n</html>',
 "exercise":"Agregá un segundo párrafo que cuente qué te gustaría crear y un subtítulo usando h2.",
 "result":"Al abrir el archivo en el navegador verás un título grande, un párrafo y un enlace. HTML define qué aparece, no su decoración."
},
"css": {
 "intro":"CSS significa Cascading Style Sheets. Se utiliza para controlar la apariencia: colores, tamaños, tipografías, márgenes y distribución.",
 "sections":[
  ("Conectar CSS", "Podés escribir estilos en un archivo separado y conectarlo desde el head con una etiqueta link. Así el diseño no queda mezclado con el contenido."),
  ("Selectores", "Un selector indica qué elementos queremos modificar. h1 selecciona todos los títulos h1; .destacado selecciona los elementos que tienen class=\"destacado\"."),
  ("Diseño adaptable", "Con media queries podemos cambiar el diseño según el ancho de pantalla. Esto permite que una página se vea bien en celulares y computadoras.")
 ],
 "code":'/* style.css */\\nbody {\\n  font-family: Arial, sans-serif;\\n  background: #f3f8ff;\\n  color: #14243b;\\n}\\n\\nh1 { color: #1769aa; }\\n\\n.destacado {\\n  padding: 16px;\\n  border-radius: 12px;\\n  background: white;\\n}',
 "exercise":"Creá una clase llamada tarjeta y aplicale un fondo blanco, espacio interior y bordes redondeados.",
 "result":"La clase se puede reutilizar en varios elementos. CSS permite cambiar el aspecto sin modificar el contenido HTML."
},
"javascript": {
 "intro":"JavaScript es un lenguaje de programación que permite que una página reaccione a lo que hace la persona: clics, formularios, cambios y cálculos.",
 "sections":[
  ("Una primera instrucción", "Podemos mostrar un mensaje en la consola del navegador usando console.log. La consola sirve para probar y revisar el comportamiento del código."),
  ("Variables", "Una variable guarda un dato que podemos utilizar más adelante. Usamos const cuando no vamos a reasignar el valor y let cuando sí puede cambiar."),
  ("Eventos", "Un evento ocurre cuando alguien realiza una acción, por ejemplo, presionar un botón. Podemos escuchar ese evento y ejecutar una función.")
 ],
 "code":'const boton = document.querySelector("#saludar");\\n\\nboton.addEventListener("click", () => {\\n  alert("¡Hola! Ya estás usando JavaScript.");\\n});',
 "exercise":"Creá un botón en HTML con id=\"saludar\" y probá el código JavaScript de la clase.",
 "result":"Al hacer clic en el botón aparecerá una ventana con un saludo. JavaScript agrega interacción a una página."
},
"pagina-completa": {
 "intro":"Ahora vamos a combinar HTML y CSS para construir una página sencilla con encabezado, presentación y una tarjeta de contenido.",
 "sections":[
  ("Planificá el contenido", "Antes de programar, decidí qué querés comunicar. Una página clara suele tener un título, una explicación breve y una acción principal."),
  ("Construí la estructura", "Usá header para el encabezado, main para el contenido principal y section para separar partes relacionadas."),
  ("Aplicá el diseño", "Con CSS podés definir el ancho máximo, centrar el contenido y crear tarjetas. Probá el resultado en una ventana angosta para revisar el diseño móvil.")
 ],
 "code":'<!DOCTYPE html>\\n<html lang="es">\\n<head>\\n  <meta charset="UTF-8">\\n  <meta name="viewport" content="width=device-width, initial-scale=1">\\n  <title>Mi proyecto</title>\\n  <link rel="stylesheet" href="style.css">\\n</head>\\n<body>\\n  <header><h1>Mi proyecto web</h1></header>\\n  <main><section><h2>Bienvenido</h2><p>Esta es mi primera página.</p></section></main>\\n</body>\\n</html>',
 "exercise":"Personalizá el título y el texto. Después agregá una tarjeta con una segunda sección.",
 "result":"Vas a tener una página con estructura semántica y una hoja de estilos independiente."
},
"github": {
 "intro":"GitHub es una plataforma para guardar proyectos usando Git. Permite tener copias del código, registrar cambios y compartir el trabajo.",
 "sections":[
  ("Repositorio", "Un repositorio es el espacio donde se guardan los archivos de un proyecto. Puede ser público o privado."),
  ("Subir archivos", "Desde GitHub podés crear un repositorio y usar Add file para crear o subir archivos. También podés trabajar desde tu computadora con Git."),
  ("Buenas prácticas", "Mantené nombres claros, organizá las carpetas y agregá un README que explique qué hace tu proyecto.")
 ],
 "code":'Estructura de ejemplo:\\nmi-pagina/\\n├── app.py\\n├── requirements.txt\\n├── Procfile\\n├── templates/\\n│   └── index.html\\n└── static/\\n    └── css/\\n        └── style.css',
 "exercise":"Creá un repositorio llamado mi-primera-web y prepará un README con el objetivo del proyecto.",
 "result":"Tu proyecto quedará guardado en GitHub y podrás conectarlo con servicios de publicación como Render."
},
"render": {
 "intro":"Render permite publicar aplicaciones web para que otras personas puedan acceder desde Internet. Puede conectarse a un repositorio de GitHub y desplegar los cambios.",
 "sections":[
  ("Preparar el proyecto", "En una aplicación Flask necesitás app.py y un archivo requirements.txt con las dependencias. También conviene incluir un Procfile con el comando de inicio."),
  ("Crear el servicio", "En Render elegí crear un Web Service y conectá el repositorio de GitHub. Seleccioná Python como entorno y configurá el comando de inicio."),
  ("Revisar el despliegue", "Cuando Render termina de construir la aplicación, muestra una dirección pública. Si falla, revisá los registros (logs): suelen indicar qué archivo o dependencia causó el problema.")
 ],
 "code":'requirements.txt:\\nFlask\\ngunicorn\\n\\nProcfile:\\nweb: gunicorn app:app',
 "exercise":"Revisá que tu proyecto tenga app.py, requirements.txt y Procfile antes de conectarlo con Render.",
 "result":"Al finalizar el despliegue tendrás una URL pública. Compartila para que otras personas puedan visitar tu página."
}
}

# Ampliación didáctica de los cursos
EXTRA_SECTIONS = {
  "primeros-pasos": [
    [
      "Qué es un algoritmo",
      "Un algoritmo es una serie ordenada de pasos para resolver un problema. Una receta tiene ingredientes y pasos; en programación hacemos algo parecido, pero escribiendo instrucciones."
    ],
    [
      "Frontend y backend",
      "Frontend es la parte que ve y utiliza la persona: textos, botones y pantallas. Backend es la parte que trabaja detrás: recibe datos, aplica reglas y puede consultar una base de datos."
    ],
    [
      "Archivos y carpetas",
      "HTML suele estar en templates, CSS y JavaScript en static, y una aplicación Flask puede iniciar desde app.py. Respetá los nombres y las mayúsculas."
    ],
    [
      "Cómo practicar",
      "Elegí un cambio pequeño, guardá el archivo, recargá el navegador y observá qué pasó. Si algo falla, revisá el mensaje de error y la ruta del archivo."
    ]
  ],
  "html": [
    [
      "Títulos y jerarquía",
      "Usá un h1 para el título principal y h2 para las secciones. Elegí la etiqueta por el significado del contenido, no solamente por su tamaño."
    ],
    [
      "Listas e imágenes",
      "ul crea una lista sin orden y ol una lista numerada. Para una imagen usamos img con src y un texto alternativo alt."
    ],
    [
      "Formularios",
      "Los formularios permiten recibir información. Cada input debe tener una etiqueta label asociada para que sea más fácil de usar."
    ],
    [
      "HTML semántico",
      "header, nav, main, section, article y footer describen partes de la página y ayudan a organizar el contenido."
    ],
    [
      "Errores frecuentes",
      "Revisá que las etiquetas estén bien escritas, que los atributos tengan comillas y que las rutas de imágenes o enlaces sean correctas."
    ]
  ],
  "css": [
    [
      "Colores, medidas y tipografía",
      "Podés usar hexadecimal como #1769aa. Para tamaños son comunes px, rem y porcentajes. Elegí una tipografía legible."
    ],
    [
      "Modelo de caja",
      "Cada elemento ocupa una caja: content es el contenido, padding el espacio interior, border el borde y margin el espacio exterior."
    ],
    [
      "Clases y reutilización",
      "Una clase empieza con punto en CSS, por ejemplo .tarjeta. En HTML se escribe class=tarjeta. Podés reutilizarla en muchos elementos."
    ],
    [
      "Flexbox y Grid",
      "Flexbox sirve para ordenar elementos en una dirección; Grid permite organizar filas y columnas."
    ],
    [
      "Responsive",
      "Una media query aplica estilos según el tamaño de pantalla. Probá tu página en un celular y evitá el desplazamiento horizontal."
    ]
  ],
  "javascript": [
    [
      "Tipos de datos",
      "JavaScript trabaja con textos (string), números (number), valores verdadero/falso (boolean), listas (arrays) y objetos."
    ],
    [
      "Condiciones",
      "if permite ejecutar instrucciones cuando se cumple una condición. else indica qué hacer cuando no se cumple."
    ],
    [
      "Repeticiones",
      "for y while repiten instrucciones. Usalos para procesar varios elementos, cuidando que el ciclo pueda terminar."
    ],
    [
      "Funciones",
      "Una función agrupa instrucciones para reutilizarlas. Puede recibir parámetros y devolver un resultado con return."
    ],
    [
      "DOM y eventos",
      "El DOM representa el documento HTML. Con querySelector seleccionás elementos y con addEventListener reaccionás a eventos como click."
    ]
  ],
  "pagina-completa": [
    [
      "Preparar la carpeta",
      "Separá index.html, style.css y script.js. En proyectos Flask, las plantillas van en templates y los recursos en static."
    ],
    [
      "Contenido accesible",
      "Usá títulos en orden, enlaces descriptivos, textos alternativos en imágenes y botones para acciones."
    ],
    [
      "Dar estilo",
      "Definí colores, tipografías y espacios generales. Después creá componentes reutilizables, como tarjetas y botones."
    ],
    [
      "Sumar interacción",
      "Conectá un archivo JavaScript y escuchá los eventos de los botones. Mantené el contenido y el comportamiento separados."
    ],
    [
      "Probar antes de publicar",
      "Revisá enlaces, botones, tamaños de pantalla y consola del navegador. Pedile a otra persona que pruebe la página."
    ]
  ],
  "github": [
    [
      "Qué es Git",
      "Git registra cambios en los archivos. GitHub aloja repositorios en Internet y agrega herramientas para colaborar."
    ],
    [
      "Commit",
      "Un commit es una captura de cambios con un mensaje que explica qué modificaste. Conviene hacer cambios pequeños y mensajes claros."
    ],
    [
      "Ramas",
      "Una rama permite probar cambios sin modificar inmediatamente la versión principal."
    ],
    [
      "README y .gitignore",
      "README.md explica el proyecto. .gitignore indica qué archivos no deberían subirse, como entornos virtuales o archivos con secretos."
    ],
    [
      "Cuidar información privada",
      "Nunca subas contraseñas, tokens ni claves SECRET_KEY. Si una clave se publica, cambiala."
    ]
  ],
  "render": [
    [
      "Comando de instalación",
      "Build Command instala las dependencias del proyecto, normalmente con pip install -r requirements.txt."
    ],
    [
      "Comando de inicio",
      "Para Flask con Gunicorn suele usarse gunicorn app:app: el primer app es el archivo app.py y el segundo es la variable Flask."
    ],
    [
      "Variables de entorno",
      "Las variables guardan configuración fuera del código. SECRET_KEY debe ser larga, aleatoria y privada. ADMIN_USER y ADMIN_PASSWORD definen el acceso administrativo si la aplicación las utiliza."
    ],
    [
      "Logs y errores",
      "Si el despliegue falla, abrí los logs y leé el último traceback desde el final. Buscá archivos faltantes, dependencias o variables no configuradas."
    ],
    [
      "Persistencia",
      "Algunos servicios pueden reemplazar el disco local al reiniciar. Para conservar datos importantes, necesitás almacenamiento persistente o una base de datos externa."
    ]
  ]
}
for course_slug, extra in EXTRA_SECTIONS.items():
    LESSONS[course_slug]["sections"].extend([tuple(item) for item in extra])

@app.route("/aprender-programar")
def learn_programming():
    return render_template("learn.html", courses=COURSES)

def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    with db() as conn:
        comments = conn.execute("SELECT * FROM comments ORDER BY id DESC LIMIT 20").fetchall()
    return render_template("index.html", courses=COURSES, comments=comments)

@app.route("/curso/<slug>")
def course(slug):
    item = next((c for c in COURSES if c["slug"] == slug), None)
    lesson = LESSONS.get(slug)
    if not item or not lesson:
        abort(404)
    return render_template("course.html", course=item, lesson=lesson, courses=COURSES)

@app.post("/comentarios")
def add_comment():
    message = request.form.get("message", "").strip()
    if not message:
        flash("Escribí una pregunta o comentario antes de publicar.", "error")
    elif len(message) > 600:
        flash("El mensaje es demasiado largo (máximo 600 caracteres).", "error")
    else:
        with db() as conn:
            conn.execute("INSERT INTO comments (message) VALUES (?)", (message,))
        flash("¡Tu mensaje se publicó correctamente!", "success")
    return redirect(url_for("home") + "#comunidad")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = os.environ.get("ADMIN_USER", "admin")
        password_hash = os.environ.get("ADMIN_PASSWORD_HASH")
        password = os.environ.get("ADMIN_PASSWORD", "cambiar123")
        entered_user = request.form.get("username", "")
        entered_password = request.form.get("password", "")
        valid_password = check_password_hash(password_hash, entered_password) if password_hash else entered_password == password
        if entered_user == username and valid_password:
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin():
    with db() as conn:
        comments = conn.execute("SELECT * FROM comments ORDER BY id DESC").fetchall()
    return render_template("admin.html", comments=comments, courses=COURSES)

@app.post("/admin/comentario/<int:comment_id>/eliminar")
@admin_required
def delete_comment(comment_id):
    with db() as conn:
        conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    flash("Comentario eliminado.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
