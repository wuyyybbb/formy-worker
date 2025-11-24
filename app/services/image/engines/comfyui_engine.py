"""
ComfyUI Engine
负责调用本地 ComfyUI 工作流
"""
import json
import requests
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from app.services.image.engines.base import EngineBase, EngineType


class ComfyUIEngine(EngineBase):
    """ComfyUI Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 ComfyUI Engine
        
        Args:
            config: ComfyUI 配置（包含 comfyui_url, workflow_path 等）
        """
        super().__init__(config)
        self.engine_type = EngineType.COMFYUI
        
        # 从配置中获取 ComfyUI 信息
        self.comfyui_url = self.get_config("comfyui_url", "http://localhost:8188")
        self.workflow_path = self.get_config("workflow_path")
        self.timeout = self.get_config("timeout", 300)
        self.poll_interval = self.get_config("poll_interval", 2)  # 轮询间隔（秒）
        
        # 客户端 ID（用于识别）
        self.client_id = str(uuid.uuid4())
    
    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        执行 ComfyUI 工作流
        
        Args:
            input_data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            Any: 工作流执行结果
        """
        self._log(f"执行 ComfyUI 工作流: {self.workflow_path}")
        
        # 1. 验证输入
        if not self.validate_input(input_data):
            raise ValueError("输入数据验证失败")
        
        # 2. 加载工作流定义
        workflow = self._load_workflow()
        
        # 3. 注入输入数据
        workflow_with_input = self._inject_input(workflow, input_data, **kwargs)
        
        # 4. 提交工作流
        prompt_id = self._submit_workflow(workflow_with_input)
        
        # 5. 等待执行完成
        result = self._wait_for_completion(prompt_id)
        
        self._log("ComfyUI 工作流执行成功")
        
        return result
    
    def validate_input(self, input_data: Any) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 是否有效
        """
        # 检查工作流文件是否存在
        if self.workflow_path and not Path(self.workflow_path).exists():
            self._log(f"工作流文件不存在: {self.workflow_path}", "ERROR")
            return False
        
        return True
    
    def _load_workflow(self) -> Dict:
        """
        加载工作流定义
        
        Returns:
            Dict: 工作流 JSON
        """
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            
            self._log(f"工作流加载成功: {self.workflow_path}")
            return workflow
            
        except Exception as e:
            raise Exception(f"加载工作流失败: {e}")
    
    def _inject_input(self, workflow: Dict, input_data: Any, **kwargs) -> Dict:
        """
        注入输入数据到工作流
        
        根据节点命名规则注入：
        - input:raw_image:1 -> 原始图片
        - input:pose_image:2 -> 姿势参考图
        
        Args:
            workflow: 工作流定义（可能是节点列表格式或 prompt 格式）
            input_data: 输入数据（可以是文件路径或字典）
            **kwargs: 其他参数（如 raw_image_path, pose_image_path）
            
        Returns:
            Dict: 注入后的工作流（prompt 格式，以节点 ID 为键）
        """
        import os
        from pathlib import Path
        
        # 处理输入数据
        if isinstance(input_data, dict):
            # 如果输入是字典，提取图片路径
            raw_image_path = input_data.get("raw_image") or input_data.get("source_image")
            pose_image_path = input_data.get("pose_image") or input_data.get("reference_image")
        else:
            # 如果输入是字符串，假设是原始图片路径
            raw_image_path = input_data
            pose_image_path = None
        
        # 从 kwargs 中获取（优先级更高）
        raw_image_path = kwargs.get("raw_image_path") or kwargs.get("source_image") or raw_image_path
        pose_image_path = kwargs.get("pose_image_path") or kwargs.get("reference_image") or pose_image_path
        
        # 转换工作流格式：从节点列表格式转换为 prompt 格式（以节点 ID 为键）
        prompt = {}
        nodes = workflow.get("nodes", [])
        
        # 如果 workflow 已经是 prompt 格式（以节点 ID 为键），直接使用
        if not nodes and isinstance(workflow, dict):
            # 检查是否是 prompt 格式
            is_prompt_format = all(isinstance(k, (int, str)) and isinstance(v, dict) for k, v in workflow.items() if k not in ["nodes", "links", "extra", "config"])
            if is_prompt_format:
                prompt = workflow.copy()
            else:
                # 从节点列表构建 prompt
                for node in workflow.get("nodes", []):
                    node_id = node.get("id")
                    if node_id is not None:
                        prompt[str(node_id)] = node
        else:
            # 从节点列表构建 prompt
            for node in nodes:
                node_id = node.get("id")
                if node_id is not None:
                    prompt[str(node_id)] = node.copy()
        
        # 查找输入节点
        raw_image_node_id = None
        pose_image_node_id = None
        
        for node_id, node in prompt.items():
            title = node.get("title", "")
            if title == "input:raw_image:1":
                raw_image_node_id = node_id
            elif title == "input:pose_image:2":
                pose_image_node_id = node_id
        
        # 注入原始图片
        if raw_image_path and raw_image_node_id:
            # 上传图片到 ComfyUI
            uploaded_filename = self._upload_image_to_comfyui(raw_image_path)
            if uploaded_filename:
                # 设置节点输入
                if "inputs" not in prompt[raw_image_node_id]:
                    prompt[raw_image_node_id]["inputs"] = {}
                # LoadImage 节点使用 "image" 字段
                prompt[raw_image_node_id]["inputs"]["image"] = uploaded_filename
                self._log(f"已注入原始图片到节点 {raw_image_node_id}: {uploaded_filename}")
        
        # 注入姿势参考图
        if pose_image_path and pose_image_node_id:
            # 上传图片到 ComfyUI
            uploaded_filename = self._upload_image_to_comfyui(pose_image_path)
            if uploaded_filename:
                # 设置节点输入
                if "inputs" not in prompt[pose_image_node_id]:
                    prompt[pose_image_node_id]["inputs"] = {}
                prompt[pose_image_node_id]["inputs"]["image"] = uploaded_filename
                self._log(f"已注入姿势参考图到节点 {pose_image_node_id}: {uploaded_filename}")
        
        return prompt
    
    def _submit_workflow(self, workflow: Dict) -> str:
        """
        提交工作流到 ComfyUI
        
        Args:
            workflow: 工作流定义
            
        Returns:
            str: Prompt ID
        """
        try:
            # 构建提交数据
            payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            # 发送请求
            url = f"{self.comfyui_url}/prompt"
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            prompt_id = result.get("prompt_id")
            
            if not prompt_id:
                raise Exception("未获取到 prompt_id")
            
            self._log(f"工作流已提交，Prompt ID: {prompt_id}")
            
            return prompt_id
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"提交工作流失败: {e}")
        except Exception as e:
            raise Exception(f"提交工作流异常: {e}")
    
    def _wait_for_completion(self, prompt_id: str) -> Any:
        """
        等待工作流执行完成
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            Any: 执行结果
        """
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"工作流执行超时: {self.timeout}秒")
            
            # 查询执行状态
            status = self._get_prompt_status(prompt_id)
            
            if status == "completed":
                # 获取输出结果
                result = self._get_output(prompt_id)
                return result
            
            elif status == "failed":
                raise Exception("工作流执行失败")
            
            elif status == "executing":
                # 继续等待
                time.sleep(self.poll_interval)
            
            else:
                # 未知状态
                time.sleep(self.poll_interval)
    
    def _get_prompt_status(self, prompt_id: str) -> str:
        """
        获取 Prompt 执行状态
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            str: 状态（executing / completed / failed）
        """
        try:
            # 查询历史记录
            url = f"{self.comfyui_url}/history/{prompt_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                history = response.json()
                
                if prompt_id in history:
                    prompt_history = history[prompt_id]
                    
                    # 检查是否有输出
                    if "outputs" in prompt_history:
                        return "completed"
                    
                    # 检查是否有错误
                    if "status" in prompt_history:
                        status_info = prompt_history["status"]
                        if status_info.get("status_str") == "error":
                            return "failed"
                    
                    return "executing"
            
            return "executing"
            
        except Exception as e:
            self._log(f"查询状态失败: {e}", "WARNING")
            return "executing"
    
    def _get_output(self, prompt_id: str) -> Any:
        """
        获取工作流输出
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            Any: 输出数据，包含 output_image 和 comparison_image
        """
        try:
            # 查询历史记录
            url = f"{self.comfyui_url}/history/{prompt_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            history = response.json()
            
            if prompt_id not in history:
                raise Exception("未找到执行历史")
            
            prompt_history = history[prompt_id]
            outputs = prompt_history.get("outputs", {})
            
            # 提取输出图片
            output_images = self._extract_output_images(outputs)
            
            # 分离输出图片和对比图片
            output_image = None
            comparison_image = None
            
            for img in output_images:
                if img.get("type") == "output":
                    output_image = img
                elif img.get("type") == "comparison":
                    comparison_image = img
            
            # 如果没有找到分类的图片，使用第一个作为输出图片
            if not output_image and output_images:
                output_image = output_images[0]
            
            return {
                "output_image": output_image,
                "comparison_image": comparison_image,
                "images": output_images,
                "outputs": outputs
            }
            
        except Exception as e:
            raise Exception(f"获取输出失败: {e}")
    
    def _extract_output_images(self, outputs: Dict) -> list:
        """
        从输出中提取图片信息
        
        根据节点命名规则提取：
        - output:image:1 -> 输出图片
        - output:image_comparer:2 -> 对比图片
        
        Args:
            outputs: 输出数据（节点 ID 为键）
            
        Returns:
            list: 图片信息列表，包含 output_image 和 comparison_image
        """
        images = []
        
        # 需要查询工作流定义来找到输出节点
        try:
            workflow = self._load_workflow()
            nodes = workflow.get("nodes", [])
            
            # 查找输出节点
            output_image_node_id = None
            comparer_image_node_id = None
            
            for node in nodes:
                title = node.get("title", "")
                node_id = node.get("id")
                if title == "output:image:1":
                    output_image_node_id = str(node_id)
                elif title == "output:image_comparer:2":
                    comparer_image_node_id = str(node_id)
            
            # 提取输出图片
            if output_image_node_id and output_image_node_id in outputs:
                node_output = outputs[output_image_node_id]
                if "images" in node_output:
                    for image_info in node_output["images"]:
                        filename = image_info.get("filename")
                        subfolder = image_info.get("subfolder", "")
                        image_type = image_info.get("type", "output")
                        
                        if filename:
                            image_url = f"{self.comfyui_url}/view"
                            params = {
                                "filename": filename,
                                "type": image_type
                            }
                            if subfolder:
                                params["subfolder"] = subfolder
                            
                            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                            full_url = f"{image_url}?{param_str}"
                            
                            images.append({
                                "type": "output",
                                "filename": filename,
                                "url": full_url,
                                "subfolder": subfolder,
                                "image_type": image_type
                            })
            
            # 提取对比图片
            if comparer_image_node_id and comparer_image_node_id in outputs:
                node_output = outputs[comparer_image_node_id]
                if "images" in node_output:
                    for image_info in node_output["images"]:
                        filename = image_info.get("filename")
                        subfolder = image_info.get("subfolder", "")
                        image_type = image_info.get("type", "temp")  # comparer 通常使用 temp 类型
                        
                        if filename:
                            image_url = f"{self.comfyui_url}/view"
                            params = {
                                "filename": filename,
                                "type": image_type
                            }
                            if subfolder:
                                params["subfolder"] = subfolder
                            
                            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                            full_url = f"{image_url}?{param_str}"
                            
                            images.append({
                                "type": "comparison",
                                "filename": filename,
                                "url": full_url,
                                "subfolder": subfolder,
                                "image_type": image_type
                            })
        except Exception as e:
            self._log(f"查找命名输出节点失败，使用默认逻辑: {e}", "WARNING")
        
        # 如果没有找到命名节点，使用原来的逻辑（向后兼容）
        if not images:
            for node_id, node_output in outputs.items():
                if "images" in node_output:
                    for image_info in node_output["images"]:
                        filename = image_info.get("filename")
                        subfolder = image_info.get("subfolder", "")
                        image_type = image_info.get("type", "output")
                        
                        if filename:
                            image_url = f"{self.comfyui_url}/view"
                            params = {
                                "filename": filename,
                                "type": image_type
                            }
                            if subfolder:
                                params["subfolder"] = subfolder
                            
                            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                            full_url = f"{image_url}?{param_str}"
                            
                            images.append({
                                "type": "output",
                                "filename": filename,
                                "url": full_url,
                                "subfolder": subfolder,
                                "image_type": image_type
                            })
        
        return images
    
    def download_image(self, image_info: Dict, save_path: str) -> str:
        """
        下载 ComfyUI 生成的图片
        
        Args:
            image_info: 图片信息
            save_path: 保存路径
            
        Returns:
            str: 保存路径
        """
        try:
            url = image_info.get("url")
            if not url:
                raise ValueError("图片信息中没有 URL")
            
            # 下载图片
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存图片
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            self._log(f"图片已下载: {save_path}")
            
            return save_path
            
        except Exception as e:
            raise Exception(f"下载图片失败: {e}")
    
    def _upload_image_to_comfyui(self, image_path: str) -> Optional[str]:
        """
        上传图片到 ComfyUI
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            Optional[str]: 上传后的文件名，失败返回 None
        """
        import os
        from pathlib import Path
        
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                self._log(f"图片文件不存在: {image_path}", "ERROR")
                return None
            
            # 读取图片文件
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 获取文件名
            filename = os.path.basename(image_path)
            
            # 上传到 ComfyUI
            url = f"{self.comfyui_url}/upload/image"
            files = {
                "image": (filename, image_data, "image/jpeg")
            }
            
            response = requests.post(url, files=files, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            uploaded_filename = result.get("name") or filename
            
            self._log(f"图片已上传到 ComfyUI: {uploaded_filename}")
            return uploaded_filename
            
        except Exception as e:
            self._log(f"上传图片到 ComfyUI 失败: {e}", "ERROR")
            return None
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: ComfyUI 是否可用
        """
        try:
            # 检查配置
            if not self.comfyui_url:
                return False
            
            # 尝试访问 ComfyUI
            url = f"{self.comfyui_url}/system_stats"
            response = requests.get(url, timeout=5)
            
            return response.status_code == 200
            
        except Exception:
            return False
