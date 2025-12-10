"""
Redis 客户端工具
统一管理 Redis 连接，使用 REDIS_URL 配置
"""
import redis
from app.core.config import settings


def get_redis_client() -> redis.Redis:
    """
    获取 Redis 客户端实例
    
    统一使用 REDIS_URL 配置，不再使用 localhost
    
    Returns:
        redis.Redis: Redis 客户端实例
        
    Raises:
        ValueError: 如果 REDIS_URL 未配置
    """
    # 使用配置对象的 get_redis_url 方法（优先 REDIS_URL，否则从分散配置构建）
    redis_url = settings.get_redis_url
    
    if not redis_url:
        raise ValueError(
            "REDIS_URL 未配置。请在环境变量中设置 REDIS_URL，"
            "格式: redis://[:password@]host[:port][/db]"
        )
    
    # 打印 Redis URL（隐藏密码）以便调试
    url_display = redis_url[:30] + "..." if len(redis_url) > 30 else redis_url
    if "@" in redis_url:
        # 隐藏密码部分
        parts = redis_url.split("@")
        url_display = f"{parts[0].split('://')[0]}://****@{parts[1][:30]}..."
    print(f"[Worker Redis] 🔗 Connecting to: {url_display}")
    
    # 使用 REDIS_URL 创建连接
    redis_client = redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    
    # 测试连接
    try:
        redis_client.ping()
        print(f"[Worker Redis] ✅ Connected successfully")
    except Exception as e:
        print(f"[Worker Redis] ❌ Connection failed: {e}")
        raise
    
    return redis_client

