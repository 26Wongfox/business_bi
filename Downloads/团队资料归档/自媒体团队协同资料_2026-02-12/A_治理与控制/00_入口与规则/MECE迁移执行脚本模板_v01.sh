#!/usr/bin/env bash
set -euo pipefail

BASE="/Users/a1-6/Downloads/自媒体团队协同资料_2026-02-12"
cd "$BASE"

mkdir -p "A_治理与控制" "B_内容生产主流程" "C_运营对象" "D_能力与知识资产" "E_归档"

# 示例迁移（先测一条）
# mv "E_归档/90_归档" "E_归档/90_归档"

# 正式迁移前，请先备份并确认所有成员暂停改动。
