from flask import Flask, render_template_string, request
from datetime import datetime, timedelta
import numpy as np
import requests

app = Flask(__name__)


# 대한민국 공휴일 API 호출 (국가별 맞춤 적용 가능)
def fetch_holidays(year):
    try:
        response = requests.get(
            f"https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo?solYear={year}&ServiceKey=YOUR_API_KEY&_type=json"
        )
        data = response.json()
        holidays = {
            item["locdate"]
            for item in data.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        }
        return holidays
    except Exception as e:
        print("공휴일 정보를 불러오지 못했습니다:", e)
        return set()


# 현재 연도 및 다음 연도의 공휴일 로드
current_year = datetime.now().year
HOLIDAYS = fetch_holidays(current_year) | fetch_holidays(current_year + 1)


def is_business_day(date):
    """토요일, 일요일, 공휴일을 제외한 영업일 판단"""
    return date.weekday() < 5 and date.strftime("%Y%m%d") not in HOLIDAYS


def count_business_days(start_date, end_date):
    """두 날짜 사이의 영업일 수 계산"""
    return sum(
        is_business_day(start_date + timedelta(days=i))
        for i in range((end_date - start_date).days + 1)
    )


def calculate_leave(join_date_str):
    join_date = datetime.strptime(join_date_str, "%Y-%m-%d")

    # 1년 미만 연차 발생 (입사일 기준)
    first_year_leave_start = join_date + timedelta(days=30)
    first_year_leave_end = join_date.replace(
        year=join_date.year + 1, month=join_date.month, day=join_date.day
    ) - timedelta(days=1)
    first_year_deadline = first_year_leave_end.replace(
        day=28
    )  # 근속 1년 발생 직전 월의 말일까지 사용 가능
    months_worked = (
        (first_year_leave_end.year - join_date.year) * 12
        + first_year_leave_end.month
        - join_date.month
    )
    earned_leaves = min(11, months_worked)  # 1개월 개근 시 1일 지급, 최대 11개

    # 1년 차 이후 연차 발생 (입사일 기준)
    one_year_later = join_date.replace(year=join_date.year + 1)
    one_year_leave_start = one_year_later
    one_year_deadline = one_year_leave_start.replace(
        year=one_year_leave_start.year + 1
    ) - timedelta(
        days=1
    )  # 근속 2년 발생 직전일까지 사용 가능
    annual_leave = 15  # 1년차 연차는 15개 고정

    # 2년 차 이후 연차 발생 (입사일 기준)
    two_year_later = join_date.replace(year=join_date.year + 2)
    two_year_deadline = two_year_later.replace(
        year=two_year_later.year + 1
    ) - timedelta(
        days=1
    )  # 근속 3년 발생 직전일까지 사용 가능

    return join_date.strftime("%Y-%m-%d"), [
        {
            "type": "입사 첫해, 1년 미만",
            "period": f"{first_year_leave_start.strftime('%Y-%m-%d')} ~ {first_year_leave_end.strftime('%Y-%m-%d')}",
            "leave_days": f"{earned_leaves}개",
            "deadline": first_year_deadline.strftime("%Y-%m-%d") + " 까지 사용해야 함",
        },
        {
            "type": "1년",
            "period": f"{one_year_leave_start.strftime('%Y-%m-%d')}",
            "leave_days": f"{annual_leave}개",
            "deadline": one_year_deadline.strftime("%Y-%m-%d") + " 까지 사용 가능",
        },
        {
            "type": "2년",
            "period": f"{two_year_later.strftime('%Y-%m-%d')}",
            "leave_days": f"{annual_leave}개",
            "deadline": two_year_deadline.strftime("%Y-%m-%d") + " 까지 사용 가능",
        },
    ]


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>연차 자동 계산기</title>
    <style>
        body {
            margin: 20px;
            text-align: center;
        }
        table {
            border-collapse: collapse;
            width: 60%;
            min-width: 660px;
            margin: 0 auto;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }
        h4 {
            margin-top: 20px;
            white-space: pre-line;
        }
    </style>
</head>
<body>
    <h2>입사일을 입력하세요:</h2>
    <form method="post">
        <input type="date" name="join_date" required>
        <button type="submit">계산</button>
    </form>
    
    {% if result %}
    <hr>
    <h3>연차 계산 결과</h3>
    <h4>
        입력한 입사일: 
        {{ join_date }}
    </h4>
    <table>
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


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    join_date = None
    if request.method == "POST":
        join_date = request.form.get("join_date")
        if join_date:
            join_date, result = calculate_leave(join_date)
    return render_template_string(HTML_TEMPLATE, result=result, join_date=join_date)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=25002, debug=True)
