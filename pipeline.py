import algo
import redis_process
from psycopg.rows import scalar_row

def launch_algo_unique(user_id: int):
    conn = algo.get_connection_db()
    if conn is None:
        print("Database connection failed. Test aborted.")
        return
        
    args = algo.Args(user_id=user_id)
    results = algo.algoSimple(args)
    redis_process.save_pool(str(user_id), results)
    print(f"Results for user {user_id} saved to Redis.")

def launch_algo():
    conn = algo.get_connection_db()
    if conn is None:
        print("Database connection failed. Test aborted.")
        return
    with conn.cursor(row_factory=scalar_row) as cur:
        cur.execute("SELECT id FROM up_users WHERE blocked = false;")
        users = cur.fetchall()
        for user in users:
            launch_algo_unique(user)
launch_algo()
