import os
import time
import json
from flask import Flask, render_template
from ranking.api import get_ranking_data
from ranking.utils import (
    parse_players,
    calculate_champion_stats,
    should_backup_based_on_time,
    compare_rankings
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
from ranking.firebase_manager import (
    upload_backup,
    download_backup,
    get_latest_backup_time,
    set_latest_backup_time,
)
from datetime import datetime
from ranking.backup_cache import get_cached_backup_data


app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["45 per minute"]
)

# -----------------백업 실행 함수---------------------

def try_backup_if_needed(user_ids):
    now = datetime.now()
    now_time = now.strftime("%Y-%m-%d %H:%M:%S")
    last_backup = get_latest_backup_time() or "없음"

    if should_backup_based_on_time(last_backup):
        valid_uid = get_valid_user_id(user_ids, team_mode=1)
        solo_data = get_ranking_data(valid_uid, teamMode=1)
        trio_data = get_ranking_data(valid_uid, teamMode=2)

        solo_players = parse_players(solo_data["data"]["players"])
        trio_players = parse_players(trio_data["data"]["players"])

        with open("ranking_backup.json", "w", encoding="utf-8") as f:
            json.dump({"solo": solo_players, "trio": trio_players}, f, ensure_ascii=False)

        upload_backup("ranking_backup.json", f"backups/rank_{now_time[:10]}.json")
        set_latest_backup_time()
        print("[백업] Firebase에 최신 랭킹 백업 완료")
        return True, now_time

    return False, now_time
    

# ------------------- userID 캐시 및 우선순위 -------------------
CACHE_TTL = 3600  # 1시간 유지
_user_cache = {
    "uid": None,
    "timestamp": 0
}
_user_queue = []  # 순서 정보

def rotate_user_queue(user_id):
    """유효하지 않은 userNetID를 뒤로 보냄"""
    if user_id in _user_queue:
        _user_queue.remove(user_id)
    _user_queue.append(user_id)

def prioritize_user(user_id):
    """가장 앞쪽으로 우선순위 높임"""
    if user_id in _user_queue:
        _user_queue.remove(user_id)
    _user_queue.insert(0, user_id)

def get_valid_user_id(user_ids, team_mode):
    """캐시 검사 후 유효 userNetID 반환"""
    now = time.time()
    cached_uid = _user_cache["uid"]

    if cached_uid and now - _user_cache["timestamp"] < CACHE_TTL:
        try:
            get_ranking_data(cached_uid, teamMode=team_mode)
            return cached_uid
        except:
            print(f"[INFO] 캐시된 {cached_uid} 비활성화 → 순환 시작")
            rotate_user_queue(cached_uid)

    for uid in user_ids:
        try:
            get_ranking_data(uid, teamMode=team_mode)
            print(f"[INFO] 유효한 userNetID 사용됨: {uid}")
            _user_cache["uid"] = uid
            _user_cache["timestamp"] = now
            print(f"[INFO] {uid} 가 1시간 동안 캐싱 됨.")
            prioritize_user(uid)
            return uid
        except Exception as e:
            print(f"[{uid}] 데이터 요청 실패: {e}")
            rotate_user_queue(uid)
            time.sleep(0.3)

    raise Exception("모든 userNetID에서 데이터를 받아오지 못했습니다.")
    
    
# -------------------- 라우팅 --------------------
    
@app.route('/')
def index():
    user_ids = os.environ.get("userNetIDs", "").split(",")
 
    # 큐 초기화 (처음만 실행)
    global _user_queue
    if not _user_queue:
        _user_queue = user_ids.copy()

    if not user_ids:
        print("[ERROR] userNetID 목록이 비어 있음")
        return render_template("index.html", error=True)
        
    try:
        last_backup = get_latest_backup_time() or "없음"
        did_backup, now_time = try_backup_if_needed(user_ids)
            
            
        # 솔로 모드
        valid_uid = get_valid_user_id(user_ids, team_mode=1)
        
        solo_data = get_ranking_data(valid_uid, teamMode=1)
        solo_players_data = solo_data["data"]["players"]
        solo_now = parse_players(solo_players_data)
        solo_stats = calculate_champion_stats(solo_players_data)

        # 트리오 모드
        trio_data = get_ranking_data(valid_uid, teamMode=2)
        trio_players_data = trio_data["data"]["players"]
        trio_now = parse_players(trio_players_data)
        trio_stats = calculate_champion_stats(trio_players_data)


        backup_data = get_cached_backup_data()

        if backup_data:
            solo_prev = backup_data["solo"]
            trio_prev = backup_data["trio"]

            # 이전 데이터와 비교하여 변화량 계산
            solo_players = compare_rankings(solo_prev, solo_now)
            trio_players = compare_rankings(trio_prev, trio_now)
        else:
            print("[INFO] 백업 데이터 없음 → 비교 생략")
            solo_players = [{ **p, "rank_change": "new", "score_change": None } for p in solo_now]
            trio_players = [{ **p, "rank_change": "new", "score_change": None } for p in trio_now]


        return render_template(
            "index.html",
            solo_players=solo_players,
            trio_players=trio_players,
            solo_stats=solo_stats,
            trio_stats=trio_stats,
            last_backup=last_backup,
            now_time=now_time
        )
            
    except Exception as e:
        print(f"[ERROR] 전체 실패: {e}")        
        return render_template("index.html", error=True)

@app.route("/trigger-backup")
def trigger_backup():
    try:
        user_ids = os.environ.get("userNetIDs", "").split(",")

        did_backup, now_time = try_backup_if_needed(user_ids)
        if did_backup:
            return f"[OK] 백업 완료: {now_time}"
        else:
            return "[SKIP] 오늘 이미 백업됨"

    except Exception as e:
        print(f"[ERROR] 백업 실패: {e}")
        return f"[ERROR] 백업 실패: {e}"




limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2 per minute"]  # 전체 요청 2회/분 제한
)

@app.route('/static/<path:filename>')
@limiter.limit("2 per minute")  # 정적 파일도 별도 제한
def serve_static(filename):
    print("[STATIC 제한] 요청됨:", filename)
    return send_from_directory('static', filename)




@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429
    
    
if __name__ == '__main__':
    app.run(debug=True)