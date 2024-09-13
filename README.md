<div id="top"></div>

## 使用技術一覧

<!-- シールド一覧 -->
<!-- 該当するプロジェクトの中から任意のものを選ぶ-->
<p style="display: inline">
  <!-- バックエンドの言語一覧 -->
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
</p>

## 目次

1. [プロジェクトについて](#プロジェクトについて)
2. [環境](#環境)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [開発環境構築](#開発環境構築)

<!-- プロジェクト名を記載 -->

## プロジェクト名

RGBtoTHERMAL

<!-- プロジェクトについて -->

## プロジェクトについて

RGB2THERMAL：RGB画像から赤外線画像を生成するためのデータ採集や3Dモデル，データセットを記載する

## 環境

<!-- 言語、フレームワーク、ミドルウェア、インフラの一覧とバージョンを記載 -->

| 言語・モジュール        | バージョン |
| --------------------- | ---------- |
| Python                | 3.11.9     |
| japanize-matplotlib   | 1.1.3      |
| keyboard              | 0.13.5     |
| matplotlib            | 3.8.4      |
| natsort               | 8.4.0      |
| matplotlib            | 3.8.4      |
| numpy                 | 1.26.4     |
| opencv-python         | 4.10.0.84  |
| mpmath                | 1.3.0      |
| scikit-learn          | 1.4.2      |
| serial                | 0.0.97     |
| tqdm                  | 4.66.4     |
| torch                 | 2.3.1+cu118|
| PyAutoGUI             | 0.9.54     |


<p align="right">(<a href="#top">トップへ</a>)</p>

## ディレクトリ構成

<!-- Treeコマンドを使ってディレクトリ構成を記載 -->


```
.
├── 3Dmodel // 本研究で用いた機構の3Dデータ
├── DataSet // 取得したデータセット
├── model //CycleGANとpix2pixの基盤モデル
├── results
│   ├── Arduino // Arduino関連プログラムで取得した結果
│   └──  Calibration // Calibration関連プログラムで取得した結果
├── src //ソースコード
│   ├── Arduino // Arduinoで使用するソースコード
│   ├── Calibration // Calibraitonの際に使用するソースコード
│   ├── DataSet // DataSetを作成する際に使用するソースコード
│   └── Others // その他以外のソースコード
├── utils // 使いまわすクラス
├── .gitignore
├── environment.yml //Anaconda専用の環境ファイル
├── dynamixel_sdk.zip // dyanmixelを動かすために必要なモジュール（仮想環境内に移動）
└── README.md
```
<p align="right">(<a href="#top">トップへ</a>)</p>

## 開発環境構築

<!-- コンテナの作成方法、パッケージのインストール方法など、開発環境構築に必要な情報を記載 -->
- Anaconda
- Windows

### Anacondaでの仮想環境
```
## 自分で1から環境を整える場合

# 仮想環境の作成
conda create --name [仮想環境名] python=3.11.9

# 仮想環境のアクティベート
conda activate [仮想環境名]
```

```
## 本研究で用いた環境をそのまま再利用する場合(この場合，仮想環境名は，RGBtoTHERMALとなる)

# enviroment.ymlから環境を構築
conda env create -f environment.yml
```
### Dynamixel_sdkの設定
```
users\anaconda\envs\[自分が使用する仮想環境]\Lib\scite-packeages\
にdynamixel_sdk.zipを解凍したものを移動させる
```

### DataSetフォルダ内のps1ファイル実行方法

.ps1ファイルは，PowerShellで実行

```
# DataSetフォルダに移動
cd ./DataSet

# xxx.ps1ファイルを実行
.\xxx.ps1
```

### DataSetフォルダ内のps1ファイル作成方法

- 新たに作成したDataSetをzipファイルにし，DropBoxに移動する
- DropBoxに移したzipファイルのリンクをコピーする
- $url = " [ここにリンクをコピー]" 
- $urlにおいて，"xxx&dl=0"を"xxxx&dl=1"に変更する

<p align="right">(<a href="#top">トップへ</a>)</p>
