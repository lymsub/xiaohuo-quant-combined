#!/usr/bin/env python3
"""
视频生成模块
功能：调用视频生成API生成背景视频
可配置模型参数，支持后续切换其他视频生成模型
"""
import os
import time
import urllib.request
import sys
import requests
import json
from pathlib import Path

# 添加当前目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import DOUBAN_CONFIG

# 配置区域
CONFIG = {
    # 模型配置（可根据需要切换其他模型）
    "model": DOUBAN_CONFIG["video_model"],
    "api_key": DOUBAN_CONFIG["api_key"],
    "base_url": DOUBAN_CONFIG["api_base_url"],
    
    # 视频生成参数
    "prompt": "专业中文财经早报背景视频，蓝色金融风格，动态滚动的中文K线图和数据图表，无任何英文内容，界面简洁专业，适合国内财经节目",
    "video_duration": 12,  # 生成12秒背景视频，后续循环到1分钟
    "output_dir": "/root/.openclaw/workspace/output/videos/",
    "default_output_name": "background_video.mp4"
}



def generate_background_video(prompt=None, output_path=None):
    """生成背景视频
    Args:
        prompt: 自定义提示词，不填则使用默认配置
        output_path: 输出路径，不填则使用默认配置
    Returns:
        生成的视频本地路径
    """
    # 创建输出目录
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    
    # 使用默认值
    if not prompt:
        prompt = CONFIG["prompt"]
    if not output_path:
        output_path = os.path.join(CONFIG["output_dir"], CONFIG["default_output_name"])
    
    api_key = CONFIG["api_key"]
    base_url = CONFIG["base_url"].rstrip("/")
    model = CONFIG["model"]
    
    print(f"开始生成背景视频，模型：{model}")
    
    try:
        # 1. 创建生成任务
        create_url = f"{base_url}/contents/generations/tasks"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "content": [
                {
                    "type": "text",
                    "text": f"{prompt} --duration 12 --watermark false"
                }
            ]
        }
        
        response = requests.post(create_url, headers=headers, json=payload)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data["id"]
        print(f"任务已创建，ID：{task_id}")
        
        # 2. 轮询任务状态
        get_url = f"{base_url}/contents/generations/tasks/{task_id}"
        while True:
            response = requests.get(get_url, headers=headers)
            response.raise_for_status()
            result = response.json()
            status = result["status"]
            
            if status == "succeeded":
                video_url = result["content"]["video_url"]
                print(f"视频生成成功，开始下载...")
                # 下载视频
                urllib.request.urlretrieve(video_url, output_path)
                print(f"视频已保存到：{output_path}")
                return output_path
            elif status == "failed":
                print(f"视频生成失败：{result.get('error', '未知错误')}")
                raise Exception(f"视频生成失败：{result.get('error', '未知错误')}")
            else:
                print(f"任务状态：{status}，等待中...")
                time.sleep(10)
                
    except Exception as e:
        print(f"视频生成出错：{e}")
        # 生成失败时返回默认背景视频，保证功能可用
        default_video = os.path.join(SCRIPT_DIR, "full_cn_morning.mp4")
        if os.path.exists(default_video):
            print(f"使用默认背景视频：{default_video}")
            return default_video
        raise e

if __name__ == "__main__":
    # 测试生成
    video_path = generate_background_video()
    print(f"生成的视频路径：{video_path}")
