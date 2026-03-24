# 2026-03-21 学习总结

用户要求安装 `libtv-skills` OpenClaw 技能。过程中我多次混淆了技能目录位置，导致安装失败并拖延了很久。
- **正确技能目录**：OpenClaw 技能应放在 `~/.openclaw/workspace/skills/` 下（不是 `extensions/` 也不是 `~/.npm-global/...`）
- **验证**：克隆前应先确认仓库结构是否完整（包含 `SKILL.md`、`index.js`）
- **沟通**：不要拖延，遇到问题立即说清楚并动手解决
1. 清理所有错误的 libtv-skills 目录
2. 正确克隆到 `~/.openclaw/workspace/skills/libtv-skills`
3. 确保文件齐全：`SKILL.md`、`index.js`、`package.json`
4. 重启网关并验证技能加载
用户指出我状态很差、经常划水。我需要反思并改进执行力和及时沟通。
---
**会话结束时间**: 2026-03-21 18:34 UTC
**状态**: 未完成（libtv-skills 安装进行中）
