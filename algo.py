import os
from pathlib import Path

import pandas as pd
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

def get_Connection():
    try:
        conn = psycopg.connect(conninfo, autocommit=True)
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        return None
def Jaccard_similarity(set1: set, set2: set)-> float:
    union = set1 | set2
    intersection = set1 & set2
    return len(intersection)/len(union)

def Overlap_similarity(set1:set, set2: set)-> float:
    minBottom = min(len(set1),len(set2))
    intersection = set1 & set2
    return len(intersection)/minBottom

def algoSimple(args: args):
    conn = get_Connection()
    if conn is None:
        return
    user_id = args.user_id
    with conn.cursor(row_factory=class_row(UpUser)) as cur:
        user : UpUser | None = cur.execute(
            "SELECT id, interests FROM up_users WHERE id = %s;", (user_id,)
        ).fetchone();
        if(user is None):
            print(f"User with id {user_id} not found.")
            return
        rows : list[UpUser] = cur.execute("SELECT id, interests FROM up_users WHERE id != %s;", (user_id,)).fetchall()
        # Jaccard similarity calculation for interests
        similarities = []
        if user.interests:
            for row in rows:
                if not row.interests:
                    row.interests = []
                similarity = Jaccard_similarity(set(user.interests), set(row.interests))
                similarities.append((row.id, similarity))
        if(similarities):
            similarities.sort(key=lambda x: x[1], reverse=True)
    print(similarities)

algoSimple(args(user_id=14))



