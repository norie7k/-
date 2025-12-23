"""
玩家社群发言分析引擎 - 桥接模块
直接引用源代码目录中的模块，确保 H5包装 始终使用最新的源代码

基于: 玩家发言总结_版本总结V2-Copy1.0(单日）/top5_Q2.ipynb
"""
from __future__ import annotations
import sys
from pathlib import Path

# ==================== 配置源代码路径 ====================
# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 源代码目录路径
SOURCE_DIR = PROJECT_ROOT / "玩家发言整理（供运营侧）" / "玩家发言总结_版本总结V2-Copy1.0(单日）"

# 将源代码目录添加到 Python 路径（必须在导入前执行）
if SOURCE_DIR.exists():
    if str(SOURCE_DIR) not in sys.path:
        sys.path.insert(0, str(SOURCE_DIR))
    print(f"✅ 已加载源代码路径: {SOURCE_DIR}")
    _SOURCE_LOADED = True
else:
    print(f"⚠️ 源代码路径不存在: {SOURCE_DIR}")
    _SOURCE_LOADED = False

# ==================== 从源代码导入模块（通配符导入，自动包含所有新增函数） ====================
if _SOURCE_LOADED:
    try:
        # 从 data_processing.py 导入所有
        from data_processing import *
        
        # 从 model_classifyV1_Copy1_Copy1.py 导入所有
        from model_classifyV1_Copy1_Copy1 import *
        
        print("✅ 成功从源代码目录导入所有模块（通配符导入）")
        
    except ImportError as e:
        print(f"⚠️ 导入源代码模块失败: {e}")
        _SOURCE_LOADED = False


# ==================== H5包装专用分析器类 ====================
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union


class PlayerCommunityAnalyzer:
    """
    玩家社群分析器 - 封装完整的分析流程
    专为 H5 Streamlit 应用设计
    
    完全基于 top5_Q2.ipynb 的流程实现
    """
    
    def __init__(
        self,
        api_url: str,
        api_key: str,
        v3_model_id: str,
        v3_1_model_id: str,
        prompt_dir: Union[str, Path],
    ):
        """
        初始化分析器
        
        Args:
            api_url: API 地址
            api_key: API 密钥  
            v3_model_id: V3 模型 ID（用于筛选游戏相关发言）
            v3_1_model_id: V3.1 模型 ID（用于话题簇分析和观点提取）
            prompt_dir: 提示词目录
        """
        if not _SOURCE_LOADED:
            raise RuntimeError("源代码模块未正确加载，请检查路径配置")
        
        self.api_url = api_url
        self.api_key = api_key
        self.v3_model_id = v3_model_id
        self.v3_1_model_id = v3_1_model_id
        self.prompt_dir = Path(prompt_dir)
        
        # 分析参数（与 top5_Q2.ipynb 一致）
        self.temperature = 0.20
        self.max_tokens = 16384
        self.timeout = 600
        self.retries = 2
        self.sleep_between = 1
        
        # 加载提示词（与 top5_Q2.ipynb 一致）
        self.system_prompt01 = load_system_prompt(self.prompt_dir / "提示词1.md")
        self.system_prompt02 = load_system_prompt(self.prompt_dir / "2话题分类.md")
        self.system_prompt03 = load_system_prompt(self.prompt_dir / "3日聚合.md")
        self.system_prompt04 = load_system_prompt(self.prompt_dir / "2话题分类和总结.md")
    
    def analyze(
        self,
        txt_path: str,
        mapping_file: str,
        speaker_map: Dict[str, str],
        start_time: str,
        end_time: str,
        batch_size: int = 300,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        执行完整的分析流程（与 top5_Q2.ipynb 主循环对应）
        
        Args:
            txt_path: QQ群聊天记录 txt 文件路径
            mapping_file: 客服昵称映射 Excel 文件路径
            speaker_map: 研发人员 ID 映射字典
            start_time: 开始时间，格式：YYYY-MM-DD HH:MM:SS
            end_time: 结束时间，格式：YYYY-MM-DD HH:MM:SS
            batch_size: 每批处理的消息数量（默认300，与 top5_Q2.ipynb 一致）
            progress_callback: 进度回调函数，接收 (current, total, message) 参数
        
        Returns:
            分析结果字典
        """
        results = {
            "status": "processing",
            "date": start_time.split(" ")[0] if " " in start_time else start_time[:10],
            "time_range": f"{start_time} ~ {end_time}",
            "total_messages": 0,
            "filtered_messages": 0,
            "top5_clusters": [],
            "error": None,
        }
        
        def update_progress(step: int, total: int, message: str):
            if progress_callback:
                progress_callback(step, total, message)
        
        try:
            # ==================== Step 1: 数据预处理 ====================
            # 对应 top5_Q2.ipynb 的数据处理部分
            update_progress(1, 6, "正在加载聊天记录...")
            
            jsonl_lines01 = build_jsonl_for_range(
                pathtxt=txt_path,
                mapping_file=mapping_file,
                speaker_map=speaker_map,
                start_time=start_time,
                end_time=end_time,
                return_str=False,
            )
            
            results["total_messages"] = len(jsonl_lines01)
            
            if len(jsonl_lines01) == 0:
                results["status"] = "no_data"
                results["error"] = "指定时间范围内没有聊天记录"
                return results
            
            # ==================== Step 2: 模型#1 + 模型#2 批处理 ====================
            # 对应 top5_Q2.ipynb 的 "加讨论观点分析的版本测试" 部分
            update_progress(2, 6, "正在进行话题簇分析...")
            
            batch_cluster_outputs = []
            total_batches = (len(jsonl_lines01) + batch_size - 1) // batch_size
            written_total = 0
            
            for b in range(total_batches):
                start_idx = b * batch_size
                end_idx = min(start_idx + batch_size, len(jsonl_lines01))
                batch_lines = jsonl_lines01[start_idx:end_idx]
                
                try:
                    # --- 模型 #1：筛选游戏相关发言 ---
                    user_prompt1 = build_user_prompt_filter(batch_lines)
                    output_filter = call_ark_chat_completions(
                        api_url=self.api_url,
                        api_key=self.api_key,
                        model=self.v3_model_id,
                        system_prompt=self.system_prompt01,
                        user_prompt=user_prompt1,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=self.timeout,
                        retries=self.retries,
                    )
                    
                    if not output_filter:
                        continue
                    
                    filter_count = sum(1 for line in output_filter.splitlines() if line.strip())
                    written_total += filter_count
                    
                    # --- 模型 #2：话题簇划分 ---
                    user_prompt2 = build_user_prompt_clsuter(output_filter)
                    output_cluster = call_ark_chat_completions(
                        api_url=self.api_url,
                        api_key=self.api_key,
                        model=self.v3_1_model_id,
                        system_prompt=self.system_prompt02,
                        user_prompt=user_prompt2,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=self.timeout,
                        retries=self.retries,
                    )
                    
                    if not output_cluster:
                        continue
                    
                    # 解析并添加 _cluster_id
                    cluster_json_list = parse_model2_output_to_json_list(
                        output_cluster,
                        batch_idx=b + 1,
                    )
                    
                    if not cluster_json_list:
                        continue
                    
                    # 推断日期并分配全局ID
                    date_str = infer_date_for_batch(cluster_json_list, batch_lines)
                    batch_id = f"B{b + 1}"
                    cluster_json_list = assign_global_cluster_ids(
                        cluster_json_list, date_str, batch_id
                    )
                    
                    # 转成 JSONL 文本
                    output_cluster_with_ids = "\n".join(
                        json.dumps(c, ensure_ascii=False) for c in cluster_json_list
                    )
                    batch_cluster_outputs.append(output_cluster_with_ids)
                    
                except Exception as e:
                    print(f"[批次 {b + 1}] 出错: {e}")
                    continue
                
                time.sleep(self.sleep_between)
            
            results["filtered_messages"] = written_total
            
            # ==================== Step 3: 模型#3 日话题簇聚合 ====================
            update_progress(3, 6, "正在聚合话题簇...")
            
            all_cluster = aggregate_cluster_outputs(batch_cluster_outputs)
            
            user_prompt3 = build_user_prompt_cluster_agg(all_cluster)
            output_cluster_agg = call_ark_chat_completions(
                api_url=self.api_url,
                api_key=self.api_key,
                model=self.v3_1_model_id,
                system_prompt=self.system_prompt03,
                user_prompt=user_prompt3,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                retries=self.retries,
            )
            
            # 解析聚合结果
            parsed_clusters = parse_jsonl_text_safe(output_cluster_agg, label="模型#3聚合输出")
            parsed_subclusters = parse_jsonl_text(all_cluster)
            
            # 修复时间轴和子话题簇列表字段
            for c in parsed_clusters:
                ensure_time_axis_key(c, verbose=False)
                ensure_subcluster_list_key(c)
            
            # ==================== Step 4: 计算热度 Top5 ====================
            update_progress(4, 6, "正在计算热度排名...")
            
            top5_results = extract_top5_heat_clusters(
                parsed_clusters, jsonl_lines01, top_k=5
            )
            final_result = attach_discussion_points(top5_results, parsed_subclusters)
            
            # ==================== Step 5: 模型#4 玩家观点分析 ====================
            update_progress(5, 6, "正在分析玩家观点...")
            
            # 获取讨论点和时间轴的映射
            rows = print_mech_time_from_top5(final_result, all_cluster)
            
            all_opinions = []
            for idx, r in enumerate(rows, start=1):
                mech = r.get("核心对象/机制") or ""
                full_time = (r.get("发言时间") or "").strip()
                
                if not mech or not full_time:
                    continue
                
                if " " not in full_time:
                    continue
                
                fayan_date, fayan_time = full_time.split(" ", 1)
                
                # 获取该时间段的原始发言
                dialogs_lines = get_dialogs_lines_by_fayan_time_debug(
                    jsonl_lines01,
                    fayan_date,
                    fayan_time,
                    debug=False,
                )
                
                if not dialogs_lines:
                    continue
                
                # 调用模型#4 分析玩家观点
                user_prompt4 = build_user_prompt_subcluster_opinion(
                    discussion_point=mech,
                    json_lines=dialogs_lines,
                )
                
                try:
                    opinion_output = call_ark_chat_completions(
                        api_url=self.api_url,
                        api_key=self.api_key,
                        model=self.v3_1_model_id,
                        system_prompt=self.system_prompt04,
                        user_prompt=user_prompt4,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        timeout=self.timeout,
                        retries=self.retries,
                    )
                    
                    opinions_this_mech = parse_opinion_output_to_list(opinion_output)
                    all_opinions.extend(opinions_this_mech)
                    
                except Exception as e:
                    print(f"模型#4 调用出错: {e}")
                    continue
            
            # ==================== Step 6: 合并结果 ====================
            update_progress(6, 6, "正在生成最终报告...")
            
            # 合并观点到 Top5
            merged_top5 = merge_top5_with_opinions_numbered(final_result, all_opinions)
            
            results["top5_clusters"] = merged_top5
            results["status"] = "success"
            
        except Exception as e:
            import traceback
            results["status"] = "error"
            results["error"] = str(e)
            results["traceback"] = traceback.format_exc()
        
        return results


# ==================== 导出列表 ====================
__all__ = [
    # 源代码导入的函数（供直接使用）
    'load_and_process',
    'build_jsonl_for_range',
    'save_jsonl',
    'load_system_prompt',
    'build_user_prompt_filter',
    'build_user_prompt_clsuter',
    'build_user_prompt_cluster_agg',
    'build_user_prompt_subcluster_opinion',
    'call_ark_chat_completions',
    'extract_valid_json_lines',
    'add_index_to_jsonl_lines',
    'count_output_filter_stats',
    'get_covered_indices_from_cluster_output',
    'aggregate_cluster_outputs',
    'assign_global_cluster_ids',
    'infer_date_for_batch',
    'parse_model2_output_to_json_list',
    'parse_jsonl_text',
    'extract_top5_heat_clusters',
    'attach_discussion_points',
    'extract_cluster_stats',
    'print_mech_time_from_top5',
    'get_dialogs_lines_by_fayan_time_debug',
    'merge_top5_with_opinions_numbered',
    'parse_opinion_output_to_list',
    'ensure_time_axis_key',
    'ensure_subcluster_list_key',
    'match_dialogs_by_time',
    'append_daily_top5_to_version_jsonl',
    
    # H5包装专用
    'PlayerCommunityAnalyzer',
    
    # 常量
    'PROJECT_ROOT',
    'SOURCE_DIR',
    '_SOURCE_LOADED',
]
