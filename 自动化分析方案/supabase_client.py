"""
Supabase 客户端封装
处理与 Supabase 的所有交互
"""
from supabase import create_client, Client
from datetime import datetime
import json
import os

# 导入配置
try:
    from config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    raise ImportError("请先复制 config.example.py 为 config.py 并填入配置信息")


class SupabaseClient:
    """Supabase 客户端封装"""
    
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.tasks_table = "analysis_tasks"
        self.uploads_bucket = "uploads"
        self.results_bucket = "results"
    
    # ==================== 任务操作 ====================
    
    def get_pending_tasks(self):
        """获取所有待处理的任务"""
        response = self.client.table(self.tasks_table)\
            .select("*")\
            .eq("status", "pending")\
            .order("created_at")\
            .execute()
        return response.data
    
    def update_task_status(self, task_id: str, status: str, **kwargs):
        """更新任务状态"""
        data = {"status": status, **kwargs}
        response = self.client.table(self.tasks_table)\
            .update(data)\
            .eq("id", task_id)\
            .execute()
        return response.data
    
    def set_task_processing(self, task_id: str):
        """设置任务为处理中"""
        return self.update_task_status(task_id, "processing")
    
    def set_task_completed(self, task_id: str, result: dict, 
                           total_messages: int = 0,
                           filtered_messages: int = 0,
                           processing_time: float = 0):
        """设置任务为已完成"""
        return self.update_task_status(
            task_id, 
            "completed",
            result=result,
            total_messages=total_messages,
            filtered_messages=filtered_messages,
            processing_time_seconds=processing_time
        )
    
    def set_task_failed(self, task_id: str, error_message: str):
        """设置任务为失败"""
        return self.update_task_status(
            task_id, 
            "failed",
            error_message=error_message
        )
    
    def create_task(self, start_time: str, end_time: str,
                    txt_file_path: str = None,
                    mapping_file_path: str = None):
        """创建新任务"""
        data = {
            "start_time": start_time,
            "end_time": end_time,
            "txt_file_path": txt_file_path,
            "mapping_file_path": mapping_file_path,
            "status": "pending"
        }
        response = self.client.table(self.tasks_table)\
            .insert(data)\
            .execute()
        return response.data[0] if response.data else None
    
    def get_task_by_id(self, task_id: str):
        """根据 ID 获取任务"""
        response = self.client.table(self.tasks_table)\
            .select("*")\
            .eq("id", task_id)\
            .execute()
        return response.data[0] if response.data else None
    
    def get_completed_tasks(self, limit: int = 10):
        """获取已完成的任务列表"""
        response = self.client.table(self.tasks_table)\
            .select("*")\
            .eq("status", "completed")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    
    # ==================== 文件操作 ====================
    
    def upload_file(self, bucket: str, file_path: str, file_content: bytes):
        """上传文件到存储桶"""
        response = self.client.storage.from_(bucket).upload(
            file_path,
            file_content,
            {"content-type": "application/octet-stream"}
        )
        return response
    
    def download_file(self, bucket: str, file_path: str) -> bytes:
        """从存储桶下载文件"""
        response = self.client.storage.from_(bucket).download(file_path)
        return response
    
    def upload_txt_file(self, task_id: str, file_content: bytes) -> str:
        """上传聊天记录 txt 文件"""
        file_path = f"tasks/{task_id}/chat.txt"
        self.upload_file(self.uploads_bucket, file_path, file_content)
        return file_path
    
    def upload_mapping_file(self, task_id: str, file_content: bytes) -> str:
        """上传 mapping xlsx 文件"""
        file_path = f"tasks/{task_id}/mapping.xlsx"
        self.upload_file(self.uploads_bucket, file_path, file_content)
        return file_path
    
    def download_task_files(self, task: dict, temp_dir: str):
        """下载任务相关的文件到本地临时目录"""
        os.makedirs(temp_dir, exist_ok=True)
        
        txt_path = None
        mapping_path = None
        
        if task.get("txt_file_path"):
            content = self.download_file(self.uploads_bucket, task["txt_file_path"])
            txt_path = os.path.join(temp_dir, "chat.txt")
            with open(txt_path, "wb") as f:
                f.write(content)
        
        if task.get("mapping_file_path"):
            content = self.download_file(self.uploads_bucket, task["mapping_file_path"])
            mapping_path = os.path.join(temp_dir, "mapping.xlsx")
            with open(mapping_path, "wb") as f:
                f.write(content)
        
        return txt_path, mapping_path


# 单例模式
_client = None

def get_client() -> SupabaseClient:
    """获取 Supabase 客户端单例"""
    global _client
    if _client is None:
        _client = SupabaseClient()
    return _client


