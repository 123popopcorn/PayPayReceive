import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from PayPaython_mobile import PayPay
from datetime import datetime, timezone
import smtplib, ssl
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app, resources={r"/process_purchase": {"origins": "https://123popopcorn.github.io"}})

# 環境変数から値を取得
phone = os.getenv('PHONE')
password = os.getenv('PASSWORD')
device_uuid = os.getenv('DEVICE_UUID')
access_token = os.getenv('ACCESS_TOKEN')
proxy_user = os.getenv('PROXY_USER')
proxy_pass = os.getenv('PROXY_PASS')
proxy_address = os.getenv('PROXY_ADDRESS')
proxies = {
    "http": f"http://{proxy_user}:{proxy_pass}@{proxy_address}",
    "https": f"http://{proxy_user}:{proxy_pass}@{proxy_address}",
}
price = os.getenv('PRICE')
product = os.getenv('PRODUCT')
google_account = os.getenv('GOOGLE_ACCOUNT')
google_app_password = os.getenv('GOOGLE_APP_PASSWORD')

@app.route('/process_purchase', methods=['POST'])
def process_purchase():
    #print(phone)
    #print(google_app_password)
    # JSONデータを取得
    data = request.json
    email = data.get('email')
    paypay_link = data.get('paypayLink')
    #print(f"Email: {email}, PayPay Link: {paypay_link}")
    # 購入処理に関するロジック（例: データベースに保存、メール送信など）
    try:
        # 購入処理の疑似ロジック（例: データを保存したり、メール送信をする）
        # 実際のロジックをここに記述
        # 例: save_to_database(email, paypay_link)
        success, message, link_info = link_check(paypay_link)
        
        # 成功した場合のレスポンス
        if success:
            paypay=PayPay(phone,password,device_uuid,proxy=proxies)
            paypay.link_receive(paypay_link, link_info=link_info)
            send_test_email(email)
            return jsonify({'message': f'{message}'}), 200
        else:
            #paypay=PayPay(phone,password,device_uuid,proxy=proxies)
            #paypay.link_cancel(paypay_link, link_info=link_info)
            return jsonify({'message': f'{message}'}), 400
    except Exception as e:
        # エラー時のレスポンス
        #print(f"Error during process_purchase: {str(e)}")
        return jsonify({'message': str(e)}), 500
    
def link_check(paypay_link):
    paypay=PayPay(access_token=access_token)
    link_info = paypay.link_check(paypay_link)
    
    try:
        if not re.match(r"^https://pay\.paypay\.ne\.jp/[a-zA-Z0-9]+$", paypay_link):
            return False, "支払い失敗！\n送金URLの形式が間違っています\nhttps://pay.paypay.ne.jp/exampleの形式で入力してください", link_info
        
        if link_info['payload']['pendingP2PInfo']['amount'] != int(price):
            return False, "支払い失敗！\n金額が間違っています", link_info
        
        if link_info['payload']['pendingP2PInfo']['isSetPasscode']:
            return False, "支払い失敗！\nパスコードが設定されています\nパスコードは設定しないでください", link_info
        
        if link_info['payload']['pendingP2PInfo']['isLinkBlocked']:
            return False, "支払い失敗！\n送金URLが間違っています\nもう一度送金URLを作成し直してください", link_info
        
        expired_at_str = link_info['payload']['pendingP2PInfo']['expiredAt']
        expired_at = datetime.strptime(expired_at_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        if expired_at < current_time:
            return False, "支払い失敗！\n送金URの期限が切れています", link_info
        
        return True, "支払い成功！\n入力されたメールアドレス宛に商品のリンクを送信しました\nメールが見つからない場合は迷惑メールフォルダなどもご確認ください", link_info

    except KeyError:
        return False, "支払い失敗！\nもう一度お試しください", link_info
    
def send_test_email(email):
    msg = make_mime_text(
        mail_to = email,
        subject = "HighLow5.0",
        body = f"ご購入ありがとうございます\n以下のリンクから商品をご確認ください\n{product}"
    )
    send_gmail(msg)
    
def make_mime_text(mail_to, subject, body):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["To"] = mail_to
    msg["From"] = google_account
    return msg

def send_gmail(msg):
    server = smtplib.SMTP_SSL(
        "smtp.gmail.com", 465,
        context = ssl.create_default_context())
    server.set_debuglevel(0)
    server.login(google_account, google_app_password)
    server.send_message(msg)
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)