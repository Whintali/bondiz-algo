import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo
from psycopg.rows import class_row
from models import *
from collections import defaultdict


load_dotenv(Path(__file__).resolve().parent / ".env.dev")



# Database connection information
conninfo = make_conninfo(
            host=os.environ["SUPABASE_DB_HOST"], # TODO transfer env 
            port=os.environ["SUPABASE_DB_PORT"],
            dbname=os.environ["SUPABASE_DB_NAME"],
            user=os.environ["SUPABASE_DB_USER"],
            password=os.environ["SUPABASE_DB_PASSWORD"],
            sslmode="require",
        )


def get_connection_db():
    try:
        conn = psycopg.connect(conninfo, autocommit=True)
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        return None
def jaccard_similarity(set1: set, set2: set)-> float:
    if(len(set1) == 0  or len(set2) == 0):
        return 0.0
    union = set1 | set2
    intersection = set1 & set2
    if len(union) == 0:
        return 0.0
    return len(intersection)/len(union)

def overlap_similarity(set1:set, set2: set)-> float:
    if(len(set1) == 0  or len(set2) == 0):
       return 0.0
    minBottom = min(len(set1),len(set2))
    intersection = set1 & set2
    if(minBottom == 0):
        return 0.0
    return len(intersection)/minBottom

# Mix of Jaccard and Overlap similarity
def mix_similarity(set1:set, set2: set, weight_jaccard: int, weight_overlap: int)-> float:
    jaccard = jaccard_similarity(set1, set2)
    overlap = overlap_similarity(set1, set2)
    if(weight_jaccard + weight_overlap == 0):
        return 0.0
    return (jaccard * weight_jaccard + overlap * weight_overlap) / (weight_jaccard + weight_overlap)

# def profilesCreation(interest_list : list[Interest]) -> dict[int,list[Interest]]:
#     result = defaultdict(list)
#     for interest in interest_list:
#         if(result[interest.user_id] == None) :
#             result[interest.user_id] = []
#         result[interest.user_id].append(Interest(interest.user_id,interest.interest_id,interest.importance))
#     # hobbies_list: list[Interest] = 
#     return result

def profilesCreation(links: list[tuple[int, int]]) -> dict[int, set[int]]:
    profiles: dict[int, set[int]] = defaultdict(set)
    for user_id, interest_id in links:
        profiles[user_id].add(interest_id)
    # hobbies_list: list[Interest] = 
    return profiles

def algoSimple(user_id:int,args: Args) -> list[Result]:
    conn = get_connection_db()
    if conn is None:
        return []
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM up_users WHERE id = %s and blocked = false;", (user_id,)
            )
            if(cur.fetchone() is None):
                print(f"User with id {user_id} not found or blocked.")
                return []
            # TODO add blocked users by the current user of the query and users who have blocked the current user to the query
            cur.execute("select u.id from up_users as u where not exists(select 1 from likes_from_user_lnk as l where l.like_id = u.id and l.user_id = %s) and not exists(select 1 from profile_views_viewer_lnk as pviewer inner join profile_views_viewed_lnk pviewed on pviewed.profile_view_id = pviewer.profile_view_id where pviewer.user_id = %s and pviewed.user_id = u.id) and u.id != %s and u.blocked = false;", (user_id, user_id, user_id))
            candidate_ids : list[int] = [row[0] for row in cur.fetchall()]
            if not candidate_ids:
                return []

            cur.execute(
                "select user_id, interest_id from up_users_interest_tags_lnk where user_id = any(%s) and interest_id is not null;",
                ([user_id] + candidate_ids,),
            )
            profiles = profilesCreation(cur.fetchall())

    user_interests = profiles.get(user_id, set())
    # Jaccard similarity calculation for interests
    similarities : list[Result]  = []
    if user_interests:
        for candidate_id in candidate_ids:
            #similarity = jaccard_similarity(set(user.interests["desires"]), set(row.interests["desires"])) if user.interests and row.interests else 0.0
            # similarity_desires = mix_similarity(set(user.interests["desires"]), set(row.interests["desires"]),args.weight_jaccard,args.weight_overlap)
            # similarity_hobbies = mix_similarity(set(user.interests["hobbies"]), set(row.interests["hobbies"]),args.weight_jaccard,args.weight_overlap)
            # similarity_total = (similarity_desires * args.weight_desires + similarity_hobbies * args.weight_hobbies) / (args.weight_desires + args.weight_hobbies) if (args.weight_desires + args.weight_hobbies) > 0 else 0.0
            similarity_hobbies = mix_similarity(user_interests, profiles.get(candidate_id, set()), args.weight_jaccard, args.weight_overlap)
            similarities.append(Result(candidate_id,FinalStats(0,similarity_hobbies,0)))
    if(similarities):
        similarities.sort(key=lambda x: x.stat.hobbies, reverse=True)
    return similarities



