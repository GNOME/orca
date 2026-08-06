# Orca v51.rc 版本

<!-- hy-mt2-i18n:start -->
[English](./README.md) | **中文** | [日本語](./README_ja.md) | [Español](./README_es.md)
<!-- hy-mt2-i18n:end -->


[目录]

## 致应用程序开发者们

如果您是希望让自己的应用程序与 Orca 集成运行的应用开发者，请参阅
[应用开发者指南](docs/application-developers.md)。

## 简介

Orca是一款免费、开源、灵活且可扩展的屏幕阅读器，它通过用户可自定义的语音和/或盲文组合，帮助用户访问图形化桌面界面。

Orca 能与支持辅助技术服务提供者接口（AT-SPI）的应用程序及工具包配合使用，该接口是 Solaris 和 Linux 系统中的主要辅助技术基础设施。尽管 Orca 属于 GNOME 项目的一部分，但它可在任何无障碍桌面环境中使用。

如需了解关于 Orca 的详细信息，包括如何运行 Orca、如何与 Orca 用户社区交流，以及在哪里提交错误报告和功能需求，请访问 <https://orca.gnome.org>。

## 依赖项

Orca 的依赖项如下：

* meson：Orca所使用的构建系统  
* Python 3：Python平台  
* pygobject-3.0：GObject库的Python绑定  
* gtk+-3.0：GTK+工具包  
* at-spi2-core 2.58.6或更高版本，且需包含Python支持功能  
* gpaste：非KDE Wayland会话下的剪贴板管理工具（可选）。Orca中用于复制或追加内容到剪贴板的命令需要该工具；在KDE会话中，Orca会尝试使用Klipper。  
* python3-babel：用于显示本地化语言名称的Babel支持工具（强烈推荐）。若没有该工具，Orca界面中的语言将显示为代码而非名称。  
* python3-brlapi：用于盲文功能的BrlAPI（<https://mielke.cc/brltty/>）支持工具（可选）  
* python3-dasbus：用于远程控制Orca的Dasbus（<https://dasbus.readthedocs.io/>）支持工具  
* python3-louis：用于缩写盲文功能的Liblouis（<https://liblouis.io/>）支持工具（可选）  
* python3-psutil：进程与系统实用工具（可选）  
* python3-setproctitle：用于设置进程名称的Python库（强烈推荐）。该工具可让`pidof orca`命令正常运行，同时还会更新 `/proc/<Orca的进程ID>/cmdline` 文件，使其包含“orca”字样。基于Chromium的浏览器会检测这一信息，从而自动启用完整的无障碍支持，无需再使用`--force-rendereer-accessibility`参数。  
* python3-speechd：Speech Dispatcher的Python绑定（可选）  
* gstreamer-1.0：GStreamer——流媒体框架（可选）  
* cargo：用于构建MathCAT（<https://daisy.github.io/MathCAT/>），以实现MathML支持功能。MathCAT默认已被内置，因此除非在`meson setup`命令中通过`-Dmathcat=false`选项取消构建，否则就需要使用cargo。  
* libwnck3：用于X11环境下的鼠标校验功能（可选，已过时）

强烈建议您同时安装 GNOME 50.x 版本对应的最新稳定版 AT-SPI2 和 ATK。

## 盲文用户的注意事项

您可以通过运行以下命令来判断 BrlAPI 的 Python 绑定是否已安装：

```sh
python -c "import brlapi"
```

如果出现错误，说明尚未安装 BrlAPI 的 Python 绑定。

## 构建与安装 Orca

如果您希望在一个名为 `_build` 的目录中构建 Orca，并将其安装到您发行版的默认位置（例如 `/usr/local`）：

```sh
meson setup _build
meson compile -C _build
meson install -C _build
```

如果需要，安装程序会提示您授予 `sudo` 权限。

若要指定其他安装位置，可在设置时使用 `-D prefix=` 选项（例如：`meson setup -D prefix=$HOME/orca-test _build`）。

要重新构建，可以删除之前创建的构建目录（例如 `_build`），或者在现有的 `meson setup` 命令末尾添加 `--reconfigure` 参数。

如需卸载，可进入之前创建的构建目录，然后使用 `ninja uninstall` 命令，若是通过 `sudo` 权限安装的 Orca，则需使用 `sudo ninja uninstall`。请注意，此操作不会删除 `__pycache__` 目录中的字节码文件。相关问题可参见此 [meson 问题记录](https://github.com/mesonbuild/meson/issues/12798)。

## 运行 Orca

如果您想修改 Orca 的偏好设置，可以在其运行时按下“Insert+空格”键。

在运行 Orca 时需要帮助，可按下“Insert+H”键。这将启用“学习模式”，该模式会以语音和盲文形式说明各种键盘及盲文输入设备操作的功能。要退出学习模式，请按下“Escape”键。最后，偏好设置对话框中还有一个“键绑定”选项卡，列出了 Orca 的键盘绑定设置。

如需更多信息，请参阅可在 Orca 内部查看的 Orca 文档，以及地址为 <https://gnome.pages.gitlab.gnome.org/orca/help> 的相关资料。

## Orca 的脚本与功能

Orca 的脚本通过响应无障碍事件来实现对应用程序及工具包的访问。例如，当应用程序中的焦点发生变化时，该应用程序会发出一个无障碍事件 `object:state-changed:focused`，随后由与该应用程序或工具包关联的脚本来处理这一事件。

如果您的应用程序或工具套件具备无障碍功能，但 Orca 对其的支持不佳，那么为该应用程序编写自定义脚本可能是正确的解决方案。（当然，另一种正确的解决方案也可能是修复 Orca 和/或该应用程序中的漏洞。）如需查看脚本示例，请查阅源代码树中的 `src/orca/scripts` 目录。

脚本还可以导入功能模块，但这些功能本身并不存在于脚本内部，而是位于导航器、呈现器及其他类似模块中。

## 远程控制器（D-Bus 接口）

Orca 提供了一个 D-Bus 接口，允许外部应用程序远程控制 Orca 的功能并向用户显示消息。如需详细的用法说明、示例及 API 文档，请参阅 [remote-controller.md](docs/remote-controller.md)。

## GSettings 支持

从 Orca v50 版本开始，它便开始使用 GSettings 进行配置。Orca 的各种模式、键值、默认值以及枚举类型的列表可在 [gsettings-schemas.md](docs/gsettings-schemas.md) 中查看。

## Spiel 文本转语音支持

默认情况下，Orca 的文本转语音功能依赖于 speech-dispatcher。同时它也具备对 [Spiel](https://github.com/project-spiel) 的基础支持，该功能允许从多种合成语音引擎中选择语音，目前支持的包括 eSpeak 和 Piper。

要测试 Spiel，需将 Orca 配置为从最新源码进行构建。编译完成后，将使用 `meson devenv` 来运行 Orca。

```sh
meson setup --force-fallback-for=spiel -Dspiel=true _build
meson compile --clean -C _build
meson install -C _build
```

如果您已有构建目录，请务必使用 `--reconfigure` 参数。如果在更新后出现问题，您可能需要重新构建并重新安装。

```sh
meson subprojects purge --confirm
meson setup --reconfigure --force-fallback-for=spiel -Dspiel=true _build 
meson compile --clean -C _build
meson install -C _build

# 确保所有旧的 Spiel 提供程序重新启动
flatpak kill ai.piper.Speech.Provider
flatpak kill org.espeak.Speech.Provider
```

接着，通过运行[Spiel文档](https://project-spiel.org/install.html)中的命令，为其中一个或多个语音提供程序（即piper或espeak）安装Flatpak。

若要从 Speech Dispatcher 切换到 Spiel，可使用 `orca --replace --speech-system=spiel`。鉴于 Orca 对 Spiel 的支持仍处于实验阶段，强烈建议使用此参数。如果希望默认使用 Spiel，可在 Orca 的偏好设置对话框中选中它。而要切回 Speech Dispatcher，则可使用 `orca --replace --speech-system=speechdispatcherfactory`。

# 进入开发环境
meson devenv -C _build

# 运行 Orca
orca --replace --speech-system=spiel

# 退出开发环境
exit

### 从源码构建 Spiel

对于高级用户而言，可以自行从源码构建 Spiel 及各类语音提供程序。如果您不确定该怎么做，建议先使用现有的 Flatpak 版本，并在继续操作前查阅相应发行版的文档。

1. 使用 Spiel 构建并安装 Orca

   请务必按照上述方法构建 Orca，这样在下一步构建提供程序时才能使用正确的 `libspeechprovider` 版本。如果您之前已经构建过 Orca，则需先按照相应步骤进行更新并重新构建，然后再继续操作。

2. 接下来构建并安装一个语音提供程序

   ```sh
   # 克隆仓库，然后在“providers/”目录中选择某个提供程序
   git clone https://github.com/eeejay/spiel-demos.git
   cd spiel-demos/providers/espeak

   # 构建并安装
   meson setup _build
   meson compile -C _build
   meson install -C _build
   ```

现在按照上述[说明](#spiel-text-to-speech-support)启动 Orca，您安装的 Spiel 提供程序将会自动开始运行。
