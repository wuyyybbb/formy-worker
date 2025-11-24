"""
外部 API Engine
负责调用闭源模型 API
"""
import requests
import time
from typing import Any, Dict, Optional

from app.services.image.engines.base import EngineBase, EngineType
from app.utils.image_io import image_to_base64, base64_to_image


class ExternalApiEngine(EngineBase):
    """外部 API Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化外部 API Engine
        
        Args:
            config: API 配置（包含 api_url, api_key 等）
        """
        super().__init__(config)
        self.engine_type = EngineType.EXTERNAL_API
        
        # 从配置中获取 API 信息
        self.api_url = self.get_config("api_url")
        self.api_key = self.get_config("api_key")
        self.timeout = self.get_config("timeout", 60)
        self.retry_times = self.get_config("retry_times", 3)
        self.retry_delay = self.get_config("retry_delay", 2)
        
        # 请求方法（GET/POST）
        self.method = self.get_config("method", "POST").upper()
        
        # 是否需要图片 base64 编码
        self.encode_images = self.get_config("encode_images", True)
    
    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        执行 API 调用
        
        Args:
            input_data: 输入数据（可以是字典或图片路径）
            **kwargs: 其他参数
            
        Returns:
            Any: API 响应结果
        """
        self._log(f"调用外部 API: {self.api_url}")
        
        # 1. 验证输入
        if not self.validate_input(input_data):
            raise ValueError("输入数据验证失败")
        
        # 2. 准备请求数据
        request_data = self._prepare_request(input_data, **kwargs)
        
        # 3. 带重试的 API 调用
        response = self._call_api_with_retry(request_data)
        
        # 4. 解析响应
        result = self._parse_response(response)
        
        self._log("API 调用成功")
        
        return result
    
    def validate_input(self, input_data: Any) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 是否有效
        """
        # 基础验证
        if input_data is None:
            return False
        
        # 如果是字典，检查必要字段
        if isinstance(input_data, dict):
            # 可以根据具体 API 要求验证字段
            return True
        
        # 如果是字符串（图片路径），检查文件是否存在
        if isinstance(input_data, str):
            from pathlib import Path
            return Path(input_data).exists()
        
        return True
    
    def _prepare_request(self, input_data: Any, **kwargs) -> Dict:
        """
        准备请求数据
        
        Args:
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            Dict: 请求数据
        """
        request_data = {}
        
        # 如果输入是字典，直接使用
        if isinstance(input_data, dict):
            request_data = input_data.copy()
        
        # 如果输入是图片路径字符串，转换为 base64
        elif isinstance(input_data, str) and self.encode_images:
            request_data["image"] = image_to_base64(input_data)
        
        # 合并额外参数
        request_data.update(kwargs)
        
        # 从配置中添加额外参数
        extra_params = self.get_config("extra_params", {})
        request_data.update(extra_params)
        
        return request_data
    
    def _call_api(self, request_data: Dict) -> Any:
        """
        调用 API
        
        Args:
            request_data: 请求数据
            
        Returns:
            Any: API 响应
        """
        # 构建请求头
        headers = {
            "Content-Type": "application/json"
        }
        
        # 添加认证信息
        if self.api_key:
            auth_type = self.get_config("auth_type", "Bearer")
            if auth_type == "Bearer":
                headers["Authorization"] = f"Bearer {self.api_key}"
            elif auth_type == "ApiKey":
                headers["X-API-Key"] = self.api_key
            elif auth_type == "Custom":
                # 自定义认证头
                auth_header = self.get_config("auth_header", "Authorization")
                headers[auth_header] = self.api_key
        
        try:
            # 发送请求
            if self.method == "POST":
                response = requests.post(
                    self.api_url,
                    json=request_data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif self.method == "GET":
                response = requests.get(
                    self.api_url,
                    params=request_data,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"不支持的请求方法: {self.method}")
            
            # 检查响应状态
            response.raise_for_status()
            
            # 返回 JSON 响应
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception(f"API 请求超时: {self.api_url}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API 请求失败: {e.response.status_code}, {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求异常: {str(e)}")
    
    def _call_api_with_retry(self, request_data: Dict) -> Any:
        """
        带重试的 API 调用
        
        Args:
            request_data: 请求数据
            
        Returns:
            Any: API 响应
        """
        last_exception = None
        
        for attempt in range(self.retry_times):
            try:
                return self._call_api(request_data)
            except Exception as e:
                last_exception = e
                self._log(f"API 调用失败（第 {attempt + 1}/{self.retry_times} 次）: {e}", "WARNING")
                
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)
        
        # 所有重试都失败
        raise Exception(f"API 调用失败（已重试 {self.retry_times} 次）: {last_exception}")
    
    def _parse_response(self, response: Any) -> Any:
        """
        解析 API 响应
        
        Args:
            response: API 响应
            
        Returns:
            Any: 解析后的结果
        """
        # 检查响应格式
        if not isinstance(response, dict):
            return response
        
        # 检查是否有错误
        if "error" in response:
            raise Exception(f"API 返回错误: {response['error']}")
        
        # 根据配置的响应字段提取结果
        result_key = self.get_config("result_key", "result")
        
        if result_key in response:
            result = response[result_key]
        else:
            result = response
        
        # 如果结果是 base64 图片，解码
        if self.get_config("decode_result", False):
            if isinstance(result, str):
                try:
                    result = base64_to_image(result)
                except Exception:
                    pass  # 如果不是 base64，保持原样
            elif isinstance(result, dict) and "image" in result:
                try:
                    result["image"] = base64_to_image(result["image"])
                except Exception:
                    pass
        
        return result
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: API 是否可用
        """
        try:
            # 简单检查配置是否完整
            if not self.api_url:
                return False
            
            # 尝试发送健康检查请求
            health_url = self.get_config("health_check_url")
            if health_url:
                response = requests.get(health_url, timeout=5)
                return response.status_code == 200
            
            return True
            
        except Exception:
            return False

