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