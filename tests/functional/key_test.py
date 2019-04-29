import redis
import time
from assert_helper import *
from conn import *

def test_type():
    conn = get_redis_conn()
    string_key = "test_string_type"
    ret = conn.set(string_key, "bar")
    assert(ret == True)
    ret = conn.type(string_key)
    assert(ret == "string")
    hash_key = "test_hash_type"
    ret = conn.hset(hash_key, "f1", "v1")
    assert(ret == 1)
    ret = conn.type(hash_key)
    assert(ret == "hash")
    list_key = "test_list_type"
    ret = conn.lpush(list_key, "v1")
    assert(ret == 1)
    ret = conn.type(list_key)
    assert(ret == "list")
    set_key = "test_set_type"
    ret = conn.sadd(set_key, "s1")
    assert(ret == 1)
    ret = conn.type(set_key)
    assert(ret == "set")
    zset_key = "test_zset_type"
    ret = conn.zadd(zset_key, "s1", 0.1)
    assert(ret == 1)
    ret = conn.type(zset_key)
    assert(ret == "zset")
    ret = conn.delete(string_key, hash_key, list_key, set_key, zset_key)
    assert(ret == 5)

def test_expire():
    key = "test_expire"
    conn = get_redis_conn()
    ret = conn.lpush(key, "v1")
    assert(ret == 1)
    ret = conn.expire(key, 2)
    assert(ret == 1)
    ret = conn.ttl(key)
    assert(ret >= 1 and ret <= 2)
    time.sleep(3)
    ret = conn.exists(key)
    assert(ret == False)
    
def test_exists():
    key = "test_exists"
    conn = get_redis_conn()
    ret = conn.set(key, "bar")
    assert(ret)
    ret = conn.exists(key)
    assert(ret)
    ret = conn.delete(key)
    assert(ret == 1)
    ret = conn.exists(key)
    assert(not ret)

def test_ttl():
    key = "test_ttl"
    conn = get_redis_conn()
    ret = conn.set(key, "bar")
    assert(ret)
    ret = conn.ttl(key)
    assert(ret == None)
    ret = conn.ttl("notexistskey")
    assert(ret == None)
    ret = conn.expire(key, 2)
    assert(ret == 1)
    ret = conn.ttl(key)
    assert(ret >= 1 and ret <= 2)

def test_persist():
    key = "test_persist"
    conn = get_redis_conn()
    ret = conn.persist(key)
    assert(not ret)
    ret = conn.set(key, "bar")
    assert(ret)
    ret = conn.persist(key)
    assert(not ret)
    ret = conn.expire(key, 100)
    assert(ret == 1)
    ret = conn.persist(key)
    assert(ret)
    ret = conn.delete(key)
    assert(ret == 1)

def test_expireat():
    key = "test_expireat"
    conn = get_redis_conn()
    ret = conn.sadd(key, "s1")
    assert(ret == 1)
    ret = conn.expireat(key, time.time()+2)
    assert(ret == 1)
    ret = conn.ttl(key)
    assert(ret >= 1 and ret <= 2)
    time.sleep(3)
    ret = conn.exists(key)
    assert(ret == False)

def test_pexpire():
    key = "test_pexpire"
    conn = get_redis_conn()
    ret = conn.hset(key, "f1", "v1")
    assert(ret == 1)
    ret = conn.pexpire(key, 2000)
    assert(ret == 1)
    ret = conn.pttl(key)
    assert(ret >= 1000 and ret <= 2000)
    time.sleep(3)
    ret = conn.exists(key)
    assert(ret == False)

def test_pexpireat():
    key = "test_pexpireat"
    conn = get_redis_conn()
    ret = conn.sadd(key, "s1")
    assert(ret == 1)
    ret = conn.pexpireat(key, (time.time()+2)*1000)
    assert(ret == 1)
    ret = conn.pttl(key)
    assert(ret >= 1000 and ret <= 2000)
    time.sleep(3)
    ret = conn.exists(key)
    assert(ret == False)
    
def test_pttl():
    key = "test_ttl"
    conn = get_redis_conn()
    ret = conn.set(key, "bar")
    assert(ret)
    ret = conn.ttl(key)
    assert(ret == None)
    ret = conn.ttl("notexistskey")
    assert(ret == None)
    ret = conn.pexpire(key, 2000)
    assert(ret == 1)
    ret = conn.ttl(key)
    assert(ret >= 1 and ret <= 2)

    ret = conn.delete(key)
    assert(ret == 1)

def test_randomkey():
    keys = ["test_randomkey", "test_randomkey_1", "test_randomkey_2"]
    conn = get_redis_conn()
    for key in keys:
        ret = conn.set(key, "bar")
        assert(ret)

    ret = conn.execute_command("RANDOMKEY")
    assert(ret in keys)

    for key in keys:
        ret = conn.delete(key)
        assert(ret == 1)


