# seat-selector/entry_app.py
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import qrcode
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

data_file = 'data.xlsx'
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=['name', 'rrn', 'phone', 'seat', 'id'])
    df.to_excel(data_file, index=False)

def generate_id(name, rrn, phone, seat):
    unique_str = f"{name}-{rrn}-{phone}-{seat}"
    return hashlib.sha256(unique_str.encode()).hexdigest()[:12]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        rrn = request.form['rrn']
        phone = request.form['phone']
        seat = request.form['seat']

        user_id = generate_id(name, rrn, phone, seat)
        df = pd.read_excel(data_file)

        if user_id not in df['id'].values:
            df.loc[len(df)] = [name, rrn, phone, seat, user_id]
            df.to_excel(data_file, index=False)

            # QR코드 생성
            os.makedirs("static/qrs", exist_ok=True)
            qr = qrcode.make(f"https://your-app-url.onrender.com/check?id={user_id}")
            qr.save(f"static/qrs/{user_id}.png")

        return redirect(url_for('success', user_id=user_id))

    return render_template('index.html')

@app.route('/success')
def success():
    user_id = request.args.get('user_id')
    df = pd.read_excel(data_file)
    row = df[df['id'] == user_id].iloc[0]
    return render_template('success.html', name=row['name'], seat=row['seat'], user_id=user_id)

@app.route('/check')
def check():
    user_id = request.args.get('id')
    if not user_id:
        return "잘못된 접근입니다."

    df = pd.read_excel(data_file)
    row = df[df['id'] == user_id]

    if len(row) == 0:
        return "입력된 사용자가 없습니다."

    seat = row.iloc[0]['seat']
    key = f"checked_{user_id}"

    if session.get(key):
        return render_template("entry.html", msg="❌ 이미 입장하셨습니다.", color="red", seat=seat)
    else:
        session[key] = True
        return render_template("entry.html", msg="✅ 확인되었습니다.", color="green", seat=seat)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # Render는 PORT 환경변수를 씀
    app.run(host='0.0.0.0', port=port)

