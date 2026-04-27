"""
Skill Management System for ai-dev-team.
Based on anthropics/skills repository structure.

Skills are stored in the `skills/` directory.
Each skill is a directory containing a SKILL.md file.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Optional

SKILLS_DIR = Path(__file__).parent / "skills"


def list_skills() -> list[dict]:
    """List all available skills with metadata from YAML frontmatter."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    
    for item in sorted(SKILLS_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                metadata = parse_skill_metadata(skill_md)
                skills.append({
                    "name": metadata.get("name", item.name),
                    "description": metadata.get("description", ""),
                    "path": str(item.relative_to(SKILLS_DIR.parent)),
                    "dir": item.name,
                    "trigger": extract_trigger(metadata.get("description", "")),
                })
    return skills


def parse_skill_metadata(skill_md: Path) -> dict:
    """Parse YAML frontmatter from SKILL.md."""
    try:
        content = skill_md.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)) or {}
    except Exception:
        pass
    return {}


def extract_trigger(description: str) -> str:
    """Extract a short trigger description from skill description."""
    # Take first sentence or first 100 chars
    first_sentence = description.split(".")[0]
    if len(first_sentence) <= 100:
        return first_sentence
    return description[:100] + "..."


def get_skill(name: str) -> Optional[dict]:
    """
    Get a skill by directory name or by 'superpowers/xxx' format.
    Supports both:
      - get_skill("webapp-testing")       → directory name
      - get_skill("superpowers/tdd")       → superpowers/skill-name format
    """
    # Handle superpowers/xxx format
    if name.startswith("superpowers/"):
        skill_short_name = name[len("superpowers/"):]
        # Map to directory name: superpowers/tdd → superpowers-test-driven-development
        dir_name = f"superpowers-{skill_short_name}"
        skill_dir = SKILLS_DIR / dir_name
    else:
        skill_dir = SKILLS_DIR / name

    if not skill_dir.exists():
        return None

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    content = skill_md.read_text(encoding="utf-8")

    return {
        "name": name,
        "content": content,
        "path": str(skill_dir.relative_to(SKILLS_DIR.parent)),
        "dir": skill_dir,
        "metadata": parse_skill_metadata(skill_md),
    }


def get_skill_scripts(skill_name: str) -> dict[str, str]:
    """Get all scripts in a skill's scripts/ directory."""
    skill = get_skill(skill_name)
    if not skill:
        return {}
    
    scripts = {}
    scripts_dir = skill["dir"] / "scripts"
    if scripts_dir.exists():
        for f in scripts_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                scripts[f.name] = f.read_text(encoding="utf-8")
    return scripts


def get_skill_references(skill_name: str) -> dict[str, str]:
    """Get all reference files in a skill's references/ directory."""
    skill = get_skill(skill_name)
    if not skill:
        return {}
    
    refs = {}
    refs_dir = skill["dir"] / "references"
    if refs_dir.exists():
        for f in refs_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                refs[f.name] = f.read_text(encoding="utf-8")
    return refs


def get_skill_examples(skill_name: str) -> dict[str, str]:
    """Get all example files in a skill's examples/ directory."""
    skill = get_skill(skill_name)
    if not skill:
        return {}
    
    examples = {}
    examples_dir = skill["dir"] / "examples"
    if examples_dir.exists():
        for f in examples_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                examples[f.name] = f.read_text(encoding="utf-8")
    return examples


def load_skill_content_for_agent(skill_name: str, max_length: int = 8000) -> str:
    """
    Load the main SKILL.md content for an agent.
    Truncates if necessary to fit within max_length.
    """
    skill = get_skill(skill_name)
    if not skill:
        return ""
    
    content = skill["content"]
    if len(content) > max_length:
        # Truncate but keep the frontmatter and first part
        return content[:max_length] + f"\n\n[... 内容已截断，原文件: {skill['path']}/SKILL.md]"
    return content


def get_skills_for_task(task_description: str) -> list[str]:
    """
    Heuristically match skills to a task description.
    Returns list of skill directory names relevant to the task.
    """
    task_lower = task_description.lower()
    skill_map = {
        # anthropics/skills
        "webapp-testing": ["web", "test", "browser", "playwright", "frontend", "ui", "自动化测试"],
        "docx": ["word", "docx", "文档", "报告", "letter", "memo"],
        "xlsx": ["excel", "xlsx", "spreadsheet", "表格", "财务", "数据"],
        "pdf": ["pdf", "表单", "form"],
        "pptx": ["ppt", "powerpoint", "演示", "slides"],
        "frontend-design": ["design", "ui", "ux", "样式", "前端"],
        "mcp-builder": ["mcp", "server", "api", "tool"],
        "skill-creator": ["skill", "agent", "create"],
        "web-artifacts-builder": ["react", "artifact", "component", "shadcn"],
        "algorithmic-art": ["art", "generative", "visual"],
        # superpowers skills (prefixed with superpowers/)
        "superpowers/test-driven-development": ["tdd", "test first", "red green", "测试驱动"],
        "superpowers/systematic-debugging": ["debug", "bug", "fix", "错误", "调试", "排查"],
        "superpowers/verification-before-completion": ["verify", "test", "complete", "验证", "完成前"],
        "superpowers/subagent-driven-development": ["subagent", "parallel", "delegate", "子代理", "并发"],
        "superpowers/brainstorming": ["brainstorm", "design", "discuss", "讨论", "设计"],
        "superpowers/writing-plans": ["plan", "implement", "step", "计划", "实施"],
        "superpowers/dispatching-parallel-agents": ["parallel", "concurrent", "dispatch", "并发", "多任务"],
        "superpowers/receiving-code-review": ["review", "feedback", "code review", "reviewer", "评审"],
        "superpowers/requesting-code-review": ["review", "request review", "评审"],
        "superpowers/writing-skills": ["skill", "write skill", "create skill"],
        "superpowers/finishing-a-development-branch": ["merge", "pr", "branch", "finish", "合并"],
        "superpowers/using-git-worktrees": ["git", "worktree", "branch", "分支"],
        "superpowers/using-superpowers": ["superpowers", "skill system"],
    }

    matched = []
    for skill_name, keywords in skill_map.items():
        if any(kw in task_lower for kw in keywords):
            matched.append(skill_name)
    return matched


def build_skill_context(task_description: str) -> str:
    """Build skill context string for an agent based on task description."""
    matched_skills = get_skills_for_task(task_description)
    if not matched_skills:
        return ""
    
    context_parts = ["\n\n## Relevant Skills Loaded\n"]
    for skill_name in matched_skills:
        content = load_skill_content_for_agent(skill_name)
        if content:
            context_parts.append(f"\n--- Skill: {skill_name} ---\n")
            context_parts.append(content)
    
    return "".join(context_parts)
