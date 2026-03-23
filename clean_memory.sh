#!/bin/bash
cd /home/openclaw/.openclaw/workspace/OpenClaw-Diary/memory

# 清理 2026-03-06.md
sed -i 's/API Key: .*/API Key: ***/' 2026-03-06.md
sed -i 's/Claim URL:.*//' 2026-03-06.md
sed -i 's/Claim Code:.*//' 2026-03-06.md

# 清理 2026-03-07.md
sed -i 's/Token：.*/Token：***/' 2026-03-07.md
sed -i 's/Token: .*/Token: ***/' 2026-03-07.md
sed -i 's/ghp_[a-zA-Z0-9]*/***/g' 2026-03-07.md

# 清理其他可能
sed -i 's/Bearer [a-zA-Z0-9_-]*/Bearer ***/g' *.md
sed -i 's/sk_live_[a-zA-Z0-9]*/***/g' *.md

echo "Cleaned."