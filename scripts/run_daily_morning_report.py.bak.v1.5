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

def upload_to_feishu_drive(local_path, file_name):
    """上传文件到飞书云盘，返回飞书内链"""
    try:
        import json
        # 调用feishu_drive_file上传接口
        cmd = f'openclaw tool feishu_drive_file --action upload --file_path "{local_path}" --type file'
        result = os.popen(cmd).read()
        # 解析返回结果
        try:
            result_json = json.loads(result)
            if "file_token" in result_json:
                return f"https://bytedance.feishu.cn/file/{result_json['file_token']}"
        except:
            pass
        # 如果解析失败，尝试从输出中提取链接
        if "https://bytedance.feishu.cn/file/" in result:
            for line in result.split("\n"):
                if "https://bytedance.feishu.cn/file/" in line:
                    return line.strip()
        print(f"飞书云盘上传失败：{result}")
        return None
    except Exception as e:
        print(f"飞书云盘上传异常：{e}")
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
    
    # 校验已存在视频是否为有效完整视频（时长≥30秒）
    valid_exist = False
    if not force_regenerate and os.path.exists(exist_final_video):
        # 获取视频时长
        try:
            import subprocess
            result = subprocess.run(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {exist_final_video}", shell=True, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            if duration >= 30:
                valid_exist = True
            else:
                print(f"⚠️ 已存在视频时长仅{duration}秒，为无效模板，强制重新生成...")
        except:
            print("⚠️ 无法校验已存在视频时长，强制重新生成...")
    
    if valid_exist:
        print(f"VIDEO_PATH={exist_final_video}")
        print("\n✅ 早报视频生成完成！")
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
            # 禁止正常生成流程使用默认模板，必须生成动态背景
            print("⚠️ 配置generate_new_background为False，强制生成动态背景...")
            video_path = get_cached_background()
            backup_video_path = os.path.join(today_save_dir, f"background_{today_str}.mp4")
            os.system(f"cp {video_path} {backup_video_path}")
        
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
        feishu_url = None
        
        # 先上传到公网COS
        # 仅输出本地视频路径，上传逻辑交给OpenClaw Skill层处理
        print(f"VIDEO_PATH={backup_final_path}")
        print("\n✅ 早报视频生成完成！")
        return backup_final_path
        
    except Exception as e:
        print(f"\n❌ 流程执行失败：{e}")
        raise e

if __name__ == "__main__":
    main()
