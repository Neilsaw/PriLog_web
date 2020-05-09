FORMAT: 1A
HOST: https://prilog.jp

# PriLog API
プリコネ動画のタイムラインを返却するWeb API

## タイムライン取得 [GET /rest/analyze?Url={url}&Token={token}]

### 処理概要

YouTube動画のURLからタイムライン情報を取得する

#### ステータス詳細

##### 2xx

         正常　(再解析不可)　解析結果確定

    200 HD画質での解析に成功（TL返却有）

    201 SD画質での解析に成功（TL返却有）



##### 3xx

        リダイレクト可能　(再解析可能)　時間をおいて再解析可能

    301 HD画質が見つからずSD画質での解析に成功（TL返却有）

    311 HD画質が見つからずSD画質での解析に失敗

    312 動画取得に失敗した

    313 解析中にタイムアウトした

    399 予期せぬエラー

##### 4xx

        解析エラー　(再解析不可)　エラー解析結果確定

    410 HD画質の動画は見つかったが解析に失敗

    412 URLが誤っている

    413 解析可能時間を超えている

    414 解像度が対応していない

    499 予期せぬエラー


##### 5xx

        APIエラー　(再解析可能)　API受理できなかった場合

    522 パラメータが不足している

    523 不正なトークン

    599 予期せぬエラー


+ Parameters

    + Url: https://www.youtube.com/watch?v=mvLSw5vCpGU (string, required) - YouTube URL
    + Token: 7AVMHAykgDwkfwiKUgBueOZnUjd5xtWZkoG2iJC3Wa8 (string, required) - API トークン

+ Response 200 (application/json)
    + Attributes
        + msg (enum) - 結果(OK または エラーメッセージ)
            + OK (string)
            + SD画質での解析です (string)
            + SD画質での解析です。5分経過後に再度解析をお願いします (string)
            + 動画の取得に失敗しました。もう一度入力をお願いします (string)
            + 解析がタイムアウトしました。もう一度入力をお願いします (string)
            + URLはhttps://www.youtube.com/watch?v=...の形式でお願いします (string)
            + 動画時間が長すぎるため、解析に対応しておりません (string)
            + 非対応の動画です。720pの一部の動画に対応しております (string)
            + 解析結果の取得に失敗しました (string)
            + 必須パラメータがありません (string)
            + 不正なトークンです　twitter @PriLog_R までご連絡下さい (string)

        + result (array[object], fixed-type) - 解析結果
            + (object)
                + debuff_value (enum) - UB時のデバフ値(存在しない場合:false (boolean), 存在する場合:(array[string])
                    + false (boolean)
                    + (array[object])
                        + 0:0 (string)
                        + 1:0 (string)
                        + 2:64 (string)
                        + 3:87 (string)
                        + 4:64 (string)
                        + 5:87 (string)
                        + 6:64 (string)
                + process_time (enum) - 処理時間(キャッシュ参照の場合:false (boolean), 新規解析の場合:(string))
                    + false (boolean)
                    + 動画に依存 (string)
                + timeline (array[object], fixed-type) - タイムライン
                     + (array[object])
                        + 0:1:30 キャル (string)
                        + 1:1:27 ペコリーヌ (string)
                        + 2:1:18 コッコロ (string)
                        + 3:1:11 キャル (string)
                        + 4:1:02 ペコリーヌ (string)
                        + 5:1:00 キャル (string)
                        + 6:0:49 コッコロ (string)
                + timeline_txt:1:30 キャル\r\n1:27 ペコリーヌ\r\n1:18 コッコロ\r\n1:11 キャル\r\n1:02 ペコリーヌ\r\n1:00 キャル\r\n0:49 コッコロ (string) - 整形済みテキスト(改行コード CRLF)
                + timeline_txt_debuff:↓  0 1:30 キャル\r\n↓  0 1:27 ペコリーヌ\r\n↓ 64 1:18 コッコロ\r\n↓ 87 1:11 キャル\r\n↓ 64 1:02 ペコリーヌ\r\n↓ 87 1:00 キャル\r\n↓ 64 0:49 コッコロ (string) - デバフ値を入れた整形済みテキスト(改行コード CRLF)
                + title:タイムライン作成サンプル　(string) - 動画のタイトル
                + total_damage (enum) - 動画での総ダメージ値(存在しない場合:false (boolean), 存在する場合:(string))
                    + false (boolean)
                    + 動画に依存 (string)
        + status:200 (number) - エラーステータス(2xx:正常, 3xx:リダイレクト可能, 4xx:解析エラー, 5xx:APIエラー, x0x:TLあり, xx0:HD解析, xx1:SD解析)
