#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局配置文件
"""
import os
import json
from typing import Dict, Any

# 基础配置
BASE_CONFIG = {
    "data_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
    "cache_db": os.path.join(os.path.dirname(os.path.abspath(__file__)), "quant_data.db"),
    "log_level": "INFO",
}

# 数据源配置
DATA_SOURCES = [
    # 内置数据源，优先级从高到低
    {
        "name": "sqlite_cache",
        "type": "sqlite",
        "enabled": True,
        "priority": 1,
        "config": {
            "db_path": BASE_CONFIG["cache_db"]
        }
    },
    {
        "name": "tushare",
        "type": "api",
        "enabled": True,
        "priority": 2,
        "config": {
            "api_key": os.getenv("TUSHARE_API_KEY", ""),
            "endpoint": "http://api.tushare.pro"
        }
    },
    {
        "name": "akshare",
        "type": "lib",
        "enabled": True,
        "priority": 3,
        "config": {}
    }
    # 用户自定义数据源可以在这里添加，或者从配置文件动态加载
]

# 自定义算法配置
CUSTOM_ALGORITHMS = [
    # 示例配置，用户可以在这里添加自己的算法
    # {
    #     "name": "my_custom_strategy",
    #     "type": "http_api",
    #     "enabled": True,
    #     "config": {
    #         "url": "http://your-server/api/generate_signals",
    #         "api_key": "your-api-key",
    #         "timeout": 10
    #     }
    # }
]

# 豆包API配置
DOUBAN_CONFIG = {
    "api_key": os.getenv("VOLC_ARK_API_KEY", os.getenv("DOUBAO_API_KEY", "")),
    "api_base_url": os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
    "video_api": "https://ark.cn-beijing.volces.com/api/v3/videos/generations",
    "video_model": "doubao-seedance-1-5-pro-251215",
    "video_style": "专业金融早报背景，抽象科技感动态数据流动画，蓝色紫色渐变光效，粒子流动，数字波浪，无任何文字和K线图，简洁大气科技感，适合财经新闻播报场景",
    "video_duration": 12
}

# 对象存储配置（可选）
COS_CONFIG = {
    "endpoint": os.getenv("COS_ENDPOINT", "https://lyming.tos-cn-beijing.volces.com/"),
    "upload_enabled": os.getenv("COS_UPLOAD_ENABLED", "true").lower() == "true"
}

# 飞书配置
FEISHU_CONFIG = {
    "webhook": os.getenv("FEISHU_WEBHOOK", ""),
    "push_enabled": os.getenv("FEISHU_PUSH_ENABLED", "false").lower() == "true",
    "send_video_directly": os.getenv("FEISHU_SEND_VIDEO", "true").lower() == "true"  # 没有COS时直接发送视频到飞书群
}

# 早报配置
MORNING_REPORT_CONFIG = {
    "enabled": True,
    "run_time": "08:30",  # 每天早上8:30运行
    "video_enabled": os.getenv("MORNING_REPORT_VIDEO_ENABLED", "false").lower() == "true",
    "push_enabled": FEISHU_CONFIG["push_enabled"]
}

def load_custom_config(config_path: str = "custom_config.json") -> Dict[str, Any]:
    """加载用户自定义配置文件"""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                custom_config = json.load(f)
                # 合并配置
                if "data_sources" in custom_config:
                    DATA_SOURCES.extend(custom_config["data_sources"])
                if "custom_algorithms" in custom_config:
                    CUSTOM_ALGORITHMS.extend(custom_config["custom_algorithms"])
                if "douban" in custom_config:
                    DOUBAN_CONFIG.update(custom_config["douban"])
                if "cos" in custom_config:
                    COS_CONFIG.update(custom_config["cos"])
                if "feishu" in custom_config:
                    FEISHU_CONFIG.update(custom_config["feishu"])
                if "morning_report" in custom_config:
                    MORNING_REPORT_CONFIG.update(custom_config["morning_report"])
                print(f"已加载自定义配置文件: {config_path}")
                return custom_config
        except Exception as e:
            print(f"加载自定义配置失败: {e}")
    return {}

# 兼容旧版本导入
class Config:
    """兼容旧版本配置类"""
    pass

class SetupWizard:
    """兼容旧版本配置向导类"""
    pass

# 初始化创建数据目录
os.makedirs(BASE_CONFIG["data_dir"], exist_ok=True)

# 加载自定义配置
load_custom_config()
