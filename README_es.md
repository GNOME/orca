# Orca v51.rc

<!-- hy-mt2-i18n:start -->
[English](./README.md) | [中文](./README_zh-CN.md) | [日本語](./README_ja.md) | **Español**
<!-- hy-mt2-i18n:end -->


[TOC]

## Atención, desarrolladores de aplicaciones

Si es un desarrollador de aplicaciones que desea hacer que su aplicación funcione con Orca, consulte la
[README para desarrolladores de aplicaciones](docs/application-developers.md).

## Introducción

Orca es un lector de pantalla gratuito, de código abierto, flexible y ampliable que permite acceder al escritorio gráfico mediante combinaciones personalizables por el usuario de voz y/o braille.

Orca funciona con aplicaciones y kits de herramientas que soportan la interfaz de proveedor de servicios de tecnología de asistencia (AT-SPI), que es la infraestructura principal de tecnología de asistencia para Solaris y Linux. Aunque Orca forma parte del Proyecto GNOME, puede utilizarse en cualquier entorno de escritorio accesible.

Consulte <https://orca.gnome.org> para obtener información detallada sobre Orca, incluyendo cómo ejecutarlo, cómo comunicarse con la comunidad de usuarios de Orca y dónde registrar errores y solicitudes de nuevas funcionalidades.

## Dependencias

Orca cuenta con las siguientes dependencias:

* meson: El sistema de compilación utilizado por Orca  
* Python 3: Plataforma Python  
* pygobject-3.0: Vinculaciones de Python para la biblioteca GObject  
* gtk+-3.0: Kit de herramientas GTK+  
* at-spi2-core 2.58.6 o superior, compilado con soporte para Python  
* gpaste: Gestor de portapapeles para sesiones Wayland que no sean de KDE (opcional). Es necesario para las comandos de Orca que copian o añaden elementos al portapapeles. En sesiones de KDE, Orca intenta utilizar Klipper.  
* python3-babel: Soporte de Babel para mostrar nombres de idiomas localizados (altamente recomendado). Sin Babel, los idiomas en la interfaz de Orca se mostrarán como códigos en lugar de nombres.  
* python3-brlapi: Soporte para BrlAPI (<https://mielke.cc/brltty/>) para braille (opcional)  
* python3-dasbus: Soporte para Dasbus (<https://dasbus.readthedocs.io/>) para control remoto de Orca  
* python3-louis: Soporte para braille contrahído mediante Liblouis (<https://liblouis.io/>) (opcional)  
* python3-psutil: Herramientas para procesos y sistema (opcional)  
* python3-setproctitle: Biblioteca de Python para establecer el título del proceso (altamente recomendado). Esto hace que `pidof orca` funcione. También actualiza `/proc/<PID de Orca>/cmdline` para que contenga “orca”. Los navegadores basados en Chromium verifican este valor para habilitar automáticamente el soporte completo de accesibilidad, sin necesidad de usar `--force-rendereer-accessibility`.  
* python3-speechd: Vinculaciones de Python para Speech Dispatcher (opcional)  
* gstreamer-1.0: GStreamer: marco de trabajo para medios en streaming (opcional)  
* cargo: Se utiliza para compilar MathCAT (<https://daisy.github.io/MathCAT/>) con soporte para MathML. MathCAT se compila por defecto, por lo que se necesita cargo a menos que se excluya pasando `-Dmathcat=false` a `meson setup`.  
* libwnck3: Se utiliza para la revisión con el ratón en X11 (opcional, obsoleto)

Se recomienda encarecidamente que también disponga de las versiones estables más recientes de AT-SPI2 y ATK para la versión GNOME 50.x.

## Nota para usuarios de Braille

Puede determinar si están instaladas las vinculaciones en Python para BrlAPI ejecutando el siguiente comando:

```sh
python -c "import brlapi"
```

Si aparece un error, significa que las bibliotecas en Python para BrlAPI no están instaladas.

## Compilación e instalación de Orca

Si desea compilar Orca en un directorio llamado `_build` e instalarlo en la ubicación predeterminada de su distribución (por ejemplo, `/usr/local`):

```sh
meson setup _build
meson compile -C _build
meson install -C _build
```

El instalador le pedirá permisos de `sudo` si es necesario.

Para especificar una ubicación de instalación alternativa, utilice `-D prefix=` durante el proceso de configuración
(por ejemplo, `meson setup -D prefix=$HOME/orca-test _build`).

Para volver a compilar, elimine el directorio de compilación que creó anteriormente (por ejemplo, `_build`) o agregue el parámetro `--reconfigure` al final de su comando `meson setup` existente.

Para desinstalarlo, vaya al directorio de compilación que creó y utilice `ninja uninstall`, o `sudo ninja uninstall` si instaló Orca con permisos `sudo`. Tenga en cuenta que esto no eliminará los archivos de bytecode en `__pycache__`. Consulte este [problema de Meson](https://github.com/mesonbuild/meson/issues/12798).

## Ejecutar Orca

Si desea modificar las preferencias de Orca, puede presionar “Insert+espacio” mientras el programa está en ejecución.

Para obtener ayuda mientras se ejecuta Orca, presione “Insert+H”. Esto activará el “modo de aprendizaje”, que proporciona una descripción hablada y en braille de lo que harán las distintas acciones de los dispositivos de entrada por teclado y braille. Para salir del modo de aprendizaje, presione “Escape”. Finalmente, el cuadro de diálogo de preferencias contiene una pestaña “Atajos de teclado” que enumera los atajos de Orca.

Para obtener más información, consulte la documentación de Orca, disponible tanto dentro de Orca como en <https://gnome.pages.gitlab.gnome.org/orca/help>.

## Las scripts y características de Orca

Los scripts de Orca permiten acceder a aplicaciones y kits de herramientas al responder a eventos accesibles. Por ejemplo, cuando cambia el foco en una aplicación, esta emitirá un evento accesible, `object:state-changed:focused`, el cual será luego manejado por el script asociado a dicha aplicación o kit de herramientas.

Si cuenta con una aplicación o kit de herramientas accesible, pero con escasa compatibilidad por parte de Orca, escribir un script personalizado para dicha aplicación podría ser la solución adecuada. (La solución correcta podría ser, en su lugar, corregir un error en Orca y/o en la aplicación.) Para ver ejemplos de scripts, consulte la carpeta `src/orca/scripts` del árbol de fuentes.

Los scripts también pueden importar funcionalidades, pero estas últimas no se encuentran dentro del script; residen en navegadores, presentadores y otros módulos similares.

## Control remoto (interfaz D-Bus)

Orca ofrece una interfaz D-Bus que permite a las aplicaciones externas controlar de forma remota las funcionalidades de Orca y mostrar mensajes a los usuarios. Para obtener instrucciones detalladas de uso, ejemplos y documentación de la API, consulte [remote-controller.md](docs/remote-controller.md).

## Soporte para GSettings

A partir de Orca v50, este utiliza GSettings para su configuración. Se puede encontrar una lista de los esquemas, claves, valores predeterminados y enumeraciones de Orca en [gsettings-schemas.md](docs/gsettings-schemas.md).

## Soporte para síntesis de voz Spiel

Por defecto, Orca utiliza speech-dispatcher para su soporte de síntesis de voz. También existe un soporte básico para [Spiel](https://github.com/project-spiel), que permite elegir voces entre varios sintetizadores, incluyendo actualmente eSpeak y Piper.

Para probar Spiel, configure Orca para que se construya a partir del código fuente más reciente. Una vez compilado, se utilizará `meson devenv` para ejecutar Orca.

```sh
meson setup --force-fallback-for=spiel -Dspiel=true _build
meson compile --clean -C _build
meson install -C _build
```

Si ya cuenta con un directorio de compilación, no olvide utilizar `--reconfigure`. Si tiene problemas después de una actualización, es posible que necesite volver a compilar e instalar:

```sh
meson subprojects purge --confirm
meson setup --reconfigure --force-fallback-for=spiel -Dspiel=true _build 
meson compile --clean -C _build
meson install -C _build

# Asegúrese de que se reinicien todos los proveedores antiguos de Spiel
flatpak kill ai.piper.Speech.Provider
flatpak kill org.espeak.Speech.Provider
```

Luego, instale el Flatpak para uno o más proveedores de voz (es decir, piper o speak) ejecutando los comandos que se encuentran en la [documentación de Spiel](https://project-spiel.org/install.html).

Para cambiar de Speech Dispatcher a Spiel, utilice `orca --replace --speech-system=spiel`. Se recomienda encarecidamente usar esta opción ya que la compatibilidad de Orca con Spiel es experimental. Si desea utilizar Spiel por defecto, puede seleccionarlo en el cuadro de diálogo de Preferencias de Orca. Para volver a cambiar a Speech Dispatcher, utilice `orca --replace --speech-system=speechdispatcherfactory`.

# Restricciones estrictas
1. **Bloqueo estructural**: Mantener absolutamente intacta la estructura original de Markdown, los sangrados, los niveles de título, las tablas, los enlaces, las URL, las insignias, los bloques de código y el código inline.
2. **Traducción selectiva**: Solo traducir el contenido de lenguaje natural visible para el usuario.
3. **Prohibición de modificaciones**: Está **estrictamente prohibido** traducir o modificar etiquetas de código, nombres de claves, placeholders de variables (como {{var}}, ${var}, %s, %d, etc.), ejemplos de comandos, rutas de archivos, nombres de proyectos, nombres de API, nombres de paquetes, nombres de modelos, identificadores y símbolos de código; a menos que ya se haya proporcionado una traducción correspondiente en la información de contexto.
4. La traducción de términos, estilos y nombres propios debe ser coherente con la información de contexto proporcionada.

### Compilación de Spiel desde el código fuente

Para usuarios avanzados, es posible compilar Spiel y los proveedores desde el código fuente. Si no está seguro, considere utilizar los Flatpaks disponibles y consulte la documentación de su distribución antes de continuar.

1. Construir e instalar Orca con Spiel

   Asegúrese de compilar Orca como se describió anteriormente, para que esté disponible la versión correcta de `libspeechprovider` al compilar un proveedor en el siguiente paso. Si ya compiló Orca con anterioridad, siga los pasos para actualizarlo y volver a compilarlo antes de continuar.

2. A continuación, construya e instale un proveedor

   ```sh
   # Clone el repositorio y luego seleccione un proveedor en la carpeta "providers/"
   git clone https://github.com/eeejay/spiel-demos.git
   cd spiel-demos/providers/espeak

   # Construya e instale
   meson setup _build
   meson compile -C _build
   meson install -C _build
   ```

Ahora inicie Orca siguiendo las [instrucciones](#spiel-text-to-speech-support) anteriores y los proveedores de Spiel que instaló se activarán automáticamente.
