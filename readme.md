## 介護伝送通信ソフトのメールボックス内ファイルパスを探す旅

### 使い方

```python
from mailbox import KaigoDensoMailBox
# 伝送通信をなにも考えずにインストールすると「C:/Kaigo/Kaigo_D/MailBox」に入ってると思います。
box = KaigoDensoMailBox()
# もし、違う場合は
box = KaigoDensoMailBox("<メールボックスのパス>")

# 事業所一覧
box.get_office_list()

# 送信データファイルパスリスト
box.get_send_file_path_list("<事業所番号文字列>"," <請求月文字列（YYYYMM）>")

# 審査結果ファイルパスリスト
box.get_result_file_path_list("<事業所番号文字列>"," <請求月文字列（YYYYMM）>")

# 審査状況一覧ファイルパス
box.get_judge_file_path("<事業所番号文字列>", "<受信月文字列（YYYYMM）>")

# 連絡文書ファイルパスリスト
box.get_contact_file_path_list("<事業所番号文字列>", "<受信月文字列（YYYYMM）>")
```