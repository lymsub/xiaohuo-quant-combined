#!/usr/bin/env python3
"""
午盘视频生成全流程入口脚本
功能：一键执行午盘数据获取→内容生成→视频生成→语音合成→视频合并全流程
适合定时任务每天自动调用
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

def get_midday_report():
    """生成午盘报告内容"""
    from portfolio_manager import get_portfolio_manager
    from return_tracker import get_return_tracker
    
    manager = get_portfolio_manager()
    portfolio = manager.list_portfolio(status='holding')
    
    tracker = get_return_tracker()
    result = tracker.track_return(tracking_time='midday')
    
    # 构建报告内容
    report = f"""
📊 高客秘书午盘收益报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

📈 整体表现
- 总资产：{result['portfolio_summary']['total_market_value']:.2f}元
- 总成本：{result['portfolio_summary']['total_cost']:.2f}元
- 总盈亏：{result['portfolio_summary']['total_profit']:.2f}元
- 盈亏比例：{result['portfolio_summary']['total_profit_pct']:.2f}%
- 日收益：{result['daily_return_pct']:.2f}%

🏆 最佳表现
- 贡献最大：{result['attribution']['top_contributor']['name']}（{result['attribution']['top_contributor']['profit']:.2f}元，{result['attribution']['top_contributor']['profit_pct']:.2f}%）

📉 需要关注
- 贡献最小：{result['attribution']['bottom_contributor']['name']}（{result['attribution']['bottom_contributor']['profit']:.2f}元，{result['attribution']['bottom_contributor']['profit_pct']:.2f}%）

📊 持仓统计
- 盈利股票：{result['attribution']['profit_count']}只
- 亏损股票：{result['attribution']['loss_count']}只
- 胜率：{result['attribution']['win_rate']:.2f}%

⚠️ 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。
    """.strip()
    
    return report

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
    print("="*80)
    print("🚀 开始执行每日午盘视频生成全流程")
    print("="*80)
    
    # 创建历史保存目录
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    today_save_dir = os.path.join(CONFIG["local_save_dir"], today_str)
    os.makedirs(today_save_dir, exist_ok=True)
    
    try:
        # Step 1: 生成午盘内容
        print("\n📝 Step 1/5：生成午盘内容...")
        report = get_midday_report()
        report_path = os.path.join(today_save_dir, f"midday_report_{today_str}.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"午盘内容已保存到：{report_path}")
        
        # Step 2: 获取背景视频
        print("\n🎬 Step 2/5：获取背景视频...")
        video_path = get_cached_background()
        backup_video_path = os.path.join(today_save_dir, f"midday_background_{today_str}.mp4")
        os.system(f"cp {video_path} {backup_video_path}")
        
        # Step 3: 生成语音
        print("\n🎤 Step 3/5：生成语音播报...")
        audio_path, audio_duration = text_to_speech(report)
        backup_audio_path = os.path.join(today_save_dir, f"midday_voice_{today_str}.mp3")
        os.system(f"cp {audio_path} {backup_audio_path}")
        
        # Step 4: 合成最终视频
        print("\n🎞️ Step 4/5：合成最终视频...")
        final_video_path = compose_video(video_path, audio_path, target_duration=60)
        backup_final_path = os.path.join(today_save_dir, f"midday_final_{today_str}.mp4")
        os.system(f"cp {final_video_path} {backup_final_path}")
        print(f"最终视频已保存到：{backup_final_path}")
        
        # Step 5: 输出视频路径
        print("\n📤 Step 5/5：输出午盘视频路径...")
        print(f"VIDEO_PATH={backup_final_path}")
        print("\n✅ 午盘视频生成完成！")
        return backup_final_path
        
    except Exception as e:
        print(f"\n❌ 流程执行失败：{e}")
        raise e

if __name__ == "__main__":
    main()
