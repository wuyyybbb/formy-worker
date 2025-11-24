"""
ID 生成器工具
"""
import time
import random
import string


def generate_task_id() -> str:
    """
    生成任务 ID
    格式: task_<timestamp>_<random>
    
    Returns:
        str: 任务 ID，例如: task_1234567890_abc123
    """
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"task_{timestamp}_{random_str}"


def generate_user_id() -> str:
    """
    生成用户 ID
    格式: usr_<timestamp>_<random>
    
    Returns:
        str: 用户 ID，例如: usr_1234567890_abc123
    """
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"usr_{timestamp}_{random_str}"


def generate_file_id() -> str:
    """
    生成文件 ID
    格式: file_<timestamp>_<random>
    
    Returns:
        str: 文件 ID，例如: file_1234567890_abc123
    """
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"file_{timestamp}_{random_str}"
