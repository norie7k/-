"""
本地任务监听脚本
后台运行，自动检测并处理分析任务
"""
import sys
import time
import os
import traceback
from datetime import datetime
from pathlib import Path

# 添加源代码路径
try:
    from config import SOURCE_CODE_DIR, PROMPTS_DIR, TEMP_DIR, POLL_INTERVAL
    from config import API_URL, API_KEY, V3_MODEL_ID, V3_1_MODEL_ID
    from config import BATCH_SIZE, TEMPERATURE, MAX_TOKENS, TIMEOUT_SEC, RETRIES
    from config import SPEAKER_MAP
except ImportError:
    print("❌ 请先复制 config.example.py 为 config.py 并填入配置信息")
    sys.exit(1)

# 添加源代码到路径
if os.path.exists(SOURCE_CODE_DIR):
    sys.path.insert(0, SOURCE_CODE_DIR)
    print(f"✅ 已加载源代码路径: {SOURCE_CODE_DIR}")
else:
    print(f"❌ 源代码路径不存在: {SOURCE_CODE_DIR}")
    sys.exit(1)

# 导入分析模块
from data_processing import build_jsonl_for_range
from model_classifyV1_Copy1_Copy1 import (
    load_system_prompt,
    build_user_prompt_filter,
    build_user_prompt_clsuter,
    build_user_prompt_cluster_agg,
    build_user_prompt_subcluster_opinion,
    call_ark_chat_completions,
    parse_model2_output_to_json_list,
    infer_date_for_batch,
    assign_global_cluster_ids,
    aggregate_cluster_outputs,
    parse_jsonl_text_safe,
    parse_jsonl_text,
    ensure_time_axis_key,
    ensure_subcluster_list_key,
    extract_top5_heat_clusters,
    attach_discussion_points,
    print_mech_time_from_top5,
    get_dialogs_lines_by_fayan_time_debug,
    merge_top5_with_opinions_numbered,
    parse_opinion_output_to_list,
)

from supabase_client import get_client
import json


def run_analysis(txt_path: str, mapping_path: str, 
                 start_time: str, end_time: str) -> dict:
    """
    运行分析（与 top5_Q2.ipynb 逻辑一致）
    """
    print(f"📊 开始分析: {start_time} ~ {end_time}")
    
    # 加载提示词
    prompt_dir = Path(PROMPTS_DIR)
    system_prompt01 = load_system_prompt(prompt_dir / "提示词1.md")
    system_prompt02 = load_system_prompt(prompt_dir / "2话题分类.md")
    system_prompt03 = load_system_prompt(prompt_dir / "3日聚合.md")
    system_prompt04 = load_system_prompt(prompt_dir / "2话题分类和总结.md")
    
    # Step 1: 数据预处理
    print("  [1/6] 加载聊天记录...")
    jsonl_lines01 = build_jsonl_for_range(
        pathtxt=txt_path,
        mapping_file=mapping_path,
        speaker_map=SPEAKER_MAP,
        start_time=start_time,
        end_time=end_time,
        return_str=False,
    )
    
    total_messages = len(jsonl_lines01)
    print(f"  → 共 {total_messages} 条消息")
    
    if total_messages == 0:
        return {
            "status": "no_data",
            "error": "指定时间范围内没有聊天记录",
            "total_messages": 0,
            "filtered_messages": 0,
            "top5_clusters": []
        }
    
    # Step 2: 模型#1 + 模型#2 批处理
    print("  [2/6] 话题簇分析...")
    batch_cluster_outputs = []
    total_batches = (total_messages + BATCH_SIZE - 1) // BATCH_SIZE
    written_total = 0
    
    for b in range(total_batches):
        start_idx = b * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_messages)
        batch_lines = jsonl_lines01[start_idx:end_idx]
        
        print(f"    批次 {b+1}/{total_batches}...")
        
        try:
            # 模型 #1：筛选
            user_prompt1 = build_user_prompt_filter(batch_lines)
            output_filter = call_ark_chat_completions(
                api_url=API_URL,
                api_key=API_KEY,
                model=V3_MODEL_ID,
                system_prompt=system_prompt01,
                user_prompt=user_prompt1,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                timeout=TIMEOUT_SEC,
                retries=RETRIES,
            )
            
            if not output_filter:
                continue
            
            filter_count = sum(1 for line in output_filter.splitlines() if line.strip())
            written_total += filter_count
            
            # 模型 #2：话题簇
            user_prompt2 = build_user_prompt_clsuter(output_filter)
            output_cluster = call_ark_chat_completions(
                api_url=API_URL,
                api_key=API_KEY,
                model=V3_1_MODEL_ID,
                system_prompt=system_prompt02,
                user_prompt=user_prompt2,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                timeout=TIMEOUT_SEC,
                retries=RETRIES,
            )
            
            if not output_cluster:
                continue
            
            # 解析并添加 ID
            cluster_json_list = parse_model2_output_to_json_list(output_cluster, batch_idx=b+1)
            if not cluster_json_list:
                continue
            
            date_str = infer_date_for_batch(cluster_json_list, batch_lines)
            batch_id = f"B{b+1}"
            cluster_json_list = assign_global_cluster_ids(cluster_json_list, date_str, batch_id)
            
            output_cluster_with_ids = "\n".join(
                json.dumps(c, ensure_ascii=False) for c in cluster_json_list
            )
            batch_cluster_outputs.append(output_cluster_with_ids)
            
        except Exception as e:
            print(f"    ❌ 批次 {b+1} 出错: {e}")
            continue
        
        time.sleep(1)  # 防止 QPS 限制
    
    # Step 3: 模型#3 聚合
    print("  [3/6] 聚合话题簇...")
    all_cluster = aggregate_cluster_outputs(batch_cluster_outputs)
    
    user_prompt3 = build_user_prompt_cluster_agg(all_cluster)
    output_cluster_agg = call_ark_chat_completions(
        api_url=API_URL,
        api_key=API_KEY,
        model=V3_1_MODEL_ID,
        system_prompt=system_prompt03,
        user_prompt=user_prompt3,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT_SEC,
        retries=RETRIES,
    )
    
    parsed_clusters = parse_jsonl_text_safe(output_cluster_agg, label="模型#3聚合输出")
    parsed_subclusters = parse_jsonl_text(all_cluster)
    
    for c in parsed_clusters:
        ensure_time_axis_key(c, verbose=False)
        ensure_subcluster_list_key(c)
    
    # Step 4: 计算热度 Top5
    print("  [4/6] 计算热度排名...")
    top5_results = extract_top5_heat_clusters(parsed_clusters, jsonl_lines01, top_k=5)
    final_result = attach_discussion_points(top5_results, parsed_subclusters)
    
    # Step 5: 模型#4 观点分析
    print("  [5/6] 分析玩家观点...")
    rows = print_mech_time_from_top5(final_result, all_cluster)
    
    all_opinions = []
    for idx, r in enumerate(rows, start=1):
        mech = r.get("核心对象/机制") or ""
        full_time = (r.get("发言时间") or "").strip()
        
        if not mech or not full_time or " " not in full_time:
            continue
        
        fayan_date, fayan_time = full_time.split(" ", 1)
        
        dialogs_lines = get_dialogs_lines_by_fayan_time_debug(
            jsonl_lines01, fayan_date, fayan_time, debug=False
        )
        
        if not dialogs_lines:
            continue
        
        user_prompt4 = build_user_prompt_subcluster_opinion(
            discussion_point=mech,
            json_lines=dialogs_lines,
        )
        
        try:
            opinion_output = call_ark_chat_completions(
                api_url=API_URL,
                api_key=API_KEY,
                model=V3_1_MODEL_ID,
                system_prompt=system_prompt04,
                user_prompt=user_prompt4,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                timeout=TIMEOUT_SEC,
                retries=RETRIES,
            )
            
            opinions_this_mech = parse_opinion_output_to_list(opinion_output)
            all_opinions.extend(opinions_this_mech)
        except Exception as e:
            print(f"    ❌ 观点分析出错: {e}")
            continue
    
    # Step 6: 合并结果
    print("  [6/6] 生成最终报告...")
    merged_top5 = merge_top5_with_opinions_numbered(final_result, all_opinions)
    
    return {
        "status": "success",
        "date": start_time.split(" ")[0],
        "time_range": f"{start_time} ~ {end_time}",
        "total_messages": total_messages,
        "filtered_messages": written_total,
        "top5_clusters": merged_top5
    }


def process_task(task: dict):
    """处理单个任务"""
    task_id = task["id"]
    client = get_client()
    
    print(f"\n{'='*50}")
    print(f"📋 处理任务: {task_id}")
    print(f"   时间范围: {task['start_time']} ~ {task['end_time']}")
    print(f"{'='*50}")
    
    # 更新状态为处理中
    client.set_task_processing(task_id)
    
    start_time_proc = time.time()
    
    try:
        # 下载文件
        temp_dir = os.path.join(TEMP_DIR, task_id)
        txt_path, mapping_path = client.download_task_files(task, temp_dir)
        
        if not txt_path:
            raise Exception("txt 文件下载失败")
        if not mapping_path:
            raise Exception("mapping 文件下载失败")
        
        # 运行分析
        result = run_analysis(
            txt_path=txt_path,
            mapping_path=mapping_path,
            start_time=task["start_time"],
            end_time=task["end_time"]
        )
        
        processing_time = time.time() - start_time_proc
        
        # 更新任务状态
        if result["status"] == "success":
            client.set_task_completed(
                task_id,
                result=result,
                total_messages=result.get("total_messages", 0),
                filtered_messages=result.get("filtered_messages", 0),
                processing_time=processing_time
            )
            print(f"✅ 任务完成！耗时 {processing_time:.1f} 秒")
        else:
            client.set_task_failed(task_id, result.get("error", "未知错误"))
            print(f"⚠️ 任务完成但无数据: {result.get('error')}")
        
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        client.set_task_failed(task_id, error_msg)
        print(f"❌ 任务失败: {e}")


def main():
    """主循环"""
    print("="*60)
    print("🚀 自动化分析任务监听器")
    print("="*60)
    print(f"轮询间隔: {POLL_INTERVAL} 秒")
    print(f"源代码目录: {SOURCE_CODE_DIR}")
    print("按 Ctrl+C 停止")
    print("="*60)
    
    client = get_client()
    
    while True:
        try:
            # 获取待处理任务
            tasks = client.get_pending_tasks()
            
            if tasks:
                print(f"\n📬 发现 {len(tasks)} 个待处理任务")
                for task in tasks:
                    process_task(task)
            else:
                print(".", end="", flush=True)
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 已停止监听")
            break
        except Exception as e:
            print(f"\n❌ 监听出错: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()


