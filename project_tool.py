#!/usr/bin/env python3
"""
项目命令行工具
用法:
    python project_tool.py list                    # 列出所有项目
    python project_tool.py view <项目名>            # 查看项目详情
    python project_tool.py create <项目名> <描述>   # 创建项目
    python project_tool.py delete <项目名>          # 删除项目
    python project_tool.py add-milestone <项目名> <标题> [描述]  # 添加里程碑
    python project_tool.py discuss <项目名> <角色> <内容>        # 添加讨论
    python project_tool.py progress <项目名>        # 查看进度
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from projects_manager import (
    list_projects, get_project, create_project, delete_project
)

def print_json(data):
    """美化打印 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        projects = list_projects()
        if not projects:
            print("\n📂 当前没有项目\n")
            return
        print("\n📂 项目列表")
        print("="*60)
        for p in projects:
            status_icon = {"active": "🟢", "completed": "✅", "paused": "⏸️"}.get(p["status"], "🟢")
            print(f"{status_icon} {p['name']}")
            print(f"   {p['description']}...")
            print(f"   📋 里程碑: {p['milestones_count']} | 💬 讨论: {p['discussions_count']}")
            print()
    
    elif command == "view":
        if len(sys.argv) < 3:
            print("用法: python project_tool.py view <项目名>")
            return
        name = sys.argv[2]
        project = get_project(name)
        if not project:
            print(f"❌ 项目 '{name}' 不存在")
            return
        
        print("\n" + "="*60)
        print(f"📋 项目: {project.name}")
        print("="*60)
        print(f"\n📝 描述: {project.description or '暂无描述'}")
        print(f"📅 创建时间: {project.created_at}")
        print(f"🔄 更新时间: {project.updated_at}")
        print(f"📊 状态: {project.status}")
        
        # 里程碑
        print(f"\n📍 里程碑 ({len(project.milestones)})")
        print("-"*40)
        for m in project.milestones:
            status_icon = {"pending": "⏳", "completed": "✅", "in_progress": "🔄"}.get(m["status"], "⏳")
            print(f"{status_icon} [{m['id']}] {m['title']}")
            if m.get("description"):
                print(f"    {m['description']}")
        
        # 讨论
        print(f"\n💬 讨论记录 ({len(project.discussions)})")
        print("-"*40)
        for d in project.discussions:
            role_icon = {"user": "👤", "ai": "🤖", "admin": "👑"}.get(d["role"], "👤")
            print(f"{role_icon} {d['role']}: {d['content'][:100]}")
            print(f"    └ {d['timestamp']}")
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("用法: python project_tool.py create <项目名> [描述]")
            return
        name = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        project = create_project(name, description)
        print(f"✅ 项目 '{name}' 创建成功！")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("用法: python project_tool.py delete <项目名>")
            return
        name = sys.argv[2]
        if delete_project(name):
            print(f"✅ 项目 '{name}' 已删除")
        else:
            print(f"❌ 项目 '{name}' 不存在")
    
    elif command == "add-milestone":
        if len(sys.argv) < 4:
            print("用法: python project_tool.py add-milestone <项目名> <标题> [描述]")
            return
        name = sys.argv[2]
        title = sys.argv[3]
        description = sys.argv[4] if len(sys.argv) > 4 else ""
        project = get_project(name)
        if not project:
            print(f"❌ 项目 '{name}' 不存在")
            return
        m = project.add_milestone(title, description)
        print(f"✅ 里程碑 '[{m['id']}] {title}' 已添加")
    
    elif command == "discuss":
        if len(sys.argv) < 5:
            print("用法: python project_tool.py discuss <项目名> <角色> <内容>")
            return
        name = sys.argv[2]
        role = sys.argv[3]
        content = " ".join(sys.argv[4:])
        project = get_project(name)
        if not project:
            print(f"❌ 项目 '{name}' 不存在")
            return
        d = project.add_discussion(role, content)
        print(f"✅ 讨论记录已添加")
    
    elif command == "progress":
        if len(sys.argv) < 3:
            print("用法: python project_tool.py progress <项目名>")
            return
        name = sys.argv[2]
        project = get_project(name)
        if not project:
            print(f"❌ 项目 '{name}' 不存在")
            return
        
        total = len(project.milestones)
        completed = sum(1 for m in project.milestones if m["status"] == "completed")
        progress = int(completed / total * 100) if total > 0 else 0
        
        print(f"\n📊 项目进度: {project.name}")
        print("="*40)
        print(f"总里程碑: {total}")
        print(f"已完成: {completed}")
        print(f"进度: {progress}%")
        print("[" + "█" * progress + "░" * (100 - progress) + "]")
    
    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
