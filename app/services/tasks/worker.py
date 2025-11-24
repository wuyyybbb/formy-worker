"""
任务 Worker 工作进程
负责从队列中获取任务并分发到对应的 Pipeline 处理
"""
import time
import signal
import sys
from typing import Optional
from pathlib import Path

from app.services.tasks.queue import get_task_queue
from app.services.tasks.manager import get_task_service
from app.schemas.task import EditMode
from app.services.image.image_assets import (
    resolve_uploaded_file,
    copy_image_to_results,
    create_comparison_image,
)


class TaskWorker:
    """任务 Worker 类"""
    
    def __init__(self):
        """初始化 Worker"""
        self.queue = get_task_queue()
        self.task_service = get_task_service()
        self.is_running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """设置信号处理器（优雅关闭）"""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """处理关闭信号"""
        print("\n[Worker] 接收到关闭信号，正在停止...")
        self.is_running = False
    
    def start(self):
        """启动 Worker 循环"""
        print("[Worker] 任务 Worker 已启动，等待任务...")
        self.is_running = True
        
        while self.is_running:
            try:
                # 从队列中获取任务（阻塞式，超时 5 秒）
                task_id = self.queue.pop_task(timeout=5)
                
                if task_id:
                    print(f"[Worker] 获取到任务: {task_id}")
                    self._process_task(task_id)
                else:
                    # 超时未获取到任务，继续循环
                    continue
                    
            except Exception as e:
                print(f"[Worker] Worker 循环出错: {e}")
                time.sleep(1)  # 出错后等待 1 秒再继续
        
        print("[Worker] 任务 Worker 已停止")
    
    def _process_task(self, task_id: str):
        """
        处理单个任务
        
        Args:
            task_id: 任务ID
        """
        try:
            # 1. 获取任务数据
            task_data = self.queue.get_task_data(task_id)
            
            if not task_data:
                print(f"[Worker] 任务数据不存在: {task_id}")
                return
            
            # 2. 解析任务信息
            input_data = task_data.get("data", {})
            mode = input_data.get("mode")
            source_image = input_data.get("source_image")
            config = input_data.get("config", {})
            
            print(f"[Worker] 开始处理任务 {task_id} - 模式: {mode}")
            
            # 3. 更新状态为处理中
            self.task_service.update_task_progress(
                task_id=task_id,
                progress=0,
                current_step="任务已开始处理"
            )
            
            # 4. 根据模式分发到对应的 Pipeline
            result = self._dispatch_to_pipeline(
                task_id=task_id,
                mode=mode,
                source_image=source_image,
                config=config
            )
            
            # 5. 标记任务完成
            if result:
                self.task_service.complete_task(task_id, result)
                print(f"[Worker] 任务完成: {task_id}")
            else:
                self.task_service.fail_task(
                    task_id=task_id,
                    error_code="PROCESSING_FAILED",
                    error_message="任务处理失败"
                )
                print(f"[Worker] 任务失败: {task_id}")
                
        except Exception as e:
            print(f"[Worker] 处理任务异常: {task_id}, 错误: {e}")
            
            # 标记任务失败
            self.task_service.fail_task(
                task_id=task_id,
                error_code="INTERNAL_ERROR",
                error_message="任务处理过程中发生异常",
                error_details=str(e)
            )
    
    def _dispatch_to_pipeline(
        self,
        task_id: str,
        mode: str,
        source_image: str,
        config: dict
    ) -> Optional[dict]:
        """
        分发任务到对应的 Pipeline
        
        Args:
            task_id: 任务ID
            mode: 编辑模式
            source_image: 原始图片
            config: 配置参数
            
        Returns:
            Optional[dict]: 处理结果（包含 output_image, thumbnail, metadata）
        """
        try:
            # TODO: 这里将调用实际的 Pipeline
            # 当前仅为骨架，返回模拟结果
            
            print(f"[Worker] 分发任务到 Pipeline - 模式: {mode}")
            
            # 模拟不同模式的处理
            if mode == EditMode.HEAD_SWAP.value:
                return self._process_head_swap(task_id, source_image, config)
            elif mode == EditMode.BACKGROUND_CHANGE.value:
                return self._process_background_change(task_id, source_image, config)
            elif mode == EditMode.POSE_CHANGE.value:
                return self._process_pose_change(task_id, source_image, config)
            else:
                print(f"[Worker] 不支持的编辑模式: {mode}")
                return None
                
        except Exception as e:
            print(f"[Worker] Pipeline 处理失败: {e}")
            return None
    
    def _process_head_swap(
        self, 
        task_id: str, 
        source_image: str, 
        config: dict
    ) -> Optional[dict]:
        """
        处理换头任务（骨架）
        
        Args:
            task_id: 任务ID
            source_image: 原始图片
            config: 配置参数
            
        Returns:
            Optional[dict]: 处理结果
        """
        # TODO: 调用 HeadSwapPipeline
        print(f"[Worker] 执行换头处理...")
        
        # 更新进度
        self.task_service.update_task_progress(task_id, 30, "正在检测人脸...")
        time.sleep(1)  # 模拟处理
        
        self.task_service.update_task_progress(task_id, 60, "正在进行头部替换...")
        time.sleep(1)
        
        self.task_service.update_task_progress(task_id, 90, "正在进行图像融合...")
        time.sleep(1)
        
        # 返回模拟结果
        return {
            "output_image": f"/results/{task_id}_output.jpg",
            "thumbnail": f"/results/{task_id}_thumb.jpg",
            "metadata": {
                "width": 1024,
                "height": 1536,
                "format": "jpeg"
            }
        }
    
    def _process_background_change(
        self, 
        task_id: str, 
        source_image: str, 
        config: dict
    ) -> Optional[dict]:
        """
        处理换背景任务（骨架）
        
        Args:
            task_id: 任务ID
            source_image: 原始图片
            config: 配置参数
            
        Returns:
            Optional[dict]: 处理结果
        """
        # TODO: 调用 BackgroundPipeline
        print(f"[Worker] 执行换背景处理...")
        
        self.task_service.update_task_progress(task_id, 25, "正在进行人像抠图...")
        time.sleep(1)
        
        self.task_service.update_task_progress(task_id, 50, "正在替换背景...")
        time.sleep(1)
        
        self.task_service.update_task_progress(task_id, 80, "正在进行边缘融合...")
        time.sleep(1)
        
        return {
            "output_image": f"/results/{task_id}_output.jpg",
            "thumbnail": f"/results/{task_id}_thumb.jpg",
            "metadata": {
                "width": 1024,
                "height": 1536,
                "format": "jpeg"
            }
        }
    
    def _process_pose_change(
        self, 
        task_id: str, 
        source_image: str, 
        config: dict
    ) -> Optional[dict]:
        """
        处理换姿势任务（骨架）
        
        Args:
            task_id: 任务ID
            source_image: 原始图片
            config: 配置参数
            
        Returns:
            Optional[dict]: 处理结果
        """
        print(f"[Worker] 执行换姿势处理...")

        pose_reference_id = config.get("pose_image") or config.get("pose_reference")

        source_path = resolve_uploaded_file(source_image)
        reference_path: Optional[Path] = None
        if pose_reference_id:
            reference_path = resolve_uploaded_file(pose_reference_id)

        self.task_service.update_task_progress(task_id, 20, "正在整理输入图片...")

        target_path = reference_path or source_path
        output_file = copy_image_to_results(
            target_path, f"{task_id}_output{target_path.suffix.lower() or '.jpg'}"
        )

        self.task_service.update_task_progress(task_id, 55, "正在生成合成图像...")

        comparison_file: Optional[Path] = None
        try:
            comparison_file = create_comparison_image(
                before_path=source_path,
                after_path=target_path,
                filename=f"{task_id}_comparison.jpg",
            )
        except Exception as cmp_err:
            print(f"[Worker] 生成对比图失败: {cmp_err}")

        self.task_service.update_task_progress(task_id, 90, "正在保存结果...")

        result_payload = {
            "output_image": f"/results/{output_file.name}",
            "thumbnail": f"/results/{output_file.name}",
            "metadata": {
                "width": 0,
                "height": 0,
                "format": target_path.suffix.replace(".", "") or "jpeg",
            }
        }

        if comparison_file:
            result_payload["comparison_image"] = f"/results/{comparison_file.name}"
            result_payload["metadata"]["comparison_image"] = result_payload["comparison_image"]

        return result_payload


def run_worker():
    """运行 Worker（入口函数）"""
    print("="*50)
    print("Formy Task Worker")
    print("="*50)
    
    # 检查 Redis 连接
    queue = get_task_queue()
    if not queue.health_check():
        print("[错误] 无法连接到 Redis，请检查配置")
        sys.exit(1)
    
    print("[成功] Redis 连接正常")
    
    # 启动 Worker
    worker = TaskWorker()
    worker.start()


if __name__ == "__main__":
    run_worker()

