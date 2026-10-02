# Forge Library Desk Bridge

Save and restore per-checkpoint txt2img settings between Forge Neo and [LoRA Library Desk](https://github.com/gariyou/lora-library-desk).

**Windows / Forge Neo向け試用版 / 0.1.0-alpha.1 / MIT**

Generate下（スタイル選択欄の下）へ3つの連携ボタンを追加します。

## 導入

Library Desk本体が必要です。本体とForgeを同じPCで使ってください。

### Gitから

Forgeの`Extensions→Install from URL`へ以下を指定してインストールします。

`https://github.com/gariyou/sd-forge-library-desk-bridge.git`

Forgeを再起動してください。実行中の生成が終わってから行ってください。

### ZIPから

[Releases](https://github.com/gariyou/sd-forge-library-desk-bridge/releases)のZIPを展開し、`scripts/`、`javascript/`、`bridge_core.py`、`local_connection.py`、`style.css`がForgeの`extensions/lora-library-desk-bridge/`直下に並ぶようにコピーします。すでに同じ拡張がある場合は置き換え、2重にインストールしないでください。Forgeを再起動します。

## 使い方

1. Library DeskとForge画面を両方開きます。
2. Forgeの「現在の設定をLibrary Deskへ保存」で、Forgeで選択中のチェックポイントに現在の設定を保存します。Library Deskにそのモデルのフォルダを登録しておく必要があります。
3. Library Deskでモデルを選択して「Forgeへ送る」で復元します。「Library Deskの設定を受け取る」は待機中の送信を受信し、「接続を更新」は画面の設定を読み直します。

外部VAE／エンコーダーの未選択も保存できます。Step、Sampler、Scheduler、サイズ、CFG、Seed、Prompt、Hires、Refiner、拡張機能の数値・文字・選択設定と生成関連オプションが対象です。保存可能な項目数は導入済みの拡張によって変わります。

この拡張は画像生成を開始しません。生成中の設定反映は拒否しますが、設定の保存は利用できます。ControlNet等の入力画像そのもの、img2img、実行中ジョブは対象外です。保存時と拡張構成や選択肢・ファイルが異なる場合は復元を拒否します。

## ポートが違う場合

Forgeの`Settings→Library Desk→Library Desk URL`で本体URLを設定し、Apply settings→Reload UIを行います。初期値は`http://127.0.0.1:8787`です。本体側の`Forge連携→接続設定`にもForge URLを設定します（初期値`http://127.0.0.1:7860`）。同じPCのHTTPループバックURLのみ対応しています。

## 対応と通信

Forge Neo 2.29.2 / Gradio 4.40.0でボタン配置と設定往復を検証しています。他のForge派生とA1111は未確認です。追加のモデル・GPUライブラリ・Gradioはインストールしません。Forge本体のバージョンや生成環境を変更しません。

通信先は同じPCのForgeとLibrary Deskのみです。モデル実体や画像を送信しません。接続設定はForge自身の設定ファイルへ、モデル別プリセットはLibrary Deskの管理DBへ保存されます。配布物に個人設定・プロンプト・認証情報は含めません。

MITはこの拡張のコードに適用します。Forge本体は外部のAGPL-3.0プロジェクトです。Forge本体のコード・ライセンスを置き換えたり同梱したりしません。[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)も参照してください。

検証内容と限界：[VALIDATION.md](VALIDATION.md)
