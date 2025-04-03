import json
import firebase_admin
from firebase_admin import credentials, storage
import os
from datetime import datetime

# 올바른 Firebase Storage 버킷 이름 (ex: <project-id>.appspot.com)
BUCKET_NAME = "asurajang-39231.firebasestorage.app"

# Firebase 앱이 이미 초기화되어 있지 않으면 초기화
if not firebase_admin._apps:
    if "RENDER" in os.environ:
        print("[INFO] Render 환경 감지됨 → 환경변수로 Firebase 초기화")
        firebase_json_str = os.environ.get("FIREBASE_CONFIG_JSON")
        cred_dict = json.loads(firebase_json_str)
        cred = credentials.Certificate(cred_dict)
    else:
        print("[INFO] 로컬 환경 → 파일로 Firebase 초기화")
        cred = credentials.Certificate("firebase_config.json")

    firebase_admin.initialize_app(cred, {
        "storageBucket": BUCKET_NAME
    })

def upload_backup(file_path, firebase_path):
    """Firebase Storage에 파일 업로드"""
    bucket = storage.bucket()
    blob = bucket.blob(firebase_path)
    blob.upload_from_filename(file_path)
    print(f"[Firebase] 백업 업로드 완료: {firebase_path}")

def download_backup(firebase_path, local_path):
    """Firebase Storage에서 파일 다운로드"""
    bucket = storage.bucket()
    blob = bucket.blob(firebase_path)
    if blob.exists():
        blob.download_to_filename(local_path)
        print(f"[Firebase] 백업 다운로드 완료: {firebase_path}")
        return True
    else:
        print(f"[Firebase] 백업 파일 없음: {firebase_path}")
        return False

def get_latest_backup_time():
    """Firebase에 저장된 마지막 백업 시간 파일 읽기"""
    bucket = storage.bucket()
    blob = bucket.blob("backups/last_backup.txt")
    if blob.exists():
        return blob.download_as_text().strip()
    return None

def set_latest_backup_time():
    """Firebase에 마지막 백업 시간 기록"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bucket = storage.bucket()
    blob = bucket.blob("backups/last_backup.txt")
    blob.upload_from_string(now_str)
    print("[Firebase] 마지막 백업 시각 저장됨:", now_str)

