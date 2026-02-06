#!/usr/bin/env python3
"""
项目管理系统 - Project Management System
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional

PROJECTS_DIR = Path(__file__).parent / "projects"

class Project:
    """项目类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.status = "active"  # active, completed, paused
        self.milestones = []  # 里程碑列表
        self.discussions = []  # 讨论记录
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "milestones": self.milestones,
            "discussions": self.discussions
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        p = cls(data["name"], data.get("description", ""))
        p.created_at = data.get("created_at", datetime.now().isoformat())
        p.updated_at = data.get("updated_at", datetime.now().isoformat())
        p.status = data.get("status", "active")
        p.milestones = data.get("milestones", [])
        p.discussions = data.get("discussions", [])
        return p
    
    def save(self):
        """保存项目"""
        PROJECTS_DIR.mkdir(exist_ok=True)
        filepath = PROJECTS_DIR / f"{self.name}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        self.updated_at = datetime.now().isoformat()
    
    def delete(self):
        """删除项目"""
        filepath = PROJECTS_DIR / f"{self.name}.json"
        if filepath.exists():
            filepath.unlink()
    
    def add_milestone(self, title: str, description: str = "", status: str = "pending"):
        """添加里程碑"""
        milestone = {
            "id": len(self.milestones) + 1,
            "title": title,
            "description": description,
            "status": status,
            "created_at": datetime.now().isoformat()
        }
        self.milestones.append(milestone)
        self.save()
        return milestone
    
    def add_discussion(self, role: str, content: str):
        """添加讨论记录"""
        discussion = {
            "id": len(self.discussions) + 1,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.discussions.append(discussion)
        self.save()
        return discussion
    
    def update_milestone_status(self, milestone_id: int, status: str):
        """更新里程碑状态"""
        for m in self.milestones:
            if m["id"] == milestone_id:
                m["status"] = status
                m["updated_at"] = datetime.now().isoformat()
                self.save()
                return m
        return None


def list_projects() -> List[dict]:
    """列出所有项目"""
    PROJECTS_DIR.mkdir(exist_ok=True)
    projects = []
    for f in PROJECTS_DIR.glob("*.json"):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            projects.append({
                "name": data["name"],
                "description": data.get("description", "")[:50],
                "status": data.get("status", "active"),
                "milestones_count": len(data.get("milestones", [])),
                "discussions_count": len(data.get("discussions", []))
            })
    return projects


def get_project(name: str) -> Optional[Project]:
    """获取项目"""
    filepath = PROJECTS_DIR / f"{name}.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return Project.from_dict(json.load(f))
    return None


def create_project(name: str, description: str = "") -> Project:
    """创建项目"""
    project = Project(name, description)
    project.save()
    return project


def delete_project(name: str) -> bool:
    """删除项目"""
    project = get_project(name)
    if project:
        project.delete()
        return True
    return False


def search_projects(keyword: str) -> List[dict]:
    """搜索项目"""
    results = []
    for p in list_projects():
        if keyword.lower() in p["name"].lower() or keyword.lower() in p["description"].lower():
            results.append(p)
    return results
