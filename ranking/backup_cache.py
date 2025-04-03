import json
from ranking.firebase_manager import get_latest_backup_time, download_backup

# 전역 캐시 저장소
_backup_cache = {
    "date": None,
    "data": None
}

def get_cached_backup_data():
    """
    Firebase Storage에서 랭킹 백업 데이터를 하루에 한 번만 다운로드하고,
    서버 메모리에 캐싱하여 재사용하는 함수
    """
    latest_backup_time = get_latest_backup_time()
    if not latest_backup_time:
        return None

    date_str = latest_backup_time[:10]  # "YYYY-MM-DD"

    if _backup_cache["date"] == date_str:
        print(f"[CACHE] 캐시된 백업 데이터 사용: {date_str}")        
        return _backup_cache["data"]

    filename = f"rank_{date_str}.json"
    local_path = f"cached_{filename}"
    firebase_path = f"backups/{filename}"

    if download_backup(firebase_path, local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            _backup_cache["date"] = date_str
            _backup_cache["data"] = json_data
            print(f"[CACHE] 백업 데이터 캐시됨: {date_str}")
            return json_data
        except FileNotFoundError:
            print(f"[ERROR] 다운로드 성공했지만 파일이 없음: {local_path}")
            return None
        except json.JSONDecodeError:
            print(f"[ERROR] JSON 파싱 실패: {local_path}")
            return None
    else:
        print(f"[ERROR] 백업 다운로드 실패: {firebase_path}")
        return None
