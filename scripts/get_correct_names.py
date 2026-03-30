#!/usr/bin/env python3
"""
获取持仓股票的正确名称
"""

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / '.xiaohuo_quant' / 'quant_data.db'

print("=" * 80)
print("  📊 获取持仓股票的正确名称")
print("=" * 80)
print()

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# 持仓的ts_code列表
portfolio_codes = [
    '603283.SH',
    '300969.SZ',
    '300919.SZ',
    '002219.SZ',
    '002866.SZ',
]

print("📦 查询持仓股票的正确名称:")
print("-" * 80)

stock_names = {}
for code in portfolio_codes:
    cursor.execute("SELECT name FROM stock_basic WHERE ts_code = ?", (code,))
    result = cursor.fetchone()
    
    if result:
        name = result[0]
        stock_names[code] = name
        print(f"  ✅ {code} - {name}")
    else:
        print(f"  ❌ {code} - (未找到名称)")
        stock_names[code] = code

print()
print("=" * 80)
print("  📋 股票名称映射:")
print("-" * 80)
for code, name in stock_names.items():
    print(f"  '{code}': '{name}',")

conn.close()
print("=" * 80)
