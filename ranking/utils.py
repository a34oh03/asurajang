import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

champion_map = {
    1: "바쥬", 2: "파이라", 3: "바라타", 4: "무이무이", 5: "등오",
    6: "하누만", 7: "비카랄라", 8: "유안", 9: "여울", 10: "테타누치",
    11: "카이사치", 12: "레이", 13: "웨이", 17: "쇼요"
}    
    
def parse_players(players_raw):
    players = []
    for i in range(0, len(players_raw), 4):
        try:
            nickname = players_raw[i]
            score = int(players_raw[i + 1])
            champ_id = int(players_raw[i + 2])
            champion = champion_map.get(champ_id, f"알 수 없음({champ_id})")
            players.append({
                "rank": i // 4 + 1,
                "nickname": nickname,
                "score": score,
                "champion": champion
            })
        except:
            continue
    return players

def calculate_champion_stats(players_raw):
    counter = defaultdict(int)
    for i in range(0, len(players_raw), 4):
        try:
            champ_id = int(players_raw[i + 2])
            counter[champ_id] += 1
        except:
            continue
    # 모든 캐릭터 포함시키기
    full_stats = {cid: counter.get(cid, 0) for cid in champion_map.keys()}

    sorted_champs = sorted(full_stats.items(), key=lambda x: x[1], reverse=True)
    labels = [champion_map.get(cid, str(cid)) for cid, _ in sorted_champs]
    counts = [count for _, count in sorted_champs]
    return {"labels": labels, "counts": counts}
    
def should_backup_based_on_time(last_backup_str: str) -> bool:
    """
    - 오늘 00:00 이후 처음으로 실행되면 백업 수행
    - 이미 오늘 중에 한 번 백업되었으면 스킵
    """
    now = datetime.now()

    if not last_backup_str or last_backup_str == "없음":
        return True

    try:
        last_backup = datetime.strptime(last_backup_str, "%Y-%m-%d %H:%M:%S")
    except:
        return True

    # 오늘 00:00 기준 시각
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if last_backup < today_start:
        print("[INFO] 오늘 아직 백업 안 됨 → 백업 수행")
        return True
    else:
        print("[INFO] 오늘 이미 백업됨 → 생략")
        return False
        


def compare_rankings(prev, curr):
    """
    이전 랭킹(prev)과 현재 랭킹(curr)을 비교하여,
    등수 변화(rank_change), 점수 변화(score_change), 신규 진입 여부를 추가함.
    """

    # 이전 플레이어 정보 맵: nickname -> (rank, score)
    prev_map = {p["nickname"]: (i + 1, p["score"]) for i, p in enumerate(prev)}
    result = []

    for i, player in enumerate(curr):
        cur_rank = i + 1
        nickname = player["nickname"]
        score = player["score"]
        champion = player.get("champion", "-")

        if nickname not in prev_map:
            # 백업에 없던 신규 유저
            rank_change = "new"
            score_change = None
        else:
            prev_rank, prev_score = prev_map[nickname]
            rank_change = prev_rank - cur_rank  # 상승: 양수, 하락: 음수
            score_change = score - prev_score

        result.append({
            "rank": cur_rank,
            "nickname": nickname,
            "champion": champion,
            "score": score,
            "rank_change": rank_change,
            "score_change": score_change
        })

    return result