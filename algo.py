import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo
from psycopg.rows import class_row
from models import *


load_dotenv(Path(__file__).resolve().parent / ".env.dev")



# Database connection information
conninfo = make_conninfo(
            host="aws-1-eu-west-1.pooler.supabase.com",
            port=5432,
            dbname="postgres",
            user="postgres.gbmnhatquzrmhtpdqsqp",
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
    if(set1 == [] or set2 == []):
        return 0.0
    union = set1 | set2
    intersection = set1 & set2
    if len(union) == 0:
        return 0.0
    return len(intersection)/len(union)

def overlap_similarity(set1:set, set2: set)-> float:
    if(set1 == [] or set2 == []):
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

def algoSimple(args: Args) -> list[Result]:
    conn = get_connection_db()
    if conn is None:
        return []
    user_id = args.user_id
    with conn.cursor(row_factory=class_row(UpUser)) as cur:
        user : UpUser | None = cur.execute(
            "SELECT id, interests FROM up_users WHERE id = %s and blocked = false;", (user_id,)
        ).fetchone();
        if(user is None):
            print(f"User with id {user_id} not found or blocked.")
            return []
        # TODO add blocked users by the current user of the query and users who have blocked the current user to the query 
        rows : list[UpUser] = cur.execute("select u.id, u.interests from up_users as u where not exists(select 1 from likes_from_user_lnk as l where l.like_id = u.id and l.user_id = %s) and not exists(select 1 from profile_views_viewer_lnk as pviewer inner join profile_views_viewed_lnk pviewed on pviewed.profile_view_id = pviewer.profile_view_id where pviewer.user_id = %s and pviewed.user_id = u.id) and u.id != %s and u.blocked = false;", (user_id, user_id, user_id)).fetchall()
        # Jaccard similarity calculation for interests
        similarities : list[Result]  = []
        if user.interests:
            for row in rows:
                if not row.interests:
                    row.interests = {
                        "desires": [],
                        "hobbies": []
                    }
                #similarity = jaccard_similarity(set(user.interests["desires"]), set(row.interests["desires"])) if user.interests and row.interests else 0.0
                similarity_desires = mix_similarity(set(user.interests["desires"]), set(row.interests["desires"]),args.weight_jaccard,args.weight_overlap)
                similarity_hobbies = mix_similarity(set(user.interests["hobbies"]), set(row.interests["hobbies"]),args.weight_jaccard,args.weight_overlap)
                similarity_total = (similarity_desires * args.weight_desires + similarity_hobbies * args.weight_hobbies) / (args.weight_desires + args.weight_hobbies) if (args.weight_desires + args.weight_hobbies) > 0 else 0.0
                similarities.append(Result(row.id,FinalStats(similarity_desires,similarity_hobbies,similarity_total)))
        if(similarities):
            similarities.sort(key=lambda x: x.stat.total, reverse=True)
        return similarities



