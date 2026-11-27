import algo
import redis_process
from psycopg.rows import scalar_row
import models

def launch_algo_unique(user_id: int,args:models.Args):
    conn = algo.get_connection_db()
    if conn is None:
        print("Database connection failed. Test aborted.")
        return
        
    args = algo.Args()
    results = algo.algoSimple(user_id,args)
    redis_process.save_pool(str(user_id), results,args)
    print(f"Results for user {user_id} saved to Redis.")

def launch_algo(args:models.Args):
    conn = algo.get_connection_db()
    if conn is None:
        print("Database connection failed. Test aborted.")
        return
    with conn.cursor(row_factory=scalar_row) as cur:
        cur.execute("SELECT id FROM up_users WHERE blocked = false;")
        users = cur.fetchall()
        for user in users:
            launch_algo_unique(user,args)
launch_algo(models.Args())
