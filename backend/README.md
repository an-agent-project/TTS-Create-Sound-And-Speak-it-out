# Backend

FastAPI backend for the podcast TTS preview API.

## Setup

From the project root:

```powershell
C:\Users\lenovo\anaconda3\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_tts_preview.py -v
```

## Initialize MySQL

The schema script creates the `tts_podcast` database, the voice tables, and the current Edge-TTS voice seed data.

```powershell
mysql -u root -p < backend\db\init.sql
```
