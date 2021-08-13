# redes-xmpp
## Proyecto 1 
José Miguel Castañeda <br> Carnet:18161

<p>Esta aplicación funciona como cliente xmpp utilizando la librería de python slixmpp.</p>

### Requerimientos
<p>Para utilizar el cliente xmpp se recomienda tener una versión de python inferior a 3.7
<br>Ejecutar  el siguiente comando para instalar los paquetes que se utilizarán en la aplicación:</p>
<pre><code>python -m pip install -r requirements.txt</code></pre>

### Inicio
<p>Para iniciar la aplicación ejecutar el comando:</p>
<pre><code>python main.py</code></pre>

### Flujo de la aplicación
<p>La aplicación cuenta de un menu principal para manejar la sesión la cual tiene las siguientes opciones:</p>

1. Registrarse 
2. Iniciar sesión con una cuenta existente
3. Salir

<p>Luego de iniciar sesión o crear una cuenta se muestra un segundo menú con las siguientes opciones:</p>

1. Mostrar todos tus contactos y su estado
2. Agregar un usuario a tus contactos
3. Mostrar detalles de un contacto
4. Enviar un mensaje directo
5. Enviar un mensaje a un grupo
6. Definir mensaje de presencia
7. Cerrar Sesión
8. Eliminar mi usuario

<p>Las notificaciones de los mensajes recibidos se muestran luego de realizar cualquier acción en la aplicación.</p>