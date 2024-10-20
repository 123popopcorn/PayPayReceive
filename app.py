import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/process_purchase', methods=['POST'])
def process_purchase():
    # JSONデータを取得
    data = request.json
    email = data.get('email')
    paypay_link = data.get('paypayLink')

    # 受け取ったデータを確認
    print(f'Received Email: {email}')
    print(f'Received PayPay Link: {paypay_link}')

    # 購入処理に関するロジック（例: データベースに保存、メール送信など）
    try:
        # 購入処理の疑似ロジック（例: データを保存したり、メール送信をする）
        # 実際のロジックをここに記述
        # 例: save_to_database(email, paypay_link)
        
        # 成功した場合のレスポンス
        return jsonify({'message': '支払い成功\n入力されたメールアドレス宛に商品のリンクを送信しました\nメールが見つからない場合は迷惑メールフォルダなどもご確認ください'}), 200
    except Exception as e:
        # エラー時のレスポンス
        return jsonify({'message': f'支払い失敗: {str(e)}'}), 500
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
