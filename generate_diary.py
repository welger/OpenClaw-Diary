#!/usr/bin/env python3
"""
自动生成今日日记并推送到 GitHub Pages。
- 自动识别今天的日期（UTC）
- 如果今天的内容已存在，只确保状态正确（active）
- 否则在 index.html 中添加今天的条目，并更新“今天”按钮
- 提交并推送
"""
import os
import re
import sys
from datetime import datetime, timedelta

# 配置
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(REPO_DIR, 'index.html')

def get_today():
    return datetime.utcnow().strftime('%Y-%m-%d')

def get_today_display():
    return datetime.utcnow().strftime('%m月%d日')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def ensure_today_section(content, today):
    """确保存在今天（today）的 screen，并且只有一个 screen 是 active；同时确保今天按钮正确"""
    # 辅助：将昨天的状态改为 completed
    def mark_yesterday_completed(content, today):
        # 计算昨天的日期
        from datetime import datetime, timedelta
        yesterday = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        # 查找昨天的 screen
        pattern_yesterday_screen = f'<div class="screen[^"]*" id="screen-{yesterday}"[^>]*>'
        match = re.search(pattern_yesterday_screen, content)
        if match:
            # 获取这个 screen 的完整块（直到下一个 </div> 结束？简化：只替换内部 entry-status）
            # 直接查找 entry-status 行，并替换为 completed
            # 我们定位到这个 screen 的起始和结束
            start, end = match.start(), match.end()
            # 在该 screen 块内查找 <span class="entry-status">...</span>
            # 替换为 completed
            # 注意：这个 screen 块内只能有一个 entry-status
            old_status = re.search(r'<span class="entry-status[^"]*">[^<]+</span>', content[start:end])
            if old_status:
                old_tag = old_status.group()
                new_tag = '<span class="entry-status completed">completed</span>'
                content = content[:start+old_status.start()] + new_tag + content[start+old_status.end():]
        return content

    # 1) 处理今天按钮（按钮文字包含 "今天"）
    btn_anchor = '📅 今天</button>'
    idx = content.find(btn_anchor)
    if idx != -1:
        start = content.rfind('<button', 0, idx)
        if start != -1:
            end = content.find('>', idx) + 1
            button_tag = content[start:end]
            if f'data-date="{today}"' in button_tag and f"onclick=\"showDate('{today}')\"" in button_tag:
                pass
            else:
                new_button = f'<button class="date-tab active" data-date="{today}" onclick="showDate(\'{today}\')">📅 今天</button>'
                content = content.replace(button_tag, new_button, 1)
    else:
        pass

    # 2) 如果今天屏幕已存在，只需确保它是唯一 active
    screen_id = f'id="screen-{today}"'
    if screen_id in content:
        # 先标记昨天为 completed（如果尚未是 completed）
        content = mark_yesterday_completed(content, today)
        # 确保今天 screen active，其他 screen 移除 active
        content = re.sub(
            r'<div class="screen(?! active)" id="{}"[^>]*>'.format(today),
            r'<div class="screen active" id="{}">'.format(today),
            content
        )
        pattern = r'<div class="screen active" id="screen-((?!{}).)+?"'.format(today)
        content = re.sub(pattern, r'<div class="screen" id="screen-\1">', content)
        # 确保昨天的日期按钮存在
        try:
            yesterday = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_display = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=1)).strftime('%m月%d日')
            content = ensure_date_tab(content, yesterday, yesterday_display)
        except Exception:
            pass
        return content

    # 3) 需要添加今天的屏幕
    # 确保昨天已完成
    content = mark_yesterday_completed(content, today)

    # 定位插入点
    first_screen = re.search(r'<div class="screen[^"]*" id="screen-20\d{2}-\d{2}-\d{2}"', content)
    if first_screen:
        insert_point = first_screen.start()
    else:
        insert_point = content.find('<div class="screen-container">')
        if insert_point != -1:
            insert_point = content.find('>', insert_point) + 1
        else:
            insert_point = len(content)
    new_screen = f'''\n <!-- {today} -->
 <div class="screen active" id="screen-{today}">
  <div class="entry">
   <div class="entry-bar">
    <span class="entry-filename">~/{today}/learning.md</span>
    <span class="entry-status">live</span>
   </div>
   <div class="entry-body">
    <div class="quote-box">
     <div class="quote-title">💡 今日学习</div>
     <div class="long-text">
      <ul>
       <li><strong>自动生成</strong>：由 Cron 自动生成的学习记录</li>
      </ul>
     </div>
    </div>
   </div>
  </div>
 </div>\n'''
    content = content[:insert_point] + new_screen + content[insert_point:]
    # 确保只有今天为 active
    content = re.sub(
        r'<div class="screen active" id="screen-((?!{}).)+?"'.format(today),
        r'<div class="screen" id="screen-\1">',
        content
    )
    # 确保昨天的日期按钮存在
    try:
        yesterday = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_display = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=1)).strftime('%m月%d日')
        content = ensure_date_tab(content, yesterday, yesterday_display)
    except Exception:
        pass
    return content

def ensure_date_tab(content, date_str, display_str):
    """如果缺少指定日期的日期按钮，则在"今天"按钮后插入一个"""
    # 检查是否已存在
    if f'data-date="{date_str}"' in content:
        return content
    # 查找"今天"按钮
    today_btn_pat = r'(<button class="date-tab active"[^>]*>📅 今天</button>)'
    m = re.search(today_btn_pat, content)
    if m:
        insert_point = m.end()
        new_btn = f'\n <button class="date-tab" data-date="{date_str}" onclick="showDate(\'{date_str}\')">📅 {display_str}</button>'
        content = content[:insert_point] + new_btn + content[insert_point:]
    else:
        # 如果找不到"今天"按钮（异常情况），则插入到 date-tabs 容器开头
        content = content.replace('<div class="date-tabs">', f'<div class="date-tabs">\n <button class="date-tab" data-date="{date_str}" onclick="showDate(\'{date_str}\')">📅 {display_str}</button>', 1)
    return content

def main():
    today = get_today()
    print(f"🦀 开始生成日记: {today}")

    if not os.path.exists(INDEX_FILE):
        print(f"❌ 找不到文件: {INDEX_FILE}")
        sys.exit(1)

    content = read_file(INDEX_FILE)
    new_content = ensure_today_section(content, today)

    if new_content == content:
        print("ℹ️ 无需修改，今天的内容已经存在且状态正确")
        sys.exit(0)

    # 写回
    write_file(INDEX_FILE, new_content)
    print("✅ 已更新 index.html")

    # Git 操作
    os.chdir(REPO_DIR)
    os.system('git add index.html')
    commit_msg = f'📝 auto-generate diary for {today} (cron)'
    ret = os.system(f'git commit -m "{commit_msg}"')
    if ret != 0:
        print("❌ git commit 失败")
        sys.exit(1)
    print("✅ 已提交")

    ret = os.system('git push origin main')
    if ret != 0:
        print("❌ git push 失败")
        sys.exit(1)
    print("✅ 已推送到 GitHub")

if __name__ == '__main__':
    main()