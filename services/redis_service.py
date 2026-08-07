import redis

redis_client = redis.Redis(
    host="redis",
    #host="localhost",
    port=6379,
    decode_responses=True
)

