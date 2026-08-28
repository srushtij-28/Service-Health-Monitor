import json
import os
import time
import redis
import requests

client=redis.Redis.from_url(os.getenv("REDIS_URL","redis://redis:6379/0"),decode_responses=True)
PREFIX="day313:service:"

def check(key):
    raw=client.get(key)
    if not raw: return
    data=json.loads(raw)
    start=time.perf_counter()
    try:
        response=requests.get(data["url"],timeout=5)
        response.raise_for_status()
        data["status"]="up"
        data["successes"]+=1
        data["consecutive_failures"]=0
    except requests.RequestException:
        data["status"]="down"
        data["failures"]+=1
        data["consecutive_failures"]+=1
    data["checks"]+=1
    data["last_response_ms"]=round((time.perf_counter()-start)*1000,2)
    client.set(key,json.dumps(data))

def run():
    print("Health monitor started",flush=True)
    while True:
        try:
            for key in list(client.scan_iter(match=PREFIX+"*")):
                check(key)
        except redis.RedisError as exc:
            print(f"Redis error: {exc}",flush=True)
        time.sleep(10)

if __name__=="__main__":
    run()
