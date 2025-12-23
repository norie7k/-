"""
玩家社群分析核心模块
此模块作为共享代码库，供 H5包装 和 Jupyter Notebook 共同引用
"""

from .data_processing import (
    load_and_process,
    build_jsonl_for_range,
    save_jsonl,
)

from .model_classify import (
    load_system_prompt,
    build_user_prompt_clsuter,
    build_user_prompt_cluster_agg,
    build_user_prompt_subcluster_opinion,
    call_ark_chat_completions,
    parse_cluster_response,
    build_daily_top5_opinion_records,
    PlayerCommunityAnalyzer,
)

__all__ = [
    # 数据处理
    'load_and_process',
    'build_jsonl_for_range',
    'save_jsonl',
    # 模型调用
    'load_system_prompt',
    'build_user_prompt_clsuter',
    'build_user_prompt_cluster_agg',
    'build_user_prompt_subcluster_opinion',
    'call_ark_chat_completions',
    'parse_cluster_response',
    'build_daily_top5_opinion_records',
    'PlayerCommunityAnalyzer',
]
