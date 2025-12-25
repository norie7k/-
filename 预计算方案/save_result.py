"""
保存分析结果脚本
运行 top5_Q2.ipynb 的逻辑并将结果保存为 JSON 文件
"""
import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# 添加源代码路径
SOURCE_DIR = Path(__file__).parent.parent / "玩家发言整理（供运营侧）" / "玩家发言总结_版本总结V2-Copy1.0(单日）"
if SOURCE_DIR.exists():
    sys.path.insert(0, str(SOURCE_DIR))
    print(f"✅ 已加载源代码路径: {SOURCE_DIR}")
else:
    print(f"❌ 源代码路径不存在: {SOURCE_DIR}")
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

# ==================== 配置 ====================
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
API_KEY = "de91deb0-aae6-46cb-bac0-17ac3b6107f5"
V3_MODEL_ID = "ep-20251020160142-5d7hp"
V3_1_MODEL_ID = "ep-20251020160025-9p5tj"

BATCH_SIZE = 300
TEMPERATURE = 0.20
MAX_TOKENS = 16384
TIMEOUT_SEC = 600
RETRIES = 2

SPEAKER_MAP = {
    "16186514": "peter本尊",
    "1655611808": "运营绾绾",
    "2073820674": "沙利文老师",
    "2726067525": "milissa",
}

# 结果保存目录
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def run_analysis(txt_path: str, mapping_path: str, 
                 start_time: str, end_time: str) -> dict:
    """
    运行分析（与 top5_Q2.ipynb 逻辑一致）
    """
    print(f"\n{'='*60}")
    print(f"📊 开始分析: {start_time} ~ {end_time}")
    print(f"{'='*60}")
    
    # 加载提示词
    prompt_dir = SOURCE_DIR
    system_prompt01 = load_system_prompt(prompt_dir / "提示词1.md")
    system_prompt02 = load_system_prompt(prompt_dir / "2话题分类.md")
    system_prompt03 = load_system_prompt(prompt_dir / "3日聚合.md")
    system_prompt04 = load_system_prompt(prompt_dir / "2话题分类和总结.md")
    
    # Step 1: 数据预处理
    print("\n[1/6] 加载聊天记录...")
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
            "date": start_time.split(" ")[0],
            "time_range": f"{start_time} ~ {end_time}",
            "total_messages": 0,
            "filtered_messages": 0,
            "top5_clusters": []
        }
    
    # Step 2: 模型#1 + 模型#2 批处理
    print("\n[2/6] 话题簇分析...")
    batch_cluster_outputs = []
    total_batches = (total_messages + BATCH_SIZE - 1) // BATCH_SIZE
    written_total = 0
    
    for b in range(total_batches):
        start_idx = b * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_messages)
        batch_lines = jsonl_lines01[start_idx:end_idx]
        
        print(f"  批次 {b+1}/{total_batches}...", end=" ")
        
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
                print("❌ 模型#1 无输出")
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
                print("❌ 模型#2 无输出")
                continue
            
            # 解析并添加 ID
            cluster_json_list = parse_model2_output_to_json_list(output_cluster, batch_idx=b+1)
            if not cluster_json_list:
                print("⚠️ 无有效簇")
                continue
            
            date_str = infer_date_for_batch(cluster_json_list, batch_lines)
            batch_id = f"B{b+1}"
            cluster_json_list = assign_global_cluster_ids(cluster_json_list, date_str, batch_id)
            
            output_cluster_with_ids = "\n".join(
                json.dumps(c, ensure_ascii=False) for c in cluster_json_list
            )
            batch_cluster_outputs.append(output_cluster_with_ids)
            print(f"✅ 筛选 {filter_count} 条")
            
        except Exception as e:
            print(f"❌ 出错: {e}")
            continue
        
        time.sleep(1)
    
    # Step 3: 模型#3 聚合
    print("\n[3/6] 聚合话题簇...")
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
    print("\n[4/6] 计算热度排名...")
    top5_results = extract_top5_heat_clusters(parsed_clusters, jsonl_lines01, top_k=5)
    final_result = attach_discussion_points(top5_results, parsed_subclusters)
    
    # Step 5: 模型#4 观点分析
    print("\n[5/6] 分析玩家观点...")
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
            print(f"  ✅ 观点 {idx}: {mech[:30]}...")
        except Exception as e:
            print(f"  ❌ 观点 {idx} 出错: {e}")
            continue
    
    # Step 6: 合并结果
    print("\n[6/6] 生成最终报告...")
    merged_top5 = merge_top5_with_opinions_numbered(final_result, all_opinions)
    
    return {
        "status": "success",
        "date": start_time.split(" ")[0],
        "time_range": f"{start_time} ~ {end_time}",
        "total_messages": total_messages,
        "filtered_messages": written_total,
        "top5_clusters": merged_top5,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_result(result: dict, output_path: Path = None):
    """保存结果到 JSON 文件"""
    if output_path is None:
        date_str = result.get("date", datetime.now().strftime("%Y-%m-%d"))
        output_path = RESULTS_DIR / f"{date_str}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存到: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="运行分析并保存结果")
    parser.add_argument("--txt", required=True, help="聊天记录 txt 文件路径")
    parser.add_argument("--mapping", required=True, help="客服映射 xlsx 文件路径")
    parser.add_argument("--start", required=True, help="开始时间 (格式: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--end", required=True, help="结束时间 (格式: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--output", help="输出文件路径 (可选)")
    
    args = parser.parse_args()
    
    # 运行分析
    result = run_analysis(
        txt_path=args.txt,
        mapping_path=args.mapping,
        start_time=args.start,
        end_time=args.end
    )
    
    # 保存结果
    output_path = Path(args.output) if args.output else None
    save_result(result, output_path)
    
    print("\n" + "="*60)
    print("🎉 分析完成！")
    print("="*60)
    print("\n下一步：")
    print("1. git add results/")
    print('2. git commit -m "添加分析结果"')
    print("3. git push")


if __name__ == "__main__":
    main()


