# Orca v51.rc

<!-- hy-mt2-i18n:start -->
[English](./README.md) | [中文](./README_zh-CN.md) | **日本語** | [Español](./README_es.md)
<!-- hy-mt2-i18n:end -->


[目次]

## アプリケーション開発者の皆様へ

もし、ご自身のアプリケーションをOrcaと連携させようとしているアプリケーション開発者であれば、
[アプリケーション開発者向けREADME](docs/application-developers.md)をご覧ください。

## はじめに

Orcaは、無料でオープンソースの、柔軟かつ拡張性に優れたスクリーンリーダーであり、ユーザーがカスタマイズ可能な音声および/または点字の組み合わせを通じてグラフィカルデスクトップにアクセスできるようにします。

Orcaは、SolarisおよびLinuxで使用される主要な補助技術インフラである補助技術サービスプロバイダインターフェース（AT-SPI）をサポートするアプリケーションやツールキットと連携動作します。OrcaはGNOME Projectの一部ではありますが、どのアクセシブルなデスクトップ環境でも利用可能です。

Orcaに関する詳細な情報、例えばOrcaの実行方法、Orcaユーザーコミュニティとの連絡先、バグや機能要望の報告先などは、<https://orca.gnome.org>をご覧ください。

## 依存関係

Orcaには以下の依存関係があります：

* meson: Orcaで使用されるビルドシステム  
* Python 3: Pythonプラットフォーム  
* pygobject-3.0: GObjectライブラリ用のPythonバインディング  
* gtk+-3.0: GTK+ツールキット  
* at-spi2-core 2.58.6以降、Pythonサポートが組み込まれたバージョン  
* gpaste: KDE以外のWaylandセッション向けのクリップボードマネージャー（任意）。  
  Orcaがクリップボードに項目をコピーまたは追加するコマンドに必要です。  
  KDEセッションではKlipperが利用されます。  
* python3-babel: ローカライズされた言語名の表示をサポートするBabel（強く推奨）。  
  Babelがなければ、OrcaのUI内の言語は名前ではなくコードとして表示されます。  
* python3-brlapi: 点字処理をサポートするBrlAPI (<https://mielke.cc/brltty/>)（任意）  
* python3-dasbus: Orcaの遠隔操作をサポートするDasbus (<https://dasbus.readthedocs.io/>)  
* python3-louis: 縮約点字処理をサポートするLiblouis (<https://liblouis.io/>)（任意）  
* python3-psutil: プロセスおよびシステム関連のユーティリティ（任意）  
* python3-setproctitle: プロセスのタイトルを設定するPythonライブラリ（強く推奨）。  
  これにより`pidof orca`が正常に動作します。また、`/proc/<OrcaのPID>/cmdline`に「orca」という文字が含まれるように更新されます。Chromiumベースのブラウザはこの値をチェックし、`--force-rendereer-accessibility`を指定しなくても自動的に完全なアクセシビリティサポートを有効にします。  
* python3-speechd: Speech Dispatcher用のPythonバインディング（任意）  
* gstreamer-1.0: ストリーミングメディアフレームワークGStreamer（任意）  
* cargo: MathMLサポートのためのMathCAT (<https://daisy.github.io/MathCAT/>)のビルドに使用されます。  
  MathCATはデフォルトでビルドされるため、`meson setup`に`-Dmathcat=false`を渡して除外しない限りcargoが必要です。  
* libwnck3: X11環境でのマウス確認機能に使用される（任意、非推奨）

GNOME 50.x リリース向けの AT-SPI2 および ATK の最新安定版も必ずインストールすることを強く推奨します。

## 点字ユーザー向けの注意事項

BrlAPI用のPythonバインディングがインストールされているかどうかは、次のコマンドを実行することで確認できます：

```sh
python -c "import brlapi"
```

エラーが表示された場合は、BrlAPI用のPythonバインディングがインストールされていないことを意味します。

## Orcaのビルドとインストール

 `_build` というディレクトリ内で Orca をビルドし、ディストリビューションのデフォルト設定の場所（例：/usr/local）に Orca をインストールしたい場合は：

```sh
meson setup _build
meson compile -C _build
meson install -C _build
```

インストーラーは必要に応じて `sudo` 権限の入力を求めてきます。

別のインストール先を指定するには、セットアップ時に `-D prefix=` を使用してください
（例: `meson setup -D prefix=$HOME/orca-test _build`）。

再ビルドするには、以前に作成したビルドディレクトリ（例：`_build`）を削除するか、既存の`meson setup`コマンドの末尾に`--reconfigure`フラグを追加してください。

アンインストールするには、作成したビルドディレクトリに`cd`して`ninja uninstall`を実行します。`sudo`権限を使ってOrcaをインストールした場合は`sudo ninja uninstall`を使用します。なお、これによって`__pycache__`内のバイトコードファイルは削除されません。詳しくはこの[mesonのissue](https://github.com/mesonbuild/meson/issues/12798)をご覧ください。

## Orcaの実行

Orcaの設定を変更したい場合は、Orcaが実行中に「Insert+space」キーを押してください。

Orcaを実行中にヘルプを取得するには、「Insert+H」キーを押してください。これにより「学習モード」が有効になり、さまざまなキーボードや点字入力デバイスの操作が何を行うかが音声および点字で説明されます。学習モードを終了するには「Escape」キーを押してください。最後に、設定ダイアログにはOrcaのキーボード割り当てが一覧表示される「Key Bindings」タブがあります。

詳細については、Orca 内部および <https://gnome.pages.gitlab.gnome.org/orca/help> で入手可能な Orca のドキュメントをご覧ください。

## Orcaのスクリプトと機能

Orcaのスクリプトは、アクセシブルなイベントに応答することでアプリケーションやツールキットへのアクセスを可能にします。例えば、アプリケーション内でフォーカスが変更されると、そのアプリケーションは`object:state-changed:focused`というアクセシブルなイベントを発行し、それをアプリケーションまたはツールキットに関連付けられたスクリプトが処理します。

もしアクセシブルなアプリケーションやツールキットがあるものの、Orcaによるサポートが不十分な場合、そのアプリケーション用にカスタムスクリプトを作成することが適切な解決策かもしれません。（実際には、Orcaやそのアプリケーション自体のバグを修正する方が適切な解決策である場合もあります。）スクリプトの例を見たい場合は、ソースツリーの`src/orca/scripts`を確認してください。

スクリプトは機能をインポートすることもできますが、これらの機能自体はスクリプト内に存在するわけではなく、ナビゲータやプレゼンタ、その他の同様のモジュール内にあります。

## リモートコントローラー（D-Busインターフェース）

OrcaはD-Busインターフェースを提供しており、外部アプリケーションがOrcaの機能を遠隔から制御したり、ユーザーにメッセージを表示したりできるようにします。詳細な使用方法の説明、例、およびAPIドキュメントについては、[remote-controller.md](docs/remote-controller.md)をご覧ください。

## GSettingsサポート

Orca v50以降では、設定にGSettingsが使用されています。Orcaのスキーマ、キー、デフォルト値、enumの一覧は[gsettings-schemas.md](docs/gsettings-schemas.md)で確認できます。

## Spiel テキスト読み上げサポート

デフォルトでは、OrcaのTTSサポートにはspeech-dispatcherが使用されています。また、複数の合成エンジンから声を選択できる[Spiel](https://github.com/project-spiel)に対する基本的なサポートも備わっており、現在はeSpeakやPiperが利用可能です。

Spielをテストするには、最新のソースからビルドできるようOrcaを設定します。コンパイルが完了したら、`meson devenv`を使用してOrcaを実行します。

```sh
meson setup --force-fallback-for=spiel -Dspiel=true _build
meson compile --clean -C _build
meson install -C _build
```

既存のビルドディレクトリがある場合は、`--reconfigure` を忘れずに使用してください。アップデート後に問題が発生した場合は、再ビルドしてから再インストールする必要があるかもしれません：

```sh
meson subprojects purge --confirm
meson setup --reconfigure --force-fallback-for=spiel -Dspiel=true _build 
meson compile --clean -C _build
meson install -C _build

# 古いSpielプロバイダーが再起動されるようにする
flatpak kill ai.piper.Speech.Provider
flatpak kill org.espeak.Speech.Provider
```

次に、[Spielのドキュメント](https://project-spiel.org/install.html)に記載されているコマンドを実行して、1つ以上の音声プロバイダ（つまりpiperまたはespeak）用のFlatpakをインストールします。

Speech DispatcherからSpielに切り替えるには、`orca --replace --speech-system=spiel`を使用します。OrcaのSpielサポートがまだ実験段階にあるため、このフラグの使用を強く推奨します。デフォルトでSpielを使用したい場合は、Orcaの設定ダイアログでそれを選択できます。再びSpeech Dispatcherに戻すには、`orca --replace --speech-system=speechdispatcherfactory`を使用してください。

# 開発環境への入り方
meson devenv -C _build

# Orcaを起動する
orca --replace --speech-system=spiel

# 開発環境からの退出
exit

### ソースからのSpielのビルド

上級ユーザーの場合、Spielや各スピーチプロバイダーをソースからビルドすることも可能です。迷った場合は、利用可能なFlatpakを使うことを検討し、続行する前にご使用のディストリビューションのドキュメントを参照してください。

1. Spielを使用してOrcaをビルドし、インストールする

   前述の手順に従って必ずOrcaをビルドしておくことで、次のステップでプロバイダをビルドする際に正しい`libspeechprovider`バージョンが利用可能になります。以前にOrcaをビルド済みの場合は、続行する前にアップデートして再ビルドする手順に従ってください。

2. 次にプロバイダをビルドしてインストールする

   ```sh
   # リポジトリをクローンし、"providers/"ディレクトリ内からプロバイダを選択する
   git clone https://github.com/eeejay/spiel-demos.git
   cd spiel-demos/providers/espeak

   # ビルドしてインストールする
   meson setup _build
   meson compile -C _build
   meson install -C _build
   ```

上記の[指示](#spiel-text-to-speech-support)に従ってOrcaを起動すると、インストールしたSpielプロバイダーが自動的に動作し始めます。
