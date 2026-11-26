import os
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import secrets
import hmac
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "true").lower() == "true",
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)
DATABASE = os.environ.get("DATABASE_PATH", "aprende_web.db")

COURSES = [
    {"slug":"primeros-pasos","title":"Programación desde cero","level":"Principiante","duration":"2 horas","description":"Lógica, algoritmos, computadoras y primeros pasos para pensar como programador.","icon":"🧭","category":"Fundamentos","topics":["Qué significa programar","Algoritmos y pseudocódigo","Variables y tipos de datos","Condiciones y decisiones"]},
    {"slug":"html","title":"HTML completo","level":"Principiante","duration":"4 horas","description":"Construí la estructura de sitios con etiquetas, formularios, tablas y HTML semántico.","icon":"🧱","category":"Frontend","topics":["Documento y etiquetas HTML","Texto, enlaces e imágenes","Listas, tablas y formularios","HTML semántico y accesibilidad"]},
    {"slug":"css","title":"CSS profesional","level":"Principiante","duration":"5 horas","description":"Diseñá sitios modernos con selectores, Flexbox, Grid, responsive y animaciones.","icon":"🎨","category":"Frontend","topics":["Selectores y cascada","Modelo de caja y tipografía","Flexbox y CSS Grid","Responsive y animaciones"]},
    {"slug":"javascript","title":"JavaScript desde cero","level":"Inicial","duration":"6 horas","description":"Aprendé variables, funciones, condiciones, DOM, eventos y almacenamiento.","icon":"⚡","category":"Frontend","topics":["Variables y tipos de datos","Condiciones y bucles","Funciones y arrays","DOM, eventos y localStorage"]},
    {"slug":"pagina-completa","title":"Crear una web completa","level":"Inicial","duration":"4 horas","description":"Uní HTML, CSS y JavaScript para construir un sitio responsive de principio a fin.","icon":"🛠️","category":"Proyectos","topics":["Planificación y estructura","Componentes y estilos","Interactividad y formularios","Pruebas y publicación"]},
    {"slug":"python","title":"Python desde cero","level":"Principiante","duration":"6 horas","description":"Dominá la sintaxis, variables, listas, diccionarios, funciones y módulos.","icon":"🐍","category":"Backend","topics":["Instalación y sintaxis","Variables, operadores y tipos","Condiciones, bucles y colecciones","Funciones, módulos y archivos"]},
    {"slug":"flask","title":"Flask y backend web","level":"Inicial","duration":"5 horas","description":"Creá servidores, rutas, plantillas, formularios, sesiones y aplicaciones Flask.","icon":"🌶️","category":"Backend","topics":["Servidor y rutas","Plantillas Jinja","Formularios y sesiones","Estructura y despliegue"]},
    {"slug":"bases-datos","title":"Bases de datos y SQL","level":"Inicial","duration":"5 horas","description":"Guardá información con tablas, consultas SQL, relaciones y SQLite.","icon":"🗄️","category":"Backend","topics":["Tablas y registros","SELECT, WHERE y ORDER BY","INSERT, UPDATE y DELETE","Relaciones y SQLite con Python"]},
    {"slug":"github","title":"Git y GitHub","level":"Inicial","duration":"2 horas","description":"Controlá versiones, guardá cambios, usá ramas y compartí tus proyectos.","icon":"🐙","category":"Herramientas","topics":["Git y repositorios","Commit y seguimiento","Ramas y colaboración","GitHub desde el navegador"]},
    {"slug":"render","title":"Publicar con Render","level":"Inicial","duration":"2 horas","description":"Prepará Flask, conectá GitHub, configurá Render y revisá los logs.","icon":"🚀","category":"Herramientas","topics":["Preparar la aplicación","Conectar GitHub","Variables y comandos","Deploy, logs y mantenimiento"]},
    {"slug":"responsive","title":"Diseño adaptable","level":"Inicial","duration":"3 horas","description":"Hacé que tu web se vea bien en celulares, tablets y computadoras.","icon":"📱","category":"Frontend","topics":["Viewport y medidas flexibles","Media queries","Diseño mobile-first","Pruebas en distintos tamaños"]},
    {"slug":"bootstrap","title":"Bootstrap","level":"Inicial","duration":"3 horas","description":"Construí interfaces rápidas con grillas, componentes y utilidades Bootstrap.","icon":"🅱️","category":"Frontend","topics":["Instalación y contenedores","Sistema de grillas","Componentes y formularios","Personalización y responsive"]},
    {"slug":"react","title":"React inicial","level":"Intermedio","duration":"5 horas","description":"Comprendé componentes, props, estado, eventos y listas en React.","icon":"⚛️","category":"Frontend","topics":["Qué es React y componentes","JSX y props","Estado y eventos","Listas y proyecto pequeño"]},
    {"slug":"apis","title":"APIs y JSON","level":"Intermedio","duration":"4 horas","description":"Conectá aplicaciones con servicios externos y aprendé a consumir APIs.","icon":"🔌","category":"Backend","topics":["HTTP y endpoints","JSON y métodos","fetch y async/await","Errores y seguridad básica"]},
    {"slug":"seguridad","title":"Seguridad web básica","level":"Intermedio","duration":"4 horas","description":"Protegé formularios, sesiones, contraseñas y datos de tus usuarios.","icon":"🛡️","category":"Profesional","topics":["Contraseñas y hashing","Sesiones y cookies","Validación de datos","Secretos y buenas prácticas"]},
    {"slug":"php","title":"PHP desde cero","level":"Inicial","duration":"4 horas","description":"Conocé la sintaxis PHP, formularios, funciones y conexión a datos.","icon":"🐘","category":"Backend","topics":["Sintaxis y variables","Condiciones y funciones","Formularios y validación","Conexión a bases de datos"]},
    {"slug":"nodejs","title":"Node.js inicial","level":"Intermedio","duration":"4 horas","description":"Ejecutá JavaScript del lado del servidor y creá un servidor sencillo.","icon":"🟩","category":"Backend","topics":["Node y npm","Módulos y archivos","Servidor HTTP","Rutas y APIs sencillas"]},
    {"slug":"typescript","title":"TypeScript","level":"Intermedio","duration":"4 horas","description":"Agregá tipos a JavaScript para organizar proyectos más robustos.","icon":"🔷","category":"Frontend","topics":["Tipos básicos","Interfaces y objetos","Funciones tipadas","Uniones y proyecto"]},
    {"slug":"ux-ui","title":"Diseño UX/UI","level":"Inicial","duration":"3 horas","description":"Planificá experiencias claras con jerarquía visual, accesibilidad y prototipos.","icon":"🧩","category":"Diseño","topics":["UX y UI","Usuarios y objetivos","Jerarquía visual","Accesibilidad y prototipos"]},
    {"slug":"ia-programacion","title":"Inteligencia artificial para programar","level":"Intermedio","duration":"3 horas","description":"Usá asistentes de IA para aprender, revisar código y construir con criterio.","icon":"🤖","category":"Profesional","topics":["Qué puede y qué no puede hacer la IA","Prompts útiles para programar","Revisar y probar código generado","Privacidad y uso responsable"]},
    {"slug":"proyecto-final","title":"Proyecto final: tu aplicación","level":"Avanzado","duration":"8 horas","description":"Planificá, desarrollá, probá y publicá una aplicación web completa.","icon":"🏆","category":"Proyectos","topics":["Definir alcance y diseño","Construir frontend","Crear backend y datos","Probar, publicar y documentar"]},
]

DETAILS = {
"primeros-pasos":[
("Pensar como programador","Programar es transformar un problema en instrucciones claras. Antes de escribir código, definí qué información recibís, qué resultado querés y qué pasos conectan ambos.","Un algoritmo para preparar una merienda puede ser: elegir ingredientes, preparar utensilios, mezclar y servir. En programación los pasos deben ser precisos y ordenados."),
("Algoritmos y pseudocódigo","Un algoritmo es una secuencia finita de pasos. El pseudocódigo permite describir la solución con palabras estructuradas antes de elegir un lenguaje.","INICIO\n  leer nombre\n  mostrar 'Hola ' + nombre\nFIN"),
("Variables y tipos","Una variable es un nombre asociado a un valor. Los tipos habituales son texto, número y booleano. Elegí nombres que expliquen qué guardan.","nombre = 'Luna'\nedad = 15\nestudia = True\nprint(nombre, edad, estudia)"),
("Decisiones y repetición","Las condiciones permiten elegir caminos. Los bucles repiten instrucciones mientras se cumpla una regla. Son herramientas centrales para automatizar tareas.","edad = 18\nif edad >= 18:\n    print('Mayor de edad')\nelse:\n    print('Menor de edad')")
],
"html":[
("Estructura del documento","HTML describe el contenido. El navegador interpreta etiquetas anidadas. Un documento comienza con doctype, contiene metadatos en head y contenido visible en body.","<!doctype html>\n<html lang='es'>\n<head><meta charset='utf-8'><title>Mi web</title></head>\n<body><h1>Hola</h1></body>\n</html>"),
("Texto, enlaces e imágenes","Usá encabezados para organizar temas, párrafos para desarrollar ideas, enlaces para navegar e imágenes con texto alternativo para describir su contenido.","<h1>Mi proyecto</h1>\n<p>Estoy aprendiendo HTML.</p>\n<a href='/contacto'>Contacto</a>\n<img src='foto.jpg' alt='Paisaje de montaña'>"),
("Listas, tablas y formularios","Las listas agrupan elementos; las tablas presentan datos relacionados y los formularios reciben información. Cada campo debe tener una etiqueta comprensible.","<label for='email'>Correo</label>\n<input id='email' name='email' type='email' required>\n<button type='submit'>Enviar</button>"),
("Semántica y accesibilidad","Elegí etiquetas por su significado. header, nav, main, section, article y footer ayudan a lectores, navegadores y tecnologías de asistencia.","<header><h1>Mi sitio</h1></header>\n<main><article><h2>Una noticia</h2><p>Contenido...</p></article></main>\n<footer>© Mi web</footer>")
],
"css":[
("Selectores y cascada","CSS aplica reglas a elementos HTML. Un selector identifica qué elementos modificar. La cascada resuelve conflictos según origen, especificidad y orden.","h1 { color: #70d6ff; }\n.destacado { font-weight: 700; }\n#principal { max-width: 900px; }"),
("Modelo de caja","Cada elemento tiene contenido, padding, borde y margen. Usar box-sizing:border-box hace más predecible el cálculo del ancho.","* { box-sizing: border-box; }\n.card { padding: 20px; border: 1px solid #333; margin: 12px; }"),
("Flexbox y Grid","Flexbox distribuye elementos en una dimensión. Grid organiza filas y columnas. Elegí la herramienta según la estructura que necesites.",".fila { display: flex; gap: 1rem; align-items: center; }\n.grilla { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }"),
("Responsive y animaciones","Las media queries permiten adaptar estilos al ancho disponible. Priorizá contenido legible, controles cómodos y movimiento moderado.","@media (max-width: 700px) {\n  .grilla { grid-template-columns: 1fr; }\n}\nbutton { transition: transform .2s; }")
],
"javascript":[
("Variables y datos","Usá const para referencias que no reasignás y let cuando el valor cambiará. JavaScript distingue texto, números, booleanos, arrays, objetos y null.","const nombre = 'Sofi';\nlet puntos = 10;\npuntos += 5;\nconsole.log(nombre, puntos);"),
("Condiciones y bucles","if/else permite elegir caminos. for recorre una cantidad conocida de veces; for...of es útil para recorrer listas.","const notas = [8, 9, 10];\nfor (const nota of notas) {\n  if (nota >= 7) console.log('Aprobado');\n}"),
("Funciones y arrays","Una función agrupa una tarea reutilizable. Los parámetros reciben datos y return devuelve un resultado. Los arrays guardan colecciones ordenadas.","function sumar(a, b) {\n  return a + b;\n}\nconst total = sumar(4, 6);"),
("DOM y eventos","El DOM representa el documento. querySelector encuentra elementos y addEventListener permite reaccionar a clics, envíos y otras acciones.","const boton = document.querySelector('#saludar');\nboton.addEventListener('click', () => {\n  document.querySelector('#salida').textContent = '¡Hola!';\n});")
],
"pagina-completa":[
("Planificar y organizar","Antes de programar definí el objetivo, el público y las secciones. Separá HTML, CSS y JavaScript en archivos claros.","mi-sitio/\n├── index.html\n├── css/style.css\n└── js/main.js"),
("Construir la estructura","Usá etiquetas semánticas y ordená el contenido en encabezado, navegación, contenido principal y pie de página.","<header><h1>Mi sitio</h1></header>\n<nav><a href='#sobre-mi'>Sobre mí</a></nav>\n<main><section id='sobre-mi'>...</section></main>"),
("Aplicar estilos e interacción","Definí colores y espaciados reutilizables. Con JavaScript escuchá eventos y actualizá el contenido sin recargar la página.","const boton = document.querySelector('#tema');\nboton.addEventListener('click', () => {\n document.body.classList.toggle('claro');\n});"),
("Revisar y publicar","Probá enlaces, formularios, navegación con teclado y diseño móvil. Subí el proyecto a GitHub y publicalo desde un servicio de hosting.","Checklist:\n- Revisar en celular\n- Corregir rutas\n- Agregar README\n- Publicar y probar la URL")
],
"python":[
("Instalar y ejecutar","Python es un lenguaje de propósito general. Un archivo suele terminar en .py y se ejecuta con python archivo.py. Los espacios al inicio de línea definen bloques.","print('Hola, mundo')\n# Comentario: explica una decisión\nprint('Estoy aprendiendo Python')"),
("Variables y tipos","Los nombres de variables deben ser descriptivos. int representa enteros, float decimales, str texto y bool verdadero/falso. input recibe texto del usuario.","nombre = input('¿Cómo te llamás? ')\nedad = int(input('Edad: '))\nprint(f'Hola {nombre}, tenés {edad}')"),
("Condiciones y colecciones","if/elif/else permite decidir. Las listas guardan elementos ordenados y los diccionarios asocian claves con valores.","usuario = {'nombre': 'Ana', 'activo': True}\nif usuario['activo']:\n    print(usuario['nombre'])"),
("Funciones y archivos","Las funciones evitan repetir código. Los módulos agrupan funciones y with permite abrir archivos cerrándolos de forma segura.","def cuadrado(numero):\n    return numero * numero\n\nwith open('nota.txt', 'w', encoding='utf-8') as archivo:\n    archivo.write(str(cuadrado(5)))")
],
"flask":[
("Servidor y rutas","Flask crea aplicaciones web en Python. Una ruta conecta una URL con una función que devuelve una respuesta.","from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef inicio():\n    return 'Hola desde Flask'"),
("Plantillas Jinja","render_template busca archivos HTML dentro de templates. Jinja permite mostrar variables, recorrer listas y crear condiciones.","from flask import render_template\n\n@app.route('/saludo/<nombre>')\ndef saludo(nombre):\n    return render_template('saludo.html', nombre=nombre)"),
("Formularios y sesiones","Los formularios envían datos mediante GET o POST. Validá siempre en el servidor. Las sesiones guardan datos pequeños asociados a una visita.","from flask import request, session\n\n@app.post('/entrar')\ndef entrar():\n    usuario = request.form.get('usuario', '').strip()\n    session['usuario'] = usuario\n    return 'Sesión iniciada'"),
("Estructura y despliegue","Separá rutas, plantillas, estilos y configuración. Guardá claves en variables de entorno y usá un servidor WSGI como Gunicorn en producción.","# requirements.txt\nFlask\ngunicorn\n\n# inicio de producción\n# gunicorn app:app")
],
"bases-datos":[
("Tablas y registros","Una base relacional organiza información en tablas. Cada fila es un registro y cada columna un atributo. Una clave primaria identifica cada fila.","CREATE TABLE alumnos (\n  id INTEGER PRIMARY KEY,\n  nombre TEXT NOT NULL,\n  edad INTEGER\n);"),
("Consultar información","SELECT recupera columnas. WHERE filtra filas y ORDER BY ordena resultados. Evitá traer más datos de los necesarios.","SELECT nombre, edad\nFROM alumnos\nWHERE edad >= 13\nORDER BY nombre;"),
("Modificar registros","INSERT agrega filas, UPDATE modifica y DELETE elimina. En aplicaciones reales usá parámetros en lugar de concatenar texto para evitar inyección SQL.","INSERT INTO alumnos (nombre, edad)\nVALUES ('Alex', 14);\n\nUPDATE alumnos SET edad = 15 WHERE id = 1;"),
("Relaciones y SQLite","Las claves foráneas conectan tablas. SQLite guarda la base en un archivo y es útil para aprender y proyectos pequeños; en producción evaluá persistencia y copias de seguridad.","CREATE TABLE cursos (\n id INTEGER PRIMARY KEY,\n titulo TEXT NOT NULL\n);\n\nCREATE TABLE inscripciones (\n alumno_id INTEGER,\n curso_id INTEGER\n);")
],
"github":[
("Git y repositorios","Git registra la historia de cambios de un proyecto. Un repositorio contiene archivos y commits. GitHub aloja repositorios y agrega colaboración web.","git init\ngit status\ngit add .\ngit commit -m 'Primer commit'"),
("Commits y seguimiento","Un commit guarda una versión con un mensaje. Revisá git status antes de confirmar y agrupá cambios relacionados.","git add app.py\ngit commit -m 'Agregar ruta de inicio'\ngit log --oneline"),
("Ramas y colaboración","Las ramas permiten trabajar en una mejora sin tocar directamente la rama principal. Antes de combinar, revisá los cambios y resolvé conflictos.","git switch -c nueva-funcion\n# trabajar y guardar cambios\ngit switch main\ngit merge nueva-funcion"),
("GitHub desde el navegador","Podés crear archivos, editar, subir carpetas y revisar el historial desde GitHub. README explica el proyecto y .gitignore excluye archivos locales o secretos.","# .gitignore\n__pycache__/\n.venv/\n*.db\n.env")
],
"render":[
("Preparar Flask","Comprobá que app.py exponga una variable llamada app, que requirements.txt incluya dependencias y que el comando de inicio use Gunicorn.","# requirements.txt\nFlask\ngunicorn\n\n# Procfile\nweb: gunicorn app:app"),
("Conectar GitHub","Creá un Web Service, elegí el repositorio y la rama correcta. El servicio puede reconstruirse automáticamente cuando llega un nuevo commit.","Build: pip install -r requirements.txt\nStart: gunicorn app:app"),
("Variables de entorno","Guardá SECRET_KEY y contraseñas en el panel Environment. No las escribas en app.py ni las subas al repositorio. Usá valores largos y privados.","import os\nSECRET_KEY = os.environ.get('SECRET_KEY')\nADMIN_USER = os.environ.get('ADMIN_USER')"),
("Deploy y logs","Revisá el estado Live y probá la URL. Si aparece un error 500, abrí Logs y buscá la última excepción completa. Verificá rutas, dependencias y base de datos.","# Revisar dependencias\npip freeze\n\n# Inicio local\nflask --app app run --debug")
],
}
DETAILS.update({
"responsive":[
("Viewport y medidas flexibles","La etiqueta viewport permite que el navegador use el ancho real del dispositivo. Para diseños adaptables combiná porcentajes, max-width, rem y unidades relativas.","<meta name='viewport' content='width=device-width, initial-scale=1'>\n.container { width: min(100% - 2rem, 1100px); margin: auto; }"),
("Media queries","Una media query aplica reglas cuando se cumple una condición, por ejemplo cuando la pantalla es más angosta que cierto ancho.","@media (max-width: 700px) {\n  .menu { flex-direction: column; }\n}"),
("Mobile-first","Diseñá primero la versión pequeña y agregá mejoras para pantallas grandes. Así priorizás contenido y evitás esconder información importante.",".grid { display: grid; grid-template-columns: 1fr; }\n@media (min-width: 800px) {\n .grid { grid-template-columns: repeat(3, 1fr); }\n}"),
("Probar en dispositivos","Revisá navegación, botones, formularios y textos en diferentes anchos. Evitá anchos fijos que generen scroll horizontal.","img { max-width: 100%; height: auto; }\nbutton, a { min-height: 44px; }")
],
"bootstrap":[
("Instalación y contenedores","Bootstrap ofrece estilos y componentes listos. Podés incorporarlo con su CDN o instalarlo en un proyecto. container limita y centra el contenido.","<div class='container'>\n  <h1>Mi sitio</h1>\n</div>"),
("Sistema de grillas","La grilla se organiza en filas y columnas responsivas. Las clases col-md-6 ocupan la mitad del ancho desde el breakpoint md.","<div class='row'>\n <div class='col-md-6'>Columna A</div>\n <div class='col-md-6'>Columna B</div>\n</div>"),
("Componentes","Botones, tarjetas, alertas y navegación aceleran la construcción. Leé la documentación para conocer opciones y atributos requeridos.","<div class='card'>\n <div class='card-body'>\n  <h2 class='card-title'>Tarjeta</h2>\n </div>\n</div>"),
("Personalización","Podés combinar clases utilitarias y CSS propio. Evitá agregar reglas globales que rompan componentes existentes.","<button class='btn btn-primary'>Enviar</button>\n<style>.btn-primary { border-radius: 20px; }</style>")
],
"react":[
("Componentes","React permite construir interfaces a partir de piezas reutilizables. Un componente suele ser una función que devuelve JSX.","function Saludo() {\n return <h1>Hola, React</h1>;\n}"),
("JSX y props","JSX combina JavaScript con una sintaxis parecida a HTML. Las props permiten pasar información de un componente padre a uno hijo.","function Tarjeta({ titulo }) {\n return <article><h2>{titulo}</h2></article>;\n}"),
("Estado y eventos","useState guarda información que puede cambiar y provoca una nueva renderización cuando se actualiza.","const [contador, setContador] = useState(0);\n<button onClick={() => setContador(contador + 1)}>\n {contador}\n</button>"),
("Listas y proyecto","map permite transformar una lista de datos en elementos. Cada elemento necesita una key estable para que React pueda identificarlo.","const tareas = ['Leer', 'Practicar'];\nreturn tareas.map(t => <li key={t}>{t}</li>);")
],
"apis":[
("HTTP y endpoints","Una API permite que dos programas intercambien información. Un endpoint es una dirección que ofrece un recurso. HTTP define métodos y códigos de respuesta.","GET /api/productos\nPOST /api/productos\n200 OK · 404 Not Found"),
("JSON y métodos","JSON es un formato de texto para intercambiar datos. Los métodos GET consultan, POST crea, PUT/PATCH modifica y DELETE elimina.","const alumno = {\n  \"nombre\": \"Alex\",\n  \"activo\": true\n};"),
("fetch y async/await","fetch realiza solicitudes desde el navegador. async/await facilita esperar la respuesta. Comprobá response.ok antes de leer los datos.","async function cargar() {\n const r = await fetch('/api/datos');\n if (!r.ok) throw new Error('Error');\n return await r.json();\n}"),
("Errores y seguridad","Manejá errores de red, validá respuestas y no expongas claves privadas en JavaScript del navegador. Los secretos deben permanecer en el servidor.","try {\n const datos = await cargar();\n console.log(datos);\n} catch (error) {\n console.error(error);\n}")
],
"seguridad":[
("Contraseñas y hashing","Nunca guardes contraseñas en texto plano. Guardá un hash generado con una función específica para contraseñas, como scrypt, bcrypt o Argon2.","from werkzeug.security import generate_password_hash\nhash_seguro = generate_password_hash('una-clave-larga')"),
("Sesiones y cookies","Las sesiones mantienen el estado de inicio de sesión. Usá cookies HttpOnly, Secure bajo HTTPS y SameSite adecuado. Protegé las operaciones sensibles.","app.config.update(\n SESSION_COOKIE_HTTPONLY=True,\n SESSION_COOKIE_SECURE=True,\n SESSION_COOKIE_SAMESITE='Lax'\n)"),
("Validación de datos","Validá los datos en el servidor aunque también exista validación en el navegador. Limitá longitudes, tipos y valores permitidos.","nombre = request.form.get('nombre', '').strip()\nif not nombre or len(nombre) > 60:\n    abort(400)"),
("Secretos y buenas prácticas","No subas claves, tokens ni contraseñas a GitHub. Usá variables de entorno, dependencias actualizadas y permisos mínimos.","import os\nAPI_KEY = os.environ.get('API_KEY')\nif not API_KEY:\n    raise RuntimeError('Falta API_KEY')")
],
"php":[
("Sintaxis y variables","PHP se ejecuta en el servidor y genera respuestas, a menudo HTML. Las variables comienzan con signo dólar y las instrucciones suelen terminar en punto y coma.","<?php\n$nombre = 'Mica';\necho 'Hola ' . $nombre;\n?>"),
("Condiciones y funciones","if permite tomar decisiones. Las funciones reúnen instrucciones reutilizables y pueden recibir parámetros.","function sumar($a, $b) {\n  return $a + $b;\n}\necho sumar(3, 4);"),
("Formularios y validación","Los datos enviados pueden leerse desde $_POST. Validá y limpiá la información en el servidor antes de usarla o mostrarla.","$correo = filter_input(INPUT_POST, 'correo', FILTER_VALIDATE_EMAIL);\nif (!$correo) {\n  echo 'Correo inválido';\n}"),
("Bases de datos","PDO permite conectarse a bases de datos y ejecutar consultas preparadas. Los parámetros ayudan a evitar inyección SQL.","$stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?');\n$stmt->execute([$id]);\n$user = $stmt->fetch();")
],
"nodejs":[
("Node y npm","Node.js ejecuta JavaScript fuera del navegador. npm administra paquetes y scripts del proyecto.","node --version\nnpm init -y\nnpm install"),
("Módulos y archivos","Los módulos separan responsabilidades. Node admite módulos CommonJS y ES Modules; elegí uno y mantené la configuración consistente.","// archivo saludar.js\nexport function saludar(nombre) {\n return 'Hola ' + nombre;\n}"),
("Servidor HTTP","El módulo http permite crear un servidor básico que escucha solicitudes y devuelve respuestas.","import { createServer } from 'node:http';\ncreateServer((req, res) => {\n res.end('Hola desde Node');\n}).listen(3000);"),
("Rutas y APIs","Un servidor puede responder distinto según URL y método. En aplicaciones mayores se suelen usar frameworks y validación de entrada.","if (req.url === '/api/saludo') {\n res.setHeader('Content-Type', 'application/json');\n res.end(JSON.stringify({ mensaje: 'Hola' }));\n}")
],
"typescript":[
("Tipos básicos","TypeScript agrega un sistema de tipos estático a JavaScript. Los tipos ayudan a detectar errores antes de ejecutar el programa.","let nombre: string = 'Luz';\nlet edad: number = 16;\nlet activo: boolean = true;"),
("Interfaces y objetos","Las interfaces describen la forma de un objeto. Permiten documentar propiedades y reutilizar contratos de datos.","interface Alumno {\n nombre: string;\n edad: number;\n}\nconst persona: Alumno = { nombre: 'Luz', edad: 16 };"),
("Funciones tipadas","Podés indicar tipos de parámetros y del valor devuelto. Esto hace más claro qué espera una función.","function sumar(a: number, b: number): number {\n return a + b;\n}"),
("Uniones y proyecto","Los tipos unión permiten aceptar más de una alternativa. TypeScript se compila a JavaScript para ejecutarse en el navegador o Node.","type Estado = 'pendiente' | 'hecho';\nlet tarea: Estado = 'pendiente';")
],
"ux-ui":[
("UX y UI","UX es la experiencia completa al usar un producto. UI es la interfaz visual y sus controles. Ambas disciplinas trabajan juntas.","Objetivo: que una persona encuentre una acción importante sin tener que adivinar dónde está."),
("Usuarios y objetivos","Antes de diseñar, identificá quién usará el sitio, qué necesita lograr y qué obstáculos puede encontrar. Priorizá tareas reales.","Persona: estudiante principiante.\nObjetivo: encontrar su primera clase.\nNecesidad: instrucciones claras y visibles."),
("Jerarquía visual","Tamaño, contraste, espacio y posición guían la atención. Usá una acción principal clara y mantené consistencia entre pantallas.","h1 { font-size: 2.5rem; }\n.primary-action { background: #58e0b3; }\n.secondary-action { border: 1px solid #456; }"),
("Accesibilidad y prototipos","Diseñá para distintos dispositivos y capacidades. Revisá contraste, foco de teclado, etiquetas de formularios y textos alternativos.","<label for='mail'>Correo</label>\n<input id='mail' type='email'>\n<button>Enviar formulario</button>")
],
"ia-programacion":[
("Qué puede y qué no puede hacer la IA","Un asistente puede explicar conceptos, proponer ejemplos y ayudar a investigar errores, pero puede equivocarse o inventar APIs. Verificá cada respuesta.","Pedile: 'Explicá qué hace este bloque y señalá qué debería probar antes de usarlo'."),
("Prompts útiles","Un buen pedido incluye contexto, objetivo, código relevante, error exacto y restricciones. Pedí explicaciones y no solo una solución final.","Contexto: aplicación Flask.\nObjetivo: validar un formulario.\nError: copiar el traceback completo.\nPedido: explicar y proponer una corrección."),
("Revisar código generado","Leé el código, probalo con casos normales y extremos, revisá dependencias y comprobá que no exponga datos ni introduzca vulnerabilidades.","# Lista de revisión\n# 1. ¿Entiendo el código?\n# 2. ¿Probé entradas inválidas?\n# 3. ¿Protegí secretos?"),
("Privacidad y uso responsable","No pegues contraseñas, datos personales, claves privadas ni archivos confidenciales en herramientas públicas. Conservá la responsabilidad sobre el resultado.","Antes de compartir un fragmento, reemplazá tokens, claves y datos privados por valores ficticios.")
],
"proyecto-final":[
("Definir alcance y diseño","Elegí un problema pequeño y definí usuarios, pantallas y funciones indispensables. Escribí qué queda fuera del proyecto para evitar crecer sin control.","Proyecto: gestor de tareas.\nFunciones: crear, completar y borrar.\nPantallas: inicio, acceso y panel."),
("Construir frontend","Prepará estructura semántica y estilos adaptables. Separá los componentes y probá la navegación con teclado y pantalla pequeña.","<main>\n <h1>Mis tareas</h1>\n <form><label for='task'>Nueva tarea</label><input id='task'></form>\n</main>"),
("Crear backend y datos","Definí rutas y validaciones del servidor. Diseñá tablas con claves y consultas parametrizadas. Guardá contraseñas como hashes.","CREATE TABLE tasks (\n id INTEGER PRIMARY KEY,\n title TEXT NOT NULL,\n done INTEGER DEFAULT 0\n);"),
("Probar, publicar y documentar","Probá formularios, permisos, errores y diseño móvil. Publicá desde GitHub y revisá logs. Documentá instalación, configuración y uso.","Checklist final:\n- README actualizado\n- secretos en variables de entorno\n- pruebas manuales\n- URL publicada\n- capturas del proyecto")
]
})

DEFAULT_DETAILS = [
("Comprender el concepto","Empezá identificando qué problema resuelve esta tecnología, dónde se utiliza y qué conceptos necesitás conocer antes de avanzar. No memorices definiciones aisladas: relacioná cada idea con un ejemplo real.","Pensá en una aplicación pequeña y anotá qué datos recibe, qué proceso realiza y qué resultado muestra."),
("Leer un ejemplo","Observá la estructura del código, los nombres de variables y la función de cada instrucción. Cambiá un valor por vez para comprobar cómo cambia el resultado.","# Ejemplo para experimentar\nmensaje = 'Estoy aprendiendo'\nprint(mensaje)"),
("Practicar paso a paso","Dividí el ejercicio en tareas pequeñas. Probá cada parte, guardá los cambios y revisá el resultado antes de sumar más complejidad.","1. Prepará el archivo.\n2. Escribí una versión mínima.\n3. Ejecutá y observá.\n4. Mejorá una parte."),
("Aplicar y revisar","Un proyecto sirve para unir conceptos. Probá entradas válidas e inválidas, revisá mensajes de error y documentá cómo se utiliza.","Antes de terminar, comprobá que el proyecto funcione, que sus nombres sean claros y que otra persona pueda entenderlo.")
]
for c in COURSES:
    c["lessons"] = []
    details = DETAILS.get(c["slug"], DEFAULT_DETAILS)
    for i, (title, explanation, code) in enumerate(details, 1):
        c["lessons"].append({"number": i, "title": title, "explanation": explanation, "code": code})

@contextmanager
def get_db():
    path = Path(DATABASE)
    if str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS comments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          message TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS progress (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          course_slug TEXT NOT NULL,
          lesson_number INTEGER NOT NULL,
          completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id, course_slug, lesson_number)
        );
        CREATE TABLE IF NOT EXISTS challenge_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
          nickname TEXT NOT NULL,
          answer TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS site_settings (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS lesson_notes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          course_slug TEXT NOT NULL,
          lesson_number INTEGER NOT NULL,
          note TEXT NOT NULL,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id, course_slug, lesson_number)
        );
        CREATE TABLE IF NOT EXISTS bookmarks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          course_slug TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id, course_slug)
        );
        CREATE TABLE IF NOT EXISTS quiz_attempts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          course_slug TEXT NOT NULL,
          score INTEGER NOT NULL,
          total INTEGER NOT NULL,
          completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id, course_slug)
        );
        CREATE TABLE IF NOT EXISTS study_days (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          study_date TEXT NOT NULL,
          UNIQUE(user_id, study_date)
        );
        CREATE TABLE IF NOT EXISTS user_profiles (
          user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
          display_name TEXT NOT NULL DEFAULT '',
          bio TEXT NOT NULL DEFAULT '',
          website TEXT NOT NULL DEFAULT '',
          favorite_stack TEXT NOT NULL DEFAULT '',
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS project_posts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          title TEXT NOT NULL,
          description TEXT NOT NULL,
          technologies TEXT NOT NULL,
          project_url TEXT NOT NULL DEFAULT '',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS notifications (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          title TEXT NOT NULL,
          body TEXT NOT NULL,
          read_at TIMESTAMP,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)


def course_quiz(item):
    title = item["title"]
    return [
        {"question": "¿Cuál es el tema central de este curso?", "options": [title, "Edición de videos", "Diseño de hardware"], "answer": 0, "explanation": "El curso se centra en " + title + "."},
        {"question": "¿Qué conviene hacer después de leer un ejemplo?", "options": ["Copiarlo sin leer", "Modificarlo, probarlo y entender el resultado", "Borrarlo sin ejecutarlo"], "answer": 1, "explanation": "Experimentar y explicar el resultado ayuda a comprender."},
        {"question": "¿Qué hacer si aparece un error?", "options": ["Ignorarlo", "Borrar todo el proyecto", "Leer el mensaje, aislar el problema y probar una corrección"], "answer": 2, "explanation": "Los errores son parte del desarrollo; analizalos paso a paso."}
    ]

def mark_study_day(conn, user_id):
    conn.execute("INSERT OR IGNORE INTO study_days (user_id, study_date) VALUES (?, ?)",
                 (user_id, datetime.now(timezone.utc).date().isoformat()))

def calculate_streak(conn, user_id):
    days = {row["study_date"] for row in conn.execute(
        "SELECT study_date FROM study_days WHERE user_id = ?", (user_id,)).fetchall()}
    today = datetime.now(timezone.utc).date()
    if not days:
        return 0
    cursor = today if today.isoformat() in days else today.fromordinal(today.toordinal() - 1)
    streak = 0
    while cursor.isoformat() in days:
        streak += 1
        cursor = cursor.fromordinal(cursor.toordinal() - 1)
    return streak

def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(24)
    return session["_csrf"]

app.jinja_env.globals["csrf_token"] = csrf_token

@app.before_request
def protect_forms():
    if request.method == "POST":
        sent = request.form.get("_csrf", "")
        expected = session.get("_csrf", "")
        if not expected or not sent or not hmac.compare_digest(sent, expected):
            abort(400, description="El formulario venció o no es válido. Volvé a cargar la página e intentá otra vez.")

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    with get_db() as conn:
        row = conn.execute("SELECT id, username, created_at FROM users WHERE id = ?", (uid,)).fetchone()
    if not row:
        session.pop("user_id", None)
        return None
    return dict(row)

@app.context_processor
def inject_globals():
    return {"current_user": current_user()}

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Iniciá sesión para guardar tu progreso.", "info")
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

def course_by_slug(slug):
    return next((c for c in COURSES if c["slug"] == slug), None)

def progress_for(user_id):
    with get_db() as conn:
        rows = conn.execute("SELECT course_slug, lesson_number FROM progress WHERE user_id = ?", (user_id,)).fetchall()
    result = {}
    for row in rows:
        result.setdefault(row["course_slug"], set()).add(row["lesson_number"])
    return result

@app.route("/")
def home():
    with get_db() as conn:
        comments = conn.execute("SELECT * FROM comments ORDER BY id DESC LIMIT 12").fetchall()
        students = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0]
    return render_template("index.html", courses=COURSES, comments=comments, students=students, completed=completed)

@app.route("/aprender-programar")
def learn_programming():
    return render_template("learn.html", courses=COURSES)

@app.route("/curso/<slug>")
def course(slug):
    item = course_by_slug(slug)
    if not item:
        abort(404)
    done = set()
    if session.get("user_id"):
        done = progress_for(session["user_id"]).get(slug, set())
    notes = {}
    bookmarks = False
    if session.get("user_id"):
        with get_db() as conn:
            rows = conn.execute("SELECT lesson_number, note FROM lesson_notes WHERE user_id = ? AND course_slug = ?",
                                (session["user_id"], slug)).fetchall()
            notes = {row["lesson_number"]: row["note"] for row in rows}
            bookmarks = conn.execute("SELECT 1 FROM bookmarks WHERE user_id = ? AND course_slug = ?",
                                     (session["user_id"], slug)).fetchone() is not None
    return render_template("course.html", course=item, done=done, notes=notes,
                           bookmarked=bookmarks, quiz=course_quiz(item))

@app.post("/curso/<slug>/completar/<int:lesson_number>")
@login_required
def complete_lesson(slug, lesson_number):
    item = course_by_slug(slug)
    if not item or lesson_number < 1 or lesson_number > len(item["lessons"]):
        abort(404)
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO progress (user_id, course_slug, lesson_number) VALUES (?, ?, ?)",
                     (session["user_id"], slug, lesson_number))
        mark_study_day(conn, session["user_id"])
    flash("¡Lección marcada como completada! Sumaste progreso.", "success")
    return redirect(url_for("course", slug=slug) + "#leccion-" + str(lesson_number))


@app.post("/curso/<slug>/guardar")
@login_required
def toggle_bookmark(slug):
    item = course_by_slug(slug)
    if not item:
        abort(404)
    with get_db() as conn:
        exists = conn.execute("SELECT 1 FROM bookmarks WHERE user_id = ? AND course_slug = ?",
                              (session["user_id"], slug)).fetchone()
        if exists:
            conn.execute("DELETE FROM bookmarks WHERE user_id = ? AND course_slug = ?",
                         (session["user_id"], slug))
            flash("Curso quitado de tus guardados.", "info")
        else:
            conn.execute("INSERT OR IGNORE INTO bookmarks (user_id, course_slug) VALUES (?, ?)",
                         (session["user_id"], slug))
            flash("Curso guardado en tu lista.", "success")
    return redirect(url_for("course", slug=slug))

@app.post("/curso/<slug>/apunte/<int:lesson_number>")
@login_required
def save_note(slug, lesson_number):
    item = course_by_slug(slug)
    if not item or lesson_number < 1 or lesson_number > len(item["lessons"]):
        abort(404)
    note = request.form.get("note", "").strip()
    if len(note) > 2000:
        flash("El apunte admite hasta 2000 caracteres.", "error")
    else:
        with get_db() as conn:
            conn.execute("""INSERT INTO lesson_notes (user_id, course_slug, lesson_number, note)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, course_slug, lesson_number)
                DO UPDATE SET note=excluded.note, updated_at=CURRENT_TIMESTAMP""",
                (session["user_id"], slug, lesson_number, note))
            mark_study_day(conn, session["user_id"])
        flash("Tu apunte quedó guardado.", "success")
    return redirect(url_for("course", slug=slug) + "#leccion-" + str(lesson_number))

@app.post("/curso/<slug>/evaluar")
@login_required
def submit_quiz(slug):
    item = course_by_slug(slug)
    if not item:
        abort(404)
    questions = course_quiz(item)
    score = sum(1 for i, question in enumerate(questions)
                if request.form.get("q" + str(i)) == str(question["answer"]))
    total = len(questions)
    with get_db() as conn:
        previous = conn.execute("SELECT score FROM quiz_attempts WHERE user_id = ? AND course_slug = ?",
                                (session["user_id"], slug)).fetchone()
        first_pass = previous is None or previous["score"] < 2
        conn.execute("""INSERT INTO quiz_attempts (user_id, course_slug, score, total)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, course_slug)
            DO UPDATE SET score=MAX(score, excluded.score), total=excluded.total,
                          completed_at=CURRENT_TIMESTAMP""",
            (session["user_id"], slug, score, total))
        if score >= 2:
            mark_study_day(conn, session["user_id"])
    if score >= 2 and first_pass:
        flash("¡Evaluación aprobada! "+str(score)+"/"+str(total)+" respuestas correctas. Desbloqueaste 10 XP.", "success")
    elif score >= 2:
        flash("¡Evaluación aprobada! "+str(score)+"/"+str(total)+" respuestas correctas. Tu mejor resultado quedó guardado.", "success")
    else:
        flash("Obtuviste "+str(score)+"/"+str(total)+". Repasá las clases e intentá otra vez.", "info")
    return redirect(url_for("course", slug=slug) + "#evaluacion")

@app.route("/registro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(username) > 24 or not username.replace("_", "").isalnum():
            flash("El usuario debe tener entre 3 y 24 caracteres: letras, números o guion bajo.", "error")
        elif len(password) < 10:
            flash("La contraseña debe tener al menos 10 caracteres.", "error")
        else:
            try:
                with get_db() as conn:
                    cur = conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                                       (username, generate_password_hash(password)))
                    session.clear()
                    session["user_id"] = cur.lastrowid
                    csrf_token()
                flash("¡Cuenta creada! Ya podés guardar tu progreso.", "success")
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("Ese nombre de usuario ya está en uso.", "error")
    return render_template("auth.html", mode="register")

@app.route("/ingresar", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            csrf_token()
            flash("¡Qué bueno verte de nuevo!", "success")
            next_url = request.args.get("next", "")
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("auth.html", mode="login")

@app.route("/salir")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/mi-aprendizaje")
@login_required
def dashboard():
    user = current_user()
    progress = progress_for(user["id"])
    completed_count = sum(len(v) for v in progress.values())
    total_lessons = sum(len(c["lessons"]) for c in COURSES)
    with get_db() as conn:
        challenges = conn.execute("SELECT COUNT(*) FROM challenge_entries WHERE user_id = ?", (user["id"],)).fetchone()[0]
        quiz_passed = conn.execute("SELECT COUNT(*) FROM quiz_attempts WHERE user_id = ? AND score >= 2", (user["id"],)).fetchone()[0]
        saved_courses = conn.execute("SELECT course_slug FROM bookmarks WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)).fetchall()
        recent_notes = conn.execute("SELECT course_slug, lesson_number, updated_at FROM lesson_notes WHERE user_id = ? ORDER BY updated_at DESC LIMIT 5", (user["id"],)).fetchall()
        streak = calculate_streak(conn, user["id"])
    xp = completed_count * 25 + challenges * 20 + quiz_passed * 10
    badges = []
    if completed_count >= 1: badges.append("Primer paso")
    if completed_count >= 4: badges.append("Cuatro lecciones")
    if completed_count >= 10: badges.append("Constancia")
    if challenges >= 1: badges.append("Primer desafío")
    return render_template("dashboard.html", user=user, progress=progress, completed_count=completed_count,
                           total_lessons=total_lessons, xp=xp, badges=badges, challenges=challenges, courses=COURSES,
                           quiz_passed=quiz_passed, saved_courses=saved_courses, recent_notes=recent_notes, streak=streak)

@app.route("/certificado/<slug>")
@login_required
def certificate(slug):
    item = course_by_slug(slug)
    if not item:
        abort(404)
    done = progress_for(session["user_id"]).get(slug, set())
    if len(done) < len(item["lessons"]):
        flash("Completá todas las lecciones para habilitar el certificado.", "info")
        return redirect(url_for("course", slug=slug))
    return render_template("certificate.html", course=item, user=current_user(), date=datetime.now(timezone.utc).strftime("%d/%m/%Y"))

@app.route("/laboratorio")
def laboratory():
    return render_template("laboratory.html")

@app.route("/herramientas")
def tools_page():
    return render_template("tools.html")

@app.route("/proyectos")
def projects():
    project_list = [
        ("Tarjeta personal","HTML + CSS","Una presentación con foto, descripción y enlaces.","🪪","Principiante"),
        ("Landing de restaurante","HTML + CSS + responsive","Una portada, menú, horarios y contacto.","🍽️","Principiante"),
        ("Calculadora","JavaScript","Operaciones básicas, validación y botones.","🧮","Inicial"),
        ("Lista de tareas","JavaScript + localStorage","Agregar, completar y borrar tareas.","✅","Inicial"),
        ("Blog con Flask","Python + Flask + SQLite","Publicar entradas y mostrarlas desde una base de datos.","✍️","Intermedio"),
        ("Panel de usuarios","Flask + SQL + seguridad","Registro, inicio de sesión y una zona privada.","🔐","Intermedio"),
        ("App del clima","API + JavaScript","Consultar datos meteorológicos desde un servicio externo.","🌦️","Intermedio"),
        ("Portfolio final","HTML + CSS + JavaScript","Mostrar tus proyectos y explicar lo que aprendiste.","🏆","Proyecto final"),
    ]
    return render_template("projects.html", projects=project_list)

@app.route("/retos", methods=["GET", "POST"])
def challenges():
    challenge = {"title":"Tu tarjeta de presentación","description":"Creá una tarjeta HTML con tu nombre, una breve presentación y un enlace. Aplicale al menos tres reglas CSS.","hint":"Usá una etiqueta h1, un párrafo, un enlace y una clase CSS para la tarjeta."}
    with get_db() as conn:
        saved = conn.execute("SELECT key, value FROM site_settings WHERE key IN ('challenge_title','challenge_description','challenge_hint')").fetchall()
    for row in saved:
        field = {"challenge_title":"title","challenge_description":"description","challenge_hint":"hint"}[row["key"]]
        challenge[field] = row["value"]
    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip()
        answer = request.form.get("answer", "").strip()
        if len(nickname) < 2 or len(nickname) > 24 or len(answer) < 10 or len(answer) > 800:
            flash("Completá un apodo y una respuesta de entre 10 y 800 caracteres.", "error")
        else:
            user_id = session.get("user_id")
            with get_db() as conn:
                conn.execute("INSERT INTO challenge_entries (user_id, nickname, answer) VALUES (?, ?, ?)",
                             (user_id, nickname, answer))
                if user_id:
                    mark_study_day(conn, user_id)
            flash("¡Desafío enviado! Sumaste 20 XP si tenés una cuenta.", "success")
            return redirect(url_for("challenges"))
    with get_db() as conn:
        entries = conn.execute("SELECT nickname, answer, created_at FROM challenge_entries ORDER BY id DESC LIMIT 8").fetchall()
    return render_template("challenges.html", challenge=challenge, entries=entries)

@app.route("/ranking")
def ranking():
    with get_db() as conn:
        rows = conn.execute("""
          SELECT u.username,
          (SELECT COUNT(*) FROM progress p WHERE p.user_id=u.id)*25 +
          (SELECT COUNT(*) FROM challenge_entries c WHERE c.user_id=u.id)*20 +
          (SELECT COUNT(*) FROM quiz_attempts q WHERE q.user_id=u.id AND q.score >= 2)*10 AS xp
          FROM users u ORDER BY xp DESC, u.username ASC LIMIT 20
        """).fetchall()
    return render_template("ranking.html", ranking=rows)

@app.post("/comentarios")
def add_comment():
    message = request.form.get("message", "").strip()
    if not message:
        flash("Escribí una pregunta o comentario antes de publicar.", "error")
    elif len(message) > 600:
        flash("El mensaje es demasiado largo (máximo 600 caracteres).", "error")
    else:
        with get_db() as conn:
            conn.execute("INSERT INTO comments (message) VALUES (?)", (message,))
        flash("¡Tu mensaje se publicó correctamente!", "success")
    return redirect(url_for("home") + "#comunidad")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = os.environ.get("ADMIN_USER", "")
        password = os.environ.get("ADMIN_PASSWORD", "")
        entered_user = request.form.get("username", "")
        entered_password = request.form.get("password", "")
        if username and password and hmac.compare_digest(entered_user, username) and hmac.compare_digest(entered_password, password):
            session.clear()
            session["admin"] = True
            csrf_token()
            return redirect(url_for("admin"))
        flash("Acceso no configurado o credenciales incorrectas. Revisá ADMIN_USER y ADMIN_PASSWORD en Render.", "error")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin():
    with get_db() as conn:
        comments = conn.execute("SELECT * FROM comments ORDER BY id DESC").fetchall()
        users = conn.execute("SELECT id, username, created_at FROM users ORDER BY id DESC LIMIT 50").fetchall()
        submissions = conn.execute("SELECT id, nickname, answer, created_at FROM challenge_entries ORDER BY id DESC LIMIT 30").fetchall()
        progress_count = conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0]
        notes_count = conn.execute("SELECT COUNT(*) FROM lesson_notes").fetchone()[0]
        quiz_count = conn.execute("SELECT COUNT(*) FROM quiz_attempts WHERE score >= 2").fetchone()[0]
        bookmark_count = conn.execute("SELECT COUNT(*) FROM bookmarks").fetchone()[0]
        project_posts = conn.execute("""SELECT p.id, p.title, p.description, p.technologies, p.project_url,
            p.created_at, u.username FROM project_posts p JOIN users u ON u.id=p.user_id
            ORDER BY p.id DESC LIMIT 40""").fetchall()
        saved = conn.execute("SELECT key, value FROM site_settings WHERE key IN ('challenge_title','challenge_description','challenge_hint')").fetchall()
    challenge = {"title":"Tu tarjeta de presentación","description":"Creá una tarjeta HTML con tu nombre, una breve presentación y un enlace. Aplicale al menos tres reglas CSS.","hint":"Usá una etiqueta h1, un párrafo, un enlace y una clase CSS para la tarjeta."}
    for row in saved:
        field = {"challenge_title":"title","challenge_description":"description","challenge_hint":"hint"}[row["key"]]
        challenge[field] = row["value"]
    return render_template("admin.html", comments=comments, users=users, submissions=submissions,
                           courses=COURSES, progress_count=progress_count, challenge=challenge,
                           notes_count=notes_count, quiz_count=quiz_count, bookmark_count=bookmark_count, project_posts=project_posts)


@app.post("/admin/reto")
@admin_required
def update_challenge():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    hint = request.form.get("hint", "").strip()
    if not title or len(title) > 100 or not description or len(description) > 500 or not hint or len(hint) > 300:
        flash("Completá el título, la descripción y la pista respetando los límites indicados.", "error")
    else:
        with get_db() as conn:
            conn.executemany("INSERT INTO site_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                             [("challenge_title", title), ("challenge_description", description), ("challenge_hint", hint)])
            conn.execute("""INSERT INTO notifications (user_id, title, body)
                SELECT id, ?, ? FROM users""", ("Nuevo reto semanal", title + " · " + description[:180]))
        flash("¡El desafío semanal se actualizó!", "success")
    return redirect(url_for("admin"))


@app.post("/admin/reto/<int:entry_id>/eliminar")
@admin_required
def delete_challenge_entry(entry_id):
    with get_db() as conn:
        conn.execute("DELETE FROM challenge_entries WHERE id = ?", (entry_id,))
    flash("Entrega del reto eliminada.", "success")
    return redirect(url_for("admin"))

@app.post("/admin/proyecto/<int:post_id>/eliminar")
@admin_required
def delete_project_post(post_id):
    with get_db() as conn:
        conn.execute("DELETE FROM project_posts WHERE id = ?", (post_id,))
    flash("Proyecto retirado de la comunidad.", "success")
    return redirect(url_for("admin"))

@app.post("/admin/comentario/<int:comment_id>/eliminar")
@admin_required
def delete_comment(comment_id):
    with get_db() as conn:
        conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    flash("Comentario eliminado.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/mi-perfil", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()[:40]
        bio = request.form.get("bio", "").strip()[:240]
        website = request.form.get("website", "").strip()[:200]
        stack = request.form.get("favorite_stack", "").strip()[:80]
        if website and not (website.startswith("https://") or website.startswith("http://")):
            flash("El enlace debe comenzar con https:// o http://.", "error")
        else:
            with get_db() as conn:
                conn.execute("""INSERT INTO user_profiles (user_id, display_name, bio, website, favorite_stack)
                    VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET
                    display_name=excluded.display_name, bio=excluded.bio, website=excluded.website,
                    favorite_stack=excluded.favorite_stack, updated_at=CURRENT_TIMESTAMP""",
                    (user["id"], display_name, bio, website, stack))
            flash("Tu perfil quedó actualizado.", "success")
            return redirect(url_for("profile"))
    with get_db() as conn:
        profile_row = conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user["id"],)).fetchone()
        posts = conn.execute("SELECT * FROM project_posts WHERE user_id = ? ORDER BY id DESC LIMIT 10", (user["id"],)).fetchall()
        unread = conn.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND read_at IS NULL", (user["id"],)).fetchone()[0]
    return render_template("profile.html", user=user, profile=profile_row, posts=posts, unread=unread)

@app.route("/comunidad/proyectos", methods=["GET", "POST"])
def community_projects():
    if request.method == "POST":
        if not session.get("user_id"):
            flash("Iniciá sesión para publicar tu proyecto.", "info")
            return redirect(url_for("login"))
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        technologies = request.form.get("technologies", "").strip()
        project_url = request.form.get("project_url", "").strip()
        if not (3 <= len(title) <= 70 and 20 <= len(description) <= 500 and 2 <= len(technologies) <= 100):
            flash("Revisá el título, la descripción y las tecnologías.", "error")
        elif project_url and not (project_url.startswith("https://") or project_url.startswith("http://")):
            flash("El enlace debe comenzar con https:// o http://.", "error")
        else:
            with get_db() as conn:
                conn.execute("INSERT INTO project_posts (user_id, title, description, technologies, project_url) VALUES (?, ?, ?, ?, ?)",
                             (session["user_id"], title, description, technologies, project_url))
                mark_study_day(conn, session["user_id"])
            flash("¡Tu proyecto se publicó en la comunidad!", "success")
            return redirect(url_for("community_projects"))
    with get_db() as conn:
        posts = conn.execute("""SELECT p.*, u.username,
            COALESCE(NULLIF(pr.display_name, ''), u.username) AS author_name
            FROM project_posts p JOIN users u ON u.id=p.user_id
            LEFT JOIN user_profiles pr ON pr.user_id=u.id
            ORDER BY p.id DESC LIMIT 60""").fetchall()
    return render_template("community_projects.html", posts=posts)

@app.route("/tutor", methods=["GET", "POST"])
@login_required
def tutor():
    answer = None
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if len(question) < 5 or len(question) > 1200:
            flash("Escribí una pregunta de entre 5 y 1200 caracteres.", "error")
        else:
            api_key = os.environ.get("AI_API_KEY", "").strip()
            if not api_key:
                flash("El tutor está preparado, pero falta configurar AI_API_KEY en Render para activarlo.", "info")
            else:
                import json
                import urllib.request
                endpoint = os.environ.get("AI_API_URL", "https://api.openai.com/v1/chat/completions")
                model = os.environ.get("AI_MODEL", "gpt-4o-mini")
                payload = {"model": model, "messages": [
                    {"role": "system", "content": "Sos un tutor paciente de programación en español. Enseñá paso a paso con ejemplos pequeños. Nunca solicites contraseñas, tokens ni datos personales."},
                    {"role": "user", "content": question}
                ], "temperature": 0.4}
                req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                    headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}, method="POST")
                try:
                    with urllib.request.urlopen(req, timeout=35) as response:
                        data = json.loads(response.read().decode("utf-8"))
                    answer = data["choices"][0]["message"]["content"]
                except Exception:
                    flash("No se pudo conectar con el tutor. Revisá la configuración de IA en Render.", "error")
    return render_template("tutor.html", answer=answer, question=question)

@app.route("/notificaciones")
@login_required
def notifications():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 40",
                            (session["user_id"],)).fetchall()
        conn.execute("UPDATE notifications SET read_at=CURRENT_TIMESTAMP WHERE user_id = ? AND read_at IS NULL",
                     (session["user_id"],))
    return render_template("notifications.html", notifications=rows)


# ── EXPANSIÓN XXL: biblioteca práctica y plan personal ─────────────────────
def init_xxl_tables():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS learning_resources (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          category TEXT NOT NULL,
          level TEXT NOT NULL DEFAULT 'Inicial',
          summary TEXT NOT NULL,
          content TEXT NOT NULL,
          code TEXT NOT NULL DEFAULT '',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS resource_progress (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          resource_id INTEGER NOT NULL REFERENCES learning_resources(id) ON DELETE CASCADE,
          completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id, resource_id)
        );
        CREATE TABLE IF NOT EXISTS study_goals (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          title TEXT NOT NULL,
          target_date TEXT NOT NULL DEFAULT '',
          done INTEGER NOT NULL DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        count = conn.execute("SELECT COUNT(*) FROM learning_resources").fetchone()[0]
        if count == 0:
            seeds = [
              ("Tu primera página HTML","HTML","Principiante","Construí una página semántica desde cero.","Creá un documento con título, encabezado, contenido principal, una sección y un pie. Probalo en el navegador y verificá que tenga lang='es' y meta charset.","<!doctype html>\n<html lang='es'>\n<head><meta charset='utf-8'><title>Mi primera web</title></head>\n<body>\n  <header><h1>Mi primera web</h1></header>\n  <main><p>Estoy aprendiendo.</p></main>\n  <footer>Hecho por mí</footer>\n</body>\n</html>"),
              ("Tarjeta de perfil con CSS","CSS","Principiante","Diseñá una tarjeta adaptable con Flexbox.","Usá una clase principal, padding, bordes redondeados, sombra suave y un ancho máximo. En pantallas pequeñas, ocupá casi todo el ancho disponible.",".tarjeta {\n  max-width: 420px;\n  margin: 2rem auto;\n  padding: 1.5rem;\n  border-radius: 18px;\n  background: #171d2b;\n  color: white;\n  display: flex;\n  flex-direction: column;\n  gap: 1rem;\n}"),
              ("Contador interactivo","JavaScript","Inicial","Conectá un botón con una variable y el DOM.","Mostrá un número en pantalla. Al presionar sumar, incrementalo; al presionar reiniciar, volvé a cero. Usá textContent para actualizar el valor.","let contador = 0;\nconst salida = document.querySelector('#valor');\ndocument.querySelector('#sumar').addEventListener('click', () => {\n  contador++;\n  salida.textContent = contador;\n});"),
              ("Formulario seguro en Flask","Python / Flask","Intermedio","Recibí y validá datos desde un formulario.","Validá los campos en el servidor, limitá la longitud y nunca concatenes datos del usuario en consultas SQL. Para contraseñas, usá funciones de hashing.","from flask import Flask, request, render_template\napp = Flask(__name__)\n\n@app.post('/contacto')\ndef contacto():\n    nombre = request.form.get('nombre', '').strip()[:60]\n    if not nombre:\n        return 'Falta el nombre', 400\n    return '¡Gracias, ' + nombre + '!'"),
              ("API y JSON","Backend","Intermedio","Entendé cómo una aplicación intercambia datos.","Una API expone endpoints. JSON representa datos estructurados. Revisá el código HTTP y manejá errores de red antes de usar la respuesta.","fetch('/api/ejemplo')\n  .then(respuesta => {\n    if (!respuesta.ok) throw new Error('Error HTTP');\n    return respuesta.json();\n  })\n  .then(datos => console.log(datos))\n  .catch(error => console.error(error));"),
              ("Publicá tu proyecto en GitHub","Herramientas","Inicial","Prepará un repositorio claro y compartible.","Incluí README, instrucciones de instalación y capturas propias. Nunca subas .env, contraseñas, tokens ni bases de datos con información privada.","git init\ngit add .\ngit commit -m \"Primer proyecto\"\ngit branch -M main\ngit remote add origin URL_DEL_REPO\ngit push -u origin main")
            ]
            conn.executemany("INSERT INTO learning_resources(title,category,level,summary,content,code) VALUES(?,?,?,?,?,?)", seeds)

@app.route("/biblioteca")
def resource_library():
    category = request.args.get("categoria", "").strip()[:40]
    with get_db() as conn:
        if category:
            resources = conn.execute("SELECT * FROM learning_resources WHERE category=? ORDER BY id DESC", (category,)).fetchall()
        else:
            resources = conn.execute("SELECT * FROM learning_resources ORDER BY id DESC").fetchall()
        categories = conn.execute("SELECT DISTINCT category FROM learning_resources ORDER BY category").fetchall()
        done = set()
        if session.get("user_id"):
            done = {r["resource_id"] for r in conn.execute("SELECT resource_id FROM resource_progress WHERE user_id=?", (session["user_id"],)).fetchall()}
    return render_template("resource_library.html", resources=resources, categories=categories, selected=category, done=done)

@app.route("/biblioteca/<int:resource_id>", methods=["GET", "POST"])
def resource_detail(resource_id):
    with get_db() as conn:
        resource = conn.execute("SELECT * FROM learning_resources WHERE id=?", (resource_id,)).fetchone()
        if not resource:
            abort(404)
        completed = False
        if session.get("user_id"):
            completed = conn.execute("SELECT 1 FROM resource_progress WHERE user_id=? AND resource_id=?", (session["user_id"], resource_id)).fetchone() is not None
        if request.method == "POST":
            if not session.get("user_id"):
                flash("Iniciá sesión para guardar tu avance.", "info")
                return redirect(url_for("login"))
            conn.execute("INSERT OR IGNORE INTO resource_progress(user_id,resource_id) VALUES(?,?)", (session["user_id"], resource_id))
            flash("¡Recurso completado! Tu avance quedó guardado.", "success")
            return redirect(url_for("resource_detail", resource_id=resource_id))
    return render_template("resource_detail.html", resource=resource, completed=completed)

@app.route("/mi-plan", methods=["GET", "POST"])
@login_required
def study_plan():
    uid = session["user_id"]
    with get_db() as conn:
        if request.method == "POST":
            title = request.form.get("title", "").strip()[:100]
            target_date = request.form.get("target_date", "").strip()[:10]
            if len(title) < 3:
                flash("La meta debe tener al menos 3 caracteres.", "error")
            else:
                conn.execute("INSERT INTO study_goals(user_id,title,target_date) VALUES(?,?,?)", (uid,title,target_date))
                flash("Meta agregada a tu plan.", "success")
            return redirect(url_for("study_plan"))
        goals = conn.execute("SELECT * FROM study_goals WHERE user_id=? ORDER BY done, id DESC", (uid,)).fetchall()
        stats = conn.execute("SELECT COUNT(*) total, SUM(done) done FROM study_goals WHERE user_id=?", (uid,)).fetchone()
        resource_done = conn.execute("SELECT COUNT(*) FROM resource_progress WHERE user_id=?", (uid,)).fetchone()[0]
    return render_template("study_plan.html", goals=goals, stats=stats, resource_done=resource_done)

@app.post("/mi-plan/<int:goal_id>/estado")
@login_required
def toggle_study_goal(goal_id):
    with get_db() as conn:
        conn.execute("UPDATE study_goals SET done=CASE WHEN done=0 THEN 1 ELSE 0 END WHERE id=? AND user_id=?", (goal_id,session["user_id"]))
    return redirect(url_for("study_plan"))

@app.post("/mi-plan/<int:goal_id>/eliminar")
@login_required
def delete_study_goal(goal_id):
    with get_db() as conn:
        conn.execute("DELETE FROM study_goals WHERE id=? AND user_id=?", (goal_id,session["user_id"]))
    flash("Meta eliminada.", "info")
    return redirect(url_for("study_plan"))

@app.route("/admin/biblioteca", methods=["GET", "POST"])
@admin_required
def admin_library():
    with get_db() as conn:
        if request.method == "POST":
            title = request.form.get("title", "").strip()[:100]
            category = request.form.get("category", "").strip()[:40]
            level = request.form.get("level", "Inicial").strip()[:30]
            summary = request.form.get("summary", "").strip()[:240]
            content = request.form.get("content", "").strip()[:5000]
            code = request.form.get("code", "").strip()[:8000]
            if len(title) < 3 or len(category) < 2 or len(content) < 10:
                flash("Completá título, categoría y contenido.", "error")
            else:
                conn.execute("INSERT INTO learning_resources(title,category,level,summary,content,code) VALUES(?,?,?,?,?,?)", (title,category,level,summary,content,code))
                flash("Recurso publicado en la biblioteca.", "success")
            return redirect(url_for("admin_library"))
        resources = conn.execute("SELECT * FROM learning_resources ORDER BY id DESC").fetchall()
    return render_template("admin_library.html", resources=resources)

@app.post("/admin/biblioteca/<int:resource_id>/eliminar")
@admin_required
def admin_delete_resource(resource_id):
    with get_db() as conn:
        conn.execute("DELETE FROM learning_resources WHERE id=?", (resource_id,))
    flash("Recurso eliminado.", "info")
    return redirect(url_for("admin_library"))

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", code=400, message=getattr(error, "description", "Solicitud no válida.")), 400

init_db()
init_xxl_tables()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
