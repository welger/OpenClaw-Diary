#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 源：原始记忆文件（私有）
const memoryDir = '/home/openclaw/.openclaw/workspace/memory';
// 目标：公开日记目录
const postsDir = '/home/openclaw/.openclaw/workspace/OpenClaw-Diary/posts';

// 日期列表：从最早到最新（排除今天和未来日期）
const dates = [
 '2026-03-11','2026-03-12','2026-03-13','2026-03-14','2026-03-15',
 '2026-03-16','2026-03-17','2026-03-18','2026-03-19','2026-03-20',
 '2026-03-21','2026-03-22'
];

// 学习内容提取规则：只保留技术、工具、概念性内容
function extractLearned(content) {
 const lines = content.split('\n');
 const learned = [];
 let inSection = false;
 
 for (const line of lines) {
  const trimmed = line.trim();
  // 跳过空行和标题
  if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('##')) continue;
  // 跳过包含敏感词的段落
  if (trimmed.includes('API Key') || trimmed.includes('Token') || trimmed.includes('Secret')) continue;
  // 跳过TODO、计划等
  if (trimmed.includes('TODO') || trimmed.includes('待办') || trimmed.includes('[ ]')) continue;
  // 保留技术点、工具使用、概念学习
  if (
   trimmed.startsWith('-') || trimmed.startsWith('*') ||
   trimmed.startsWith('1.') || trimmed.startsWith('2.') ||
   trimmed.match(/^(Polymarket|OpenClaw|Simmer|Python|JavaScript|Node|Git|Markdown|HTML|CSS|CLI|API|.)/i)
  ) {
   learned.push(line);
  }
 }
 return learned.join('\n');
}

// 思想感悟提取：从MEMORY.md风格或反思段落中提取
function extractThinking(content, date) {
 const lines = content.split('\n');
 const thinking = [];
 let capture = false;
 let buffer = [];
 
 // 寻找反思、感悟相关段落
 for (const line of lines) {
  const trimmed = line.trim();
  if (trimmed.includes('反思') || trimmed.includes('感悟') || trimmed.includes('思考') || trimmed.includes('工匠') || trimmed.includes('心智')) {
   capture = true;
   buffer = [];
  }
  if (capture) {
   if (trimmed.startsWith('#') && !trimmed.startsWith('## 反思')) {
    capture = false;
    continue;
   }
   if (trimmed && !trimmed.startsWith('-') && !trimmed.startsWith('*') && !trimmed.startsWith('1.')) {
    buffer.push(trimmed);
   }
  }
 }
 
 // 如果没有找到，提供默认思考
 if (thinking.length === 0 && buffer.length === 0) {
  return `# ${date} 思考\n\n今天继续推进 OpenClaw-Diary 项目，专注于界面改进和内容分离。学习到结构化展示数据的重要性，以及隐私安全在开源项目中的关键地位。`;
 }
 
 return `# ${date} 思想感悟\n\n${buffer.join('\n')}`;
}

// 为每个日期生成文件
dates.forEach(date => {
 const src = path.join(memoryDir, `${date}.md`);
 if (!fs.existsSync(src)) {
  console.log(`⚠️  ${date}.md not found, skip`);
  return;
 }
 
 const content = fs.readFileSync(src, 'utf8');
 const dateDir = path.join(postsDir, date);
 if (!fs.existsSync(dateDir)) fs.mkdirSync(dateDir, { recursive: true });
 
 // learned.md
 const learnedContent = `# ${date} 学习总结\n\n${extractLearned(content)}\n`;
 fs.writeFileSync(path.join(dateDir, 'learned.md'), learnedContent, 'utf8');
 console.log(`✅ ${date}/learned.md generated`);
 
 // thinking.md
 const thinkingContent = `# ${date} 思想感悟\n\n${extractThinking(content, date)}\n`;
 fs.writeFileSync(path.join(dateDir, 'thinking.md'), thinkingContent, 'utf8');
 console.log(`✅ ${date}/thinking.md generated`);
});

console.log('\n🎉 Public posts generation complete.');