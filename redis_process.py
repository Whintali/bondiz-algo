import redis
from models import Result
from datetime import datetime
from zoneinfo import ZoneInfo 

_redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True) # TODO change to the server ip and api key

MAX_POOL_SIZE = 100 # maximum number of results to store in the pool

ALGORITHM_VERSION = "2.0.0"
TIME_BEFORE_CONSUMPTION = 3600 # time in seconds before the pool is considered expired

def pool_key(user_id: str) -> str:
    return f"{ALGORITHM_VERSION}:pool:{user_id}"

# TODO add async
def save_pool(user_id: str, results: list[Result]) -> None:
    key = pool_key(user_id)
    tmp_key = key + ":tmp" # Avoid a not finished pool to be consumed by the user

    pipeline = _redis_client.pipeline()
    pipeline.delete(tmp_key) # Avoid the possibility of having a not finished pool
    if results:
        dateNow = datetime.now(ZoneInfo("Europe/Paris")).strftime('%Y-%m-%d %H:%M:%S%z')
        payload = {
            "generated_at": dateNow, # TODO date format to change for uniform timestamp format
            "candidates": [
                {"user_id": r.user_id,"hobbies_score":r.stat.hobbies,"desires_score": r.stat.desires, "score": r.stat.total}
                for r in results[:MAX_POOL_SIZE] 
            ],
            # HERE add info to the json redis output 
        }
        pipeline.json().set(key, "$", payload)
        pipeline.expire(key, TIME_BEFORE_CONSUMPTION)
    else : 
        pipeline.delete(pool_key(user_id)) # If no results, delete the last pool to avoid consuming an old one
    pipeline.execute()
        
