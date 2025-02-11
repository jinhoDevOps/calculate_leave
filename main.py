from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>연차 자동 계산기</title>
</head>
<body>
    <h2>입사일을 입력하세요:</h2>
    <form method="post">
        <input type="date" name="join_date" required>
        <button type="submit">계산</button>
    </form>
    
    {% if result %}
    <h3>연차 계산 결과</h3>
    <table border="1">
        <tr><th>구분</th><th>휴가 발생일</th><th>발생 연차</th><th>사용 기한</th></tr>
        {% for row in result %}
        <tr>
            <td>{{ row["type"] }}</td>
            <td>{{ row["period"] }}</td>
            <td>{{ row["leave_days"] }}</td>
            <td>{{ row["deadline"] }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
"""

def calculate_leave(join_date_str):
    join_date = datetime.strptime(join_date_str, "%Y-%m-%d")
    
    # 1년 미만 연차 발생 (월차 기준)
    first_year_start = (join_date.replace(day=1) + timedelta(days=31)).replace(day=1)
    first_year_end = datetime(join_date.year + 1, join_date.month - 1, 1)
    first_year_leave_days = min(11, (first_year_end.year - join_date.year) * 12 + first_year_end.month - join_date.month)
    first_year_leave_deadline = first_year_end.strftime('%Y-%m') + " 까지 사용해야 함"
    
    # 1년 차 이후 연차 발생
    one_year_later = datetime(join_date.year + 1, join_date.month, join_date.day)
    one_year_leave_end = datetime(one_year_later.year + 1, one_year_later.month - 1, 1)
    one_year_leave_deadline = one_year_leave_end.strftime('%Y-%m') + " 까지 사용 가능"
    
    return [
        {"type": "입사 첫해, 1년 미만", "period": f"{first_year_start.strftime('%Y-%m-%d')} ~ {first_year_end.strftime('%Y-%m-%d')}", "leave_days": f"최대 {first_year_leave_days}개", "deadline": first_year_leave_deadline},
        {"type": "1년 차 이후", "period": f"{one_year_later.strftime('%Y-%m-%d')} ~ {one_year_leave_end.strftime('%Y-%m-%d')}", "leave_days": "15개", "deadline": one_year_leave_deadline},
    ]

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        join_date = request.form.get("join_date")
        if join_date:
            result = calculate_leave(join_date)
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=25002, debug=True)
