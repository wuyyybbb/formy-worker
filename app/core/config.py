"""
应用配置
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "Formy"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    
    # Redis 配置
    # 方式1: 使用完整的 Redis URL (优先，适合 Render 等云平台)
    REDIS_URL: Optional[str] = None
    # 方式2: 分别配置各项（备选）
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"          # 上传文件存储目录
    RESULT_DIR: str = "./results"          # 结果文件存储目录
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 最大上传文件大小（10MB）
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    
    # 任务配置
    TASK_RETENTION_DAYS: int = 7           # 任务结果保留天数
    MAX_CONCURRENT_TASKS_PER_USER: int = 3 # 每用户最大并发任务数
    
    # JWT 配置
    # 支持 JWT_SECRET 和 SECRET_KEY（向后兼容）
    JWT_SECRET: Optional[str] = None
    SECRET_KEY: str = "formy-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    @property
    def get_jwt_secret(self) -> str:
        """获取 JWT 密钥（优先使用 JWT_SECRET，否则使用 SECRET_KEY）"""
        return self.JWT_SECRET or self.SECRET_KEY
    
    # CORS 配置
    # 支持 Vercel 预览域名和生产域名
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://formy-frontend.vercel.app,https://*.vercel.app"
    
    @property
    def get_cors_origins(self) -> list:
        """解析 CORS 配置（支持逗号分隔的字符串和通配符）"""
        if isinstance(self.CORS_ORIGINS, str):
            origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            # 处理通配符：将 *.vercel.app 转换为所有匹配的域名
            # 注意：FastAPI CORSMiddleware 不支持通配符，需要明确列出
            # 这里我们返回所有配置的域名，通配符需要在运行时动态匹配
            return origins
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else []
    
    # Engine 配置文件路径
    ENGINE_CONFIG_PATH: str = "./engine_config.yml"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()

