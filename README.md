## 실행 방법

### 1. 도커 이미지 빌드
```sh
docker build -t flask-annual-leave .
docker image prune -f  # <none> 이미지 삭제
```

### 2. 컨테이너 실행 (백그라운드 모드)
```sh
docker run -d  --name annual-leave -p 25002:25002 flask-annual-leave
```

### 3. 웹 애플리케이션 접속
웹 브라우저에서 아래 주소로 접속하면 연차 계산을 할 수 있습니다.
```
http://localhost:25002
```

## 개발 환경
- Python 3.12
- Flask

## 기능
- 입사일을 입력하면 1년 미만 연차와 1년 이후 연차를 계산하여 HTML로 표시

