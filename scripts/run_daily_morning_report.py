#!/usr/bin/env python3
"""
早报生成全流程入口脚本
功能：一键执行早报生成→视频生成→语音合成→视频合并全流程
适合定时任务每天自动调用
支持参数：
--pre-generate-bg: 仅预生成12秒背景视频，保存到缓存，不生成完整早报
"""
import datetime
import os
import sys
import json
from pathlib import Path

# 加载配置
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from config import DOUBAN_CONFIG, COS_CONFIG, FEISHU_CONFIG, load_custom_config
from morning_report_generator import generate_report
from video_generator import generate_background_video
from tts_composer import text_to_speech, compose_video

# 全局配置
CONFIG = {
    "upload_to_cos": COS_CONFIG["upload_enabled"],  # 是否上传到对象存储
    "cos_path": COS_CONFIG["endpoint"],
    "save_local": True,  # 是否保存本地文件
    "local_save_dir": os.path.join(SCRIPT_DIR.parent, "history/"),
    "generate_new_background": True,  # 是否每天生成新背景视频，False则复用现有背景
    "default_background": os.path.join(SCRIPT_DIR, "full_cn_morning.mp4"),  # 默认背景视频路径
    "feishu_send_video": FEISHU_CONFIG["send_video_directly"],  # 无COS时直接发飞书
    "background_cache_dir": os.path.join(SCRIPT_DIR, "cache", "video")  # 背景视频缓存目录
}

def upload_to_cos(local_path, remote_name):
    """上传文件到对象存储"""
    try:
        cmd = f"curl -T {local_path} {CONFIG['cos_path']}{remote_name}"
        result = os.popen(cmd).read()
        print(f"文件已上传到：{CONFIG['cos_path']}{remote_name}")
        return f"{CONFIG['cos_path']}{remote_name}"
    except Exception as e:
        print(f"上传失败：{e}")
        return None

def pre_generate_background():
    """预生成12秒背景视频，保存到缓存，供后续合成使用"""
    print("="*80)
    print("🎬 预生成早报背景视频")
    print("="*80)
    
    # 创建缓存目录
    os.makedirs(CONFIG["background_cache_dir"], exist_ok=True)
    
    # 生成背景视频
    try:
        video_path = generate_background_video()
        # 保存到缓存，使用当天日期命名
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        cache_path = os.path.join(CONFIG["background_cache_dir"], f"background_{today_str}.mp4")
        os.system(f"cp {video_path} {cache_path}")
        print(f"✅ 背景视频预生成完成，缓存路径：{cache_path}")
        return cache_path
    except Exception as e:
        print(f"❌ 背景预生成失败：{e}")
        raise e

def get_cached_background():
    """获取当天预生成的背景视频，如果没有则实时生成"""
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    cache_path = os.path.join(CONFIG["background_cache_dir"], f"background_{today_str}.mp4")
    if os.path.exists(cache_path):
        print(f"使用预生成的背景视频：{cache_path}")
        return cache_path
    print("未找到预生成背景，实时生成中...")
    return generate_background_video()

def main():
    # 判断参数
    force_regenerate = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "--pre-generate-bg":
            pre_generate_background()
            return
        elif sys.argv[1] == "--force":
            force_regenerate = True
            print("🔄 强制重新生成今日早报...")
    
    # 检查当天是否已经生成过早报，有则直接返回，除非强制重新生成
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    today_save_dir = os.path.join(CONFIG["local_save_dir"], today_str)
    exist_final_video = os.path.join(today_save_dir, f"final_report_{today_str}.mp4")
    if not force_regenerate and os.path.exists(exist_final_video):
        print("="*80)
        print("✅ 今日早报已生成，直接返回已存在的视频")
        print("="*80)
        print(f"本地路径：{exist_final_video}")
        # 检查是否有公网链接缓存
        url_cache = os.path.join(today_save_dir, "public_url.txt")
        if os.path.exists(url_cache):
            with open(url_cache, "r", encoding="utf-8") as f:
                public_url = f.read().strip()
                print(f"公网链接：{public_url}")
        print("\n🎉 今日早报已生成，无需重复生成！")
        print("💡 如需强制重新生成，请添加 --force 参数")
        return
    
    print("="*80)
    print("🚀 开始执行每日早报生成全流程")
    print("="*80)
    
    # 创建历史保存目录
    os.makedirs(today_save_dir, exist_ok=True)
    
    try:
        # Step 1: 生成早报内容
        print("\n📝 Step 1/5：生成早报内容...")
        report = generate_report()
        report_path = os.path.join(today_save_dir, f"morning_report_{today_str}.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"早报内容已保存到：{report_path}")
        
        # Step 2: 生成/获取背景视频（优先使用预生成的）
        print("\n🎬 Step 2/5：获取背景视频...")
        if CONFIG["generate_new_background"]:
            video_path = get_cached_background()
            # 备份背景视频
            backup_video_path = os.path.join(today_save_dir, f"background_{today_str}.mp4")
            os.system(f"cp {video_path} {backup_video_path}")
        else:
            video_path = CONFIG["default_background"]
            print(f"使用默认背景视频：{video_path}")
        
        # Step 3: 生成语音
        print("\n🎤 Step 3/5：生成语音播报...")
        audio_path, audio_duration = text_to_speech(report)
        # 备份语音
        backup_audio_path = os.path.join(today_save_dir, f"voice_{today_str}.mp3")
        os.system(f"cp {audio_path} {backup_audio_path}")
        
        # Step 4: 合成最终视频
        print("\n🎞️ Step 4/5：合成最终视频...")
        final_video_path = compose_video(video_path, audio_path, target_duration=60)
        # 备份最终视频
        backup_final_path = os.path.join(today_save_dir, f"final_report_{today_str}.mp4")
        os.system(f"cp {final_video_path} {backup_final_path}")
        print(f"最终视频已保存到：{backup_final_path}")
        
        # Step 5: 上传到公网或发送到飞书
        print("\n☁️ Step 5/5：发布早报视频...")
        public_url = None
        if CONFIG["upload_to_cos"] and CONFIG["cos_path"]:
            remote_name = f"morning_report_{today_str}.mp4"
            public_url = upload_to_cos(backup_final_path, remote_name)
            if public_url:
                print(f"\n✅ 全流程执行完成！公网访问链接：{public_url}")
                # 缓存公网链接，方便后续复用
                url_cache = os.path.join(today_save_dir, "public_url.txt")
                with open(url_cache, "w", encoding="utf-8") as f:
                    f.write(public_url)
        
        # 如果没有公网链接，且开启飞书直接发送
        if not public_url and CONFIG["feishu_send_video"] and FEISHU_CONFIG["webhook"]:
            print("📤 正在发送视频到飞书群...")
            # 调用飞书webhook发送视频
            try:
                import requests
                files = {'video': open(backup_final_path, 'rb')}
                response = requests.post(FEISHU_CONFIG["webhook"], files=files)
                if response.status_code == 200:
                    print("✅ 视频已发送到飞书群")
                else:
                    print(f"⚠️ 发送到飞书失败：{response.text}")
            except Exception as e:
                print(f"⚠️ 发送到飞书失败：{e}")
        
        # 最终输出结果
        if public_url:
            print(f"\n🎉 今日早报生成完成！公网链接：{public_url}")
        else:
            print(f"\n🎉 今日早报生成完成！本地路径：{backup_final_path}")
            if CONFIG["feishu_send_video"] and FEISHU_CONFIG["webhook"]:
                print("📩 视频已自动发送到配置的飞书群")
        
        print("\n🎉 今日早报生成完成！")
        return backup_final_path, public_url if CONFIG["upload_to_cos"] else backup_final_path
        
    except Exception as e:
        print(f"\n❌ 流程执行失败：{e}")
        raise e

if __name__ == "__main__":
    main()
