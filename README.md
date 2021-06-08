# 화재 조기 탐지 시스템 회원 서비스(Back-end)

**contributors**

- Giyoon Park

<br/>

**사용한 웹 프레임워크**

- djagno 3.1.7
- django restframework 3.12.2

<br/>

**기타**

- 실행을 위해, `settings.py`에서 `DATABASES` 변수와 `SECRET_KEY`을 변경해야한다. 

<br/>

## 1. 구현한 핵심 기능

- 회원가입
- 로그인
- JWT 발급
- CCTV 등록/삭제

<br/>

## 2. 실행 방법

## a. 필요한 라이브러리 설치

- `requirements.txt`가 있는 경로에 들어가서 아래의 명령어를 입력한다.

```
pip install -r requirements.txt
```

<br/>

## b. Django 모델을 migration file에 패키징하기

```
python manage.py makemigrations
```

<br/>

## c. Djagno 모델을 DB에 적용하기

```
python manage.py migrate
```

<br/>

## d. 서버 실행하기

```
python manage.py runserver
```

