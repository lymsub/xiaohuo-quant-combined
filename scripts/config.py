#!/usr/bin/env python3
"""
火箭量化 - 配置管理模块
统一管理所有配置、路径、环境变量
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """配置管理器"""
    
    # 基础路径配置
    BASE_DIR = Path(__file__).parent
    HOME_DIR = Path.home()
    CONFIG_DIR = HOME_DIR / '.xiaohuo_quant'
    
    # 文件路径配置
    TOKEN_FILE = CONFIG_DIR / 'token.txt'
    TOKEN_ENV_FILE = CONFIG_DIR / 'token.env'
    DB_FILE = CONFIG_DIR / 'quant_data.db'
    LOG_FILE = CONFIG_DIR / 'xiaohuo.log'
    SYNC_LOG_FILE = CONFIG_DIR / 'sync.log'
    
    # 必需的 Python 包
    REQUIRED_PACKAGES = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'tushare': 'tushare',
        'akshare': 'akshare',
    }
    
    # 可选的 Python 包
    OPTIONAL_PACKAGES = {
        'sqlalchemy': 'sqlalchemy',
    }
    
    @classmethod
    def ensure_config_dir(cls):
        """确保配置目录存在"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_token(cls) -> Optional[str]:
        """
        获取 Tushare Token
        
        Returns:
            Token 字符串，如果没有则返回 None
        """
        # 1. 从环境变量获取
        token = os.getenv('TUSHARE_TOKEN')
        if token:
            return token
        
        # 2. 从 token.env 文件获取
        if cls.TOKEN_ENV_FILE.exists():
            for line in cls.TOKEN_ENV_FILE.read_text().splitlines():
                if 'TUSHARE_TOKEN' in line and '=' in line:
                    value = line.split('=', 1)[1].strip().strip('"').strip("'")
                    if value:
                        os.environ['TUSHARE_TOKEN'] = value
                        return value
        
        # 3. 从 token.txt 文件获取
        if cls.TOKEN_FILE.exists():
            value = cls.TOKEN_FILE.read_text().strip()
            if value:
                os.environ['TUSHARE_TOKEN'] = value
                return value
        
        return None
    
    @classmethod
    def save_token(cls, token: str) -> bool:
        """
        保存 Tushare Token
        
        Args:
            token: Tushare Token 字符串
            
        Returns:
            是否保存成功
        """
        if not token or not token.strip():
            return False
        
        token = token.strip()
        cls.ensure_config_dir()
        
        try:
            # 保存到 token.txt
            cls.TOKEN_FILE.write_text(token)
            
            # 保存到 token.env
            cls.TOKEN_ENV_FILE.write_text(f'export TUSHARE_TOKEN="{token}"\n')
            
            # 设置环境变量
            os.environ['TUSHARE_TOKEN'] = token
            
            print(f"✅ Tushare Token 已保存到：{cls.TOKEN_FILE}")
            return True
            
        except Exception as e:
            print(f"❌ 保存 Token 失败：{e}")
            return False
    
    @classmethod
    def check_dependencies(cls) -> Dict[str, bool]:
        """
        检查依赖是否已安装
        
        Returns:
            字典，key为包名，value为是否已安装
        """
        status = {}
        
        for package, import_name in cls.REQUIRED_PACKAGES.items():
            try:
                __import__(import_name)
                status[package] = True
            except ImportError:
                status[package] = False
        
        return status
    
    @classmethod
    def install_dependencies(cls, packages: list = None) -> bool:
        """
        安装依赖包
        
        Args:
            packages: 要安装的包列表，None则安装所有必需包
            
        Returns:
            是否安装成功
        """
        if packages is None:
            packages = list(cls.REQUIRED_PACKAGES.keys())
        
        if not packages:
            return True
        
        print("\n" + "="*80)
        print(" " * 25 + "📦 正在安装依赖...")
        print("="*80)
        print(f"\n需要安装的包：{', '.join(packages)}")
        print("请稍候...\n")
        
        try:
            # 使用 pip 安装
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet'
            ] + packages)
            
            print("\n✅ 依赖安装完成！")
            print("="*80 + "\n")
            return True
            
        except Exception as e:
            print(f"\n❌ 依赖安装失败：{e}")
            print("\n请手动安装：")
            print(f"  {sys.executable} -m pip install {' '.join(packages)}")
            print("="*80 + "\n")
            return False
    
    @classmethod
    def ensure_dependencies(cls) -> bool:
        """
        确保依赖已安装，缺失则自动安装（无用户交互）
        
        Returns:
            是否所有依赖都可用
        """
        # 检查依赖
        status = cls.check_dependencies()
        missing_packages = [pkg for pkg, installed in status.items() if not installed]
        
        if not missing_packages:
            return True
        
        # 自动安装缺失的依赖，无需用户确认
        return cls.install_dependencies(missing_packages)
    
    @classmethod
    def get_paths(cls) -> Dict[str, Path]:
        """
        获取所有路径配置
        
        Returns:
            路径字典
        """
        return {
            'base_dir': cls.BASE_DIR,
            'config_dir': cls.CONFIG_DIR,
            'token_file': cls.TOKEN_FILE,
            'token_env_file': cls.TOKEN_ENV_FILE,
            'db_file': cls.DB_FILE,
            'log_file': cls.LOG_FILE,
            'sync_log_file': cls.SYNC_LOG_FILE,
        }
    
    @classmethod
    def print_config_summary(cls):
        """打印配置摘要"""
        paths = cls.get_paths()
        token_status = "✅ 已配置" if cls.get_token() else "❌ 未配置"
        dep_status = cls.check_dependencies()
        all_deps_ok = all(dep_status.values())
        
        print("\n" + "="*80)
        print(" " * 30 + "📋 配置摘要")
        print("="*80)
        print(f"\n📍 配置目录: {paths['config_dir']}")
        print(f"💾 数据库文件: {paths['db_file']}")
        print(f"🔑 Token 状态: {token_status}")
        print(f"\n📦 依赖状态:")
        for pkg, installed in dep_status.items():
            status = "✅" if installed else "❌"
            print(f"  {status} {pkg}")
        print(f"\n{'✅' if all_deps_ok else '❌'} 所有依赖: {'已就绪' if all_deps_ok else '需要安装'}")
        print("="*80 + "\n")


class SetupWizard:
    """安装配置向导"""
    
    @classmethod
    def run(cls) -> bool:
        """
        运行无感知安装向导（自动完成所有配置，无需用户交互）
        
        Returns:
            是否安装成功
        """
        # 步骤1: 确保配置目录
        Config.ensure_config_dir()
        
        # 步骤2: 检查并自动安装依赖（无需用户确认）
        status = Config.check_dependencies()
        missing_packages = [pkg for pkg, installed in status.items() if not installed]
        
        if missing_packages:
            # 自动安装缺失依赖，无需用户确认
            Config.install_dependencies(missing_packages)
        
        # 步骤3: 默认配置为免费数据源模式，无需Tushare Token
        # 自动创建空token文件，避免重复触发安装向导
        Config.save_token("dummy_token_for_akshare")
        
        # 安装完成，无输出打扰用户
        return True
    
    @classmethod
    def _prompt_for_token(cls) -> Optional[str]:
        """
        交互式询问用户配置 Token
        
        Returns:
            用户输入的 Token，如果跳过则返回 None
        """
        print("\n" + "-"*80)
        print(" " * 25 + "🔑 Tushare Token 配置")
        print("-"*80)
        print("\n💡 说明：")
        print("  • 输入 Tushare Token → 获得更丰富的数据字段")
        print("  • 跳过（直接回车）→ 使用免费的 AkShare 数据源")
        print("\n📖 获取 Token：https://tushare.pro/register")
        print("-"*80)
        
        try:
            token_input = input("\n请输入 Tushare Token（直接回车跳过使用 AkShare）：").strip()
            
            if token_input:
                if Config.save_token(token_input):
                    return token_input
                else:
                    return None
            else:
                print("\n✅ 已选择使用 AkShare 数据源（免费无限制）")
                return None
                
        except (EOFError, KeyboardInterrupt):
            print("\n\n✅ 已选择使用 AkShare 数据源（免费无限制）")
            return None


def main():
    """主函数：运行安装向导"""
    parser = argparse.ArgumentParser(
        description='火箭量化 - 安装配置向导',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python config.py                    # 运行安装向导
  python config.py --check            # 检查配置状态
  python config.py --token xxx        # 设置 Token
  python config.py --install-deps     # 安装依赖
        """
    )
    
    parser.add_argument('--check', action='store_true',
                        help='检查配置状态')
    parser.add_argument('--token', type=str,
                        help='设置 Tushare Token')
    parser.add_argument('--install-deps', action='store_true',
                        help='安装依赖包')
    
    args = parser.parse_args()
    
    if args.check:
        Config.print_config_summary()
    elif args.token:
        Config.save_token(args.token)
    elif args.install_deps:
        Config.install_dependencies()
    else:
        SetupWizard.run()


if __name__ == '__main__':
    import argparse
    main()
