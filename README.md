# FORJASIS2026 (期間限定公開)

計測分析データを [MaiML](https://www.jaima.or.jp/)（JIS K 0200 / MaiML-Schema-1_0）形式で
作成・変換・可視化するためのツール一式をまとめたハンズオン用パッケージです。

Excelで記載した実験計画・実験結果をMaiMLファイルに変換するツールと、eLabFTWの実験記録を
MaiMLに変換するツール、生成したMaiMLファイルをブラウザ上で可視化するViewerの、
合計4つのツールで構成されています。

## 構成

```
FORJASIS2026/
├── SETUP/                  環境構築用（初回のみ実行）
│   ├── ForMacUsers/        Mac用セットアップスクリプト
│   ├── ForWindowsUsers/    Windows用セットアップスクリプト
│   ├── requirements.txt    共通のPython依存パッケージ
│   └── DATAFILES.zip       ハンズオン用サンプルデータ
├── RUN/                    各ツールの実行用スクリプト
│   ├── ForMacUsers/        Mac用実行スクリプト（.sh）
│   └── ForWindowsUsers/    Windows用実行スクリプト（.bat）
└── SRC/                    各ツール本体（GitHubの各リポジトリを取り込んだもの）
    ├── 01_Excel2MaiMLProtocol/   Excel → MaiML（計画情報）変換
    ├── 02_Excel2MaiMLData/       Excel + MaiML → MaiML（実測データ）マージ
    ├── 03_MaiMLStandaloneViewer/ MaiMLファイルの可視化ビューア
    └── 05_elabftw2MaiML/         eLabFTW → MaiML 変換
```

## 各ツールについて

| No. | ツール名 | 概要 | GitHub |
|-----|---------|------|--------|
| 01 | Excel2MaiMLProtocol | 計測分析の手順・条件等の計画情報を記載したExcelファイルから、`protocolFileRootType` タイプのMaiMLファイルを生成する | https://github.com/MaiML-Tools/Excel2MaiMLProtocol |
| 02 | Excel2MaiMLData | 01で作成した計画MaiMLファイルと、実測結果を記載したExcelファイルをマージし、`maimlRootType` タイプのMaiMLファイルを生成する | https://github.com/MaiML-Tools/Excel2MaiMLData |
| 03 | MaiMLStandaloneViewer | MaiMLファイルをブラウザ上でグラフ表示・可視化・分析するスタンドアロンWebアプリ | https://github.com/MaiML-Tools/MaiMLStandaloneViewer |
| 05 | elabftw2MaiML | eLabFTW（REST API v2）の実験データを読み出し、MaiMLファイルに変換する（読み取り専用） | https://github.com/MaiML-Sandbox/elabftw2MaiML |

各ツールの詳細な入出力仕様は、各GitHubレポジトリを参照してください。

## セットアップ（初回のみ）

### Mac

```bash
cd SETUP/ForMacUsers/
./00_macSetup.sh
```

Python仮想環境 `handsonvenv` を作成し、`SETUP/requirements.txt` に記載の依存パッケージを
インストールしたうえで、`SETUP/DATAFILES.zip` を `RUN/ForMacUsers/` に展開します。

### Windows

```bat
cd SETUP\ForWindowsUsers
00_windowsSetup.bat
```

Mac用と同様に、仮想環境の作成・依存パッケージのインストール・DATAFILESの展開を行います。

プロキシ環境下にある場合は、各セットアップスクリプト内のプロキシ設定部分のコメントアウトを
解除し、環境に合わせて書き換えてください。

## 実行方法

セットアップ完了後、`RUN/ForMacUsers/`（Windows環境< `RUN/ForWindowsUsers/`)配下の
スクリプトを番号順に実行します。

| 番号 | スクリプト | 内容 |
|------|-----------|------|
| 01 | `01_Excel2MaiMLProtocol.sh` / `.bat` | `DATAFILES/01_Excel2MaiMLProtocol/INPUT/` のExcelファイルからMaiML（計画情報）を生成し、`DATAFILES/01_Excel2MaiMLProtocol/OUTPUT/` に出力 |
| 02 | `02_Excel2MaiMLData.sh` / `.bat` | 01の出力MaiMLと `DATAFILES/02_Excel2MaiMLData/INPUT/` のExcel（実測結果）をマージし、`DATAFILES/02_Excel2MaiMLData/OUTPUT/` に出力 |
| 03 | `03_MaiMLStandaloneViewer.sh` / `.bat` | ビューア（`HTML-MaiMLViewer.html`）を既定のブラウザで開く |
| 05 | `05_elabftw2MaiML.sh` / `.bat` | eLabFTWの実験データ（実験ID指定）をMaiMLに変換し、`DATAFILES/05_elabftw2MaiML/MaiML/` に出力 |

- 各スクリプトは `RUN/ForMacUsers/` または `RUN/ForWindowsUsers/` から実行してください（相対パスで `SRC/` を参照しています）。
- 05番のスクリプトは、実行前にサーバーやAPIキーの設定、`--experiment-id` などの引数をご自身の環境に合わせて編集してください。

## 必要環境

- Python 3系（`venv` が利用できること）
- 主な依存パッケージ（`SETUP/requirements.txt` に記載）
  - openpyxl, pandas, numpy, lxml, python-dateutil, elabapi-python など
- MaiMLStandaloneViewer（03）はWebブラウザのみで動作し、Python環境は不要

## 注意事項

- elabftw2MaiML（05）はeLabFTWに対して読み取り専用でアクセスします（書き込み・更新は行いません）。
- 各ツールの最新版・詳細ドキュメントは、上記GitHubリポジトリを参照してください。
