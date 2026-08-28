import json
import os
import redis
from flask import Flask,jsonify,request

app=Flask(__name__)
client=redis.Redis.from_url(os.getenv("REDIS_URL","redis://redis:6379/0"),decode_responses=True)
PREFIX="day313:service:"

DEFAULT={"api":{"name":"api","url":"http://api:5000/health"}}

def seed():
    for name,data in DEFAULT.items():
        key=PREFIX+name
        if not client.exists(key):
            client.set(key,json.dumps({
                **data,"status":"unknown","checks":0,"successes":0,
                "failures":0,"consecutive_failures":0,"last_response_ms":None
            }))

@app.get("/")
def home():
    return jsonify(service="day313-health-monitor",message="Service health monitor is running")

@app.get("/health")
def health():
    try:
        client.ping()
        return jsonify(status="healthy",redis="connected")
    except redis.RedisError:
        return jsonify(status="unhealthy"),503

@app.get("/services")
def services():
    seed()
    result=[]
    for key in client.scan_iter(match=PREFIX+"*"):
        data=json.loads(client.get(key))
        checks=data["checks"]
        data["uptime_percent"]=round(data["successes"]/checks*100,2) if checks else 0
        result.append(data)
    return jsonify(services=result)

@app.get("/services/<name>")
def service(name):
    raw=client.get(PREFIX+name)
    if not raw:
        return jsonify(error="service not found"),404
    data=json.loads(raw)
    checks=data["checks"]
    data["uptime_percent"]=round(data["successes"]/checks*100,2) if checks else 0
    return jsonify(data)

@app.post("/services")
def add_service():
    data=request.get_json(silent=True) or {}
    name,url=data.get("name"),data.get("url")
    if not name or not url:
        return jsonify(error="name and url are required"),400
    if client.exists(PREFIX+name):
        return jsonify(error="service already exists"),409
    item={"name":name,"url":url,"status":"unknown","checks":0,"successes":0,
          "failures":0,"consecutive_failures":0,"last_response_ms":None}
    client.set(PREFIX+name,json.dumps(item))
    return jsonify(item),201

if __name__=="__main__":
    seed()
    app.run(host="0.0.0.0",port=5000)
