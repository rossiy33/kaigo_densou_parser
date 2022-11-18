import pathlib
import re
from xml.etree import ElementTree


class KaigoDensoMailBox:
    __mailbox: pathlib.Path

    def __init__(self, str_mailbox_path: str = "C:/Kaigo/Kaigo_D/MailBox"):
        self.__mailbox = pathlib.Path(str_mailbox_path)

    # 事業所フォルダリスト
    def get_office_list(self, non_hd=True):
        if non_hd:
            return [p.name for p in self.__mailbox.iterdir() if p.is_dir() and not p.name[:2] == 'HD']
        else:
            return [p.name for p in self.__mailbox.iterdir() if p.is_dir()]

    # 情報XML（file_type: send, judge）
    def __get_info_tree(self, office_number: str, file_type: str) -> ElementTree:
        office_path = self.__mailbox / str(office_number)
        match file_type:
            case 'send':  # 送信データ
                info_path = office_path / f"DATA_{office_number}_SEND.xml"
            case 'result':  # 審査支払、審査支払状況管理、通知文書管理
                info_path = office_path / f"DATA_{office_number}_RESULT.xml"
            case 'contactp':  # 審査状況一覧
                info_path = office_path / f"DATA_{office_number}_CONTACTP.xml"
            case 'contact':  # 連絡文書（介護インフォメーション、連絡電文情報など）
                info_path = office_path / f"DATA_{office_number}_CONTACT.xml"
            case _:
                raise TypeError("unkown file type")
        del office_path

        with info_path.open(mode="r") as f:
            xml_data = f.read()
        assert xml_data
        return ElementTree.fromstring(xml_data)

    # 送信ファイルpathリスト
    def get_send_file_path_list(self, office_number: str, str_bill_ym: str) -> [pathlib.Path]:
        # メール情報から格納パスを取得
        path_list = []
        for e in list(self.__get_info_tree(office_number, 'send').findall("./送信箱/送信データ")):
            if e.findtext("状態") not in ["到達完了", "連合会到達", "送信完了"]:
                continue
            # 2018-05からある
            if not e.findtext("請求年月"):
                continue
            if not e.findtext("請求年月") == str_bill_ym:
                continue

            path_list.extend(pathlib.Path(e.findtext("送信ファイルパス")).iterdir())
        return path_list

    # 審査支払状況管理
    def get_result_status(self, office_number: str, str_judge_ym: str) -> dict:
        # メール情報から結果状況を取得
        for e in list(self.__get_info_tree(office_number, 'result').findall("./受信箱/審査支払状況管理/状況")):
            if not e.attrib['審査年月'] == str_judge_ym:
                continue

            return {
                'ステータスレベル': e.findtext("ステータスレベル"),
                '支払通知': e.findtext("支払通知"),
                '返戻通知': e.findtext("返戻通知")}

    # 最新結果番号
    def get_result_lasted_notice_num(self, office_number: str) -> dict:
        # メール情報から最新結果番号を取得
        for e in list(self.__get_info_tree(office_number, 'result').findall("./受信箱/通知文書管理")):
            return {'最新通知番号': e.findtext("最新通知番号")}

    # 審査支払通知ファイルpathリスト
    def get_result_file_path_list(self, office_number: str, notice_num: str = '', str_bill_ym: str = '') -> [pathlib.Path]:
        # メール情報から審査支払通知ファイルpathを取得
        path_list = []
        for e in list(self.__get_info_tree(office_number, 'result').findall("./受信箱/審査支払/通知文書")):
            if notice_num and not e.attrib['番号'] == notice_num:
                continue
            if str_bill_ym and not e.attrib['請求年月'] == str_bill_ym:
                continue

            path_list.append(pathlib.Path(e.findtext('ファイルパス')+e.findtext('ファイル名')))

        return path_list

    # 審査状況一覧ファイルpath
    def get_judge_file_path(self, office_number: str, str_recv_ym: str) -> pathlib.Path | None:
        # メール情報から格納パスを取得
        for e in list(self.__get_info_tree(office_number, 'contactp').findall("./受信箱/印刷/お知らせ")):
            if not e.findtext('タイトル') == '審査状況一覧の送付':
                continue
            if not e.findtext('受信日付')[:6] == str_recv_ym:
                continue

            if e.findtext('ファイルパス'):
                return list(pathlib.Path(e.findtext('ファイルパス')).iterdir())[0]

    # 連絡文書ファイルpathリスト
    def get_contact_file_path_list(self, office_number: str, str_recv_ym: str) -> {str: pathlib.Path}:
        # メール情報から格納パスを取得
        dic = {}
        for e in list(self.__get_info_tree(office_number, 'contact').findall("./受信箱/連絡文書/お知らせ")):
            if not e.findtext('受信日付')[:6] == str_recv_ym:
                continue

            title = e.findtext('タイトル')
            if '連絡電文' in title:
                title = f"{str_recv_ym}_{office_number}_{re.findall('連絡電文情報（(.*)）', title)[0]}"

            dic[title] = list(pathlib.Path(e.findtext('ファイルパス')).iterdir())[0]
        return dic
