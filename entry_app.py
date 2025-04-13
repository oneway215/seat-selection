from flask import Flask, request, render_template, redirect, url_for
import uuid

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# 좌석 예약 상태 저장
reserved_seats = {}  # 예: { 'R1C1': 'abc123', 'R2C5': 'xyz789' }
user_seat_map = {}   # 예: { 'abc123': 'R1C1', 'xyz789': 'R2C5' }

@app.route('/')
def seat_page():
    return render_template('seats.html', reserved=reserved_seats)

@app.route('/reserve', methods=['POST'])
def reserve():
    seat_id = request.form['seat']
    if seat_id in reserved_seats:
        return f"<h3>{seat_id}는 이미 예약된 좌석입니다.</h3><a href='/'>돌아가기</a>"

    unique_id = str(uuid.uuid4())[:8]  # 8자리 고유 ID 생성
    reserved_seats[seat_id] = unique_id
    user_seat_map[unique_id] = seat_id
    return redirect(url_for('check_in', id=unique_id))

@app.route('/check')
def check_in():
    user_id = request.args.get('id', 'UNKNOWN')
    seat_id = user_seat_map.get(user_id, '정보 없음')
    return render_template('entry.html', user_id=user_id, seat_id=seat_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
