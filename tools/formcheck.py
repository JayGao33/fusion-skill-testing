#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
formcheck.py — skill 形式层检查（通用版，fusion-skill-testing 步骤 1 使用）
用法: python tools/formcheck.py [skill_dir] [--limit 文件:行数,...] [--help]
输出: 检查项逐项 [OK]/[WARN]/[FAIL]；exit 0 = 全部通过，1 = 存在失败
依赖: Python 3
说明: 仅检查确定性/机械性项目（跨 skill 通用）；语义层与行为层按 SKILL.md 流程人工执行。
      目标 skill 若有自己的 formcheck，优先用目标 skill 的，本脚本仅作兜底。
      每条 FAIL 附「→ 修复提示」，帮助不熟悉脚本的用户定位问题；无法读取的文件按
      WARN 跳过而非崩溃；未预期异常以友好信息兜底。

检查项:
  ①  frontmatter: SKILL.md 必须有 name/description；其他 .md 不应有 frontmatter（防多入口）
  ②  文件链接目标存在性（同目录相对路径）
  ③  锚点有效性（# 后的 slug 能在目标文件标题中找到）
  ④  孤儿文件: reference/ 下 .md 未被 SKILL.md 引用（无入口可达）
  ⑤  行数红线（可选配置，默认不限制；用 --limit 传入 "文件:行数" 逗号分隔）
  ⑦  安全初检（默认启用）：扫描全部 .md/.py 的敏感凭据模式（FAIL）与高危操作命令（WARN）——
      算法化替代人工 grep 的安全红线初筛，最终判定由人工复核（SKILL.md 步骤 1.8）
"""
import os
import re
import sys

USAGE = """用法:
  python tools/formcheck.py [skill_dir] [--limit 文件:行数,...] [--help]

  skill_dir  目标 skill 包目录（内含 SKILL.md）；缺省为当前目录
  --limit    行数红线，如 --limit "SKILL.md:200,reference/x.md:100"
  --help / -h  显示本帮助

示例:
  python tools/formcheck.py ~/.workbuddy/skills/my-skill
  python tools/formcheck.py . --limit "SKILL.md:200"

退出码: 0 = 全部通过（可含 WARN）；1 = 存在 FAIL"""

if "--help" in sys.argv or "-h" in sys.argv:
    print(USAGE)
    sys.exit(0)

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
LIMITS = {}  # 文件相对路径 -> 行数上限（--limit "a.md:200,b.md:100"）

for i, a in enumerate(sys.argv):
    if a == "--limit" and i + 1 < len(sys.argv):
        for pair in sys.argv[i + 1].split(","):
            if ":" in pair:
                f, n = pair.rsplit(":", 1)
                LIMITS[f.strip()] = int(n)

if not os.path.isdir(ROOT):
    print(f"错误：目录不存在：{sys.argv[1]}")
    print("提示：skill_dir 应指向包含 SKILL.md 的 skill 包目录。")
    print(USAGE)
    sys.exit(1)

os.chdir(ROOT)

if len(sys.argv) == 1 and not os.path.isfile(os.path.join(ROOT, "SKILL.md")):
    print("提示：未指定 skill_dir，且当前目录不是 skill 包（找不到 SKILL.md）。")
    print(USAGE)
    sys.exit(1)

FAIL = 0
WARN_COUNT = 0

def ok(msg):   print(f"  [OK] {msg}")
def warn(msg):
    global WARN_COUNT
    print(f"  [WARN] {msg}")
    WARN_COUNT += 1
def fail(msg, hint=None):
    global FAIL
    print(f"  [FAIL] {msg}")
    if hint:
        print(f"         → 修复提示：{hint}")
    FAIL = 1

ALL_MD = []
for dirpath, _, files in os.walk("."):
    for f in sorted(files):
        if f.endswith(".md"):
            rel = os.path.relpath(os.path.join(dirpath, f), ".").replace("\\", "/")
            ALL_MD.append(rel)
ALL_MD.sort()

def read(f):
    try:
        with open(f, encoding="utf-8") as fh:
            return fh.read()
    except (FileNotFoundError, PermissionError) as e:
        warn(f"无法读取 {f}（{e.__class__.__name__}），跳过该文件")
        return ""
    except UnicodeDecodeError:
        warn(f"{f} 不是有效 UTF-8 文本，跳过（如含二进制内容请改名）")
        return ""

print(f"=== 形式层检查（通用）· {os.path.basename(ROOT)} ===")

# ------------------------------------------------------------
# ① frontmatter 检查
# ------------------------------------------------------------
print("--- ① frontmatter ---")
if "SKILL.md" not in ALL_MD:
    fail("SKILL.md 不存在（这不是一个 skill 包？）",
         hint="在目录根放 SKILL.md，或以 skill 包目录为参数运行本脚本")
else:
    txt = read("SKILL.md")
    fm = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not fm:
        fail("SKILL.md 缺少 frontmatter（必须以 --- 开头）",
             hint="文件开头加 --- 包裹的 frontmatter 块，内含 name / description")
    else:
        body = fm.group(1)
        for key in ("name", "description"):
            if re.search(rf"^{key}\s*:", body, re.M):
                ok(f"frontmatter.{key} 存在")
            else:
                fail(f"frontmatter.{key} 缺失（模型无法自动触发该 skill）",
                     hint=f"在 frontmatter 块内补 {key}: <值>，这是模型识别与触发该 skill 的依据")
        if not body.strip().startswith("name:"):
            warn("frontmatter 首字段不是 name（惯例：name 在最前）")

for f in ALL_MD:
    if f == "SKILL.md":
        continue
    if read(f).lstrip().startswith("---"):
        fail(f"{f} 带 frontmatter——只有 SKILL.md 应带 frontmatter（其余文件是参考材料）",
             hint="删除该文件开头的 --- 块，或将其并入 SKILL.md（多入口会令模型混淆）")

# ------------------------------------------------------------
# ② 文件链接目标存在性
# ------------------------------------------------------------
print("--- ② 文件链接目标 ---")
broken = 0
for f in ALL_MD:
    for lno, line in enumerate(read(f).splitlines(), 1):
        for target in re.findall(r"\]\(([^)#]+\.md)", line):
            if target.startswith("http"):
                continue
            tgt = os.path.normpath(os.path.join(os.path.dirname(f), target))
            if not os.path.isfile(tgt):
                fail(f"{f}:{lno} 链接目标不存在: {target}",
                     hint="检查相对路径与文件名大小写（Windows 大小写不敏感，但跨平台会踩坑）；文件应在同一目录或按相对路径可达")
                broken = 1
if not broken:
    ok("所有文件链接目标存在")

# ------------------------------------------------------------
# ③ 锚点有效性
# ------------------------------------------------------------
print("--- ③ 锚点 ---")
def slugify(s):
    for ch in [' ', '　', '：', ':', '（', '）', '(', ')', '·', '、', '，', ',', '「', '」', '"', "'"]:
        s = s.replace(ch, '')
    return s

headings = {}
for f in ALL_MD:
    slugs = set()
    for line in read(f).splitlines():
        m = re.match(r'^#{1,6}\s+(.+)$', line)
        if m:
            slugs.add(slugify(m.group(1)))
    headings[f] = slugs

anchor_broken = 0
for f in ALL_MD:
    for lno, line in enumerate(read(f).splitlines(), 1):
        for m in re.finditer(r"\]\(([^)#]+\.md)#([^)\s]+)", line):
            target, anchor = m.group(1), m.group(2)
            tgt = os.path.normpath(os.path.join(os.path.dirname(f), target)).replace("\\", "/")
            if tgt in headings:
                a = slugify(anchor)
                # 精确匹配优先；失败用前缀匹配（兼容「路径矩阵（…）」这类带括号后缀标题）。
                # 已知折中：若存在两个标题同前缀（如「步骤1」与「步骤10」），前缀匹配会放过其中一处的错链；
                # 实际触发需标题刻意同名前缀，风险低，接受此折中以换中文标题兼容性。
                if a not in headings[tgt] and not any(s.startswith(a) for s in headings[tgt]):
                    fail(f"{f}:{lno} 锚点不存在: {target}#{anchor}",
                         hint="修正 # 后的锚点使其对应目标文件的实际标题（中英文标点都会影响匹配）")
                    anchor_broken = 1
if not anchor_broken:
    ok("所有锚点有效")

# ------------------------------------------------------------
# ④ 孤儿文件
# ------------------------------------------------------------
print("--- ④ 孤儿文件 ---")
if "SKILL.md" in ALL_MD:
    skill_txt = read("SKILL.md")
    orphan = 0
    for f in ALL_MD:
        if f == "SKILL.md" or f.startswith("tools/"):
            continue
        # CLAUDE.md（给模型的维护约定）与 README*（给人看的说明，含多语言版如 README_EN.md）是标准伴生元文档，不需被 SKILL.md 引用
        if f == "CLAUDE.md" or f.startswith("README"):
            continue
        if f not in skill_txt:
            fail(f"孤儿文件：{f} 未被 SKILL.md 引用（无入口可达）",
                 hint="在 SKILL.md 加指向该文件的链接，或将其移出 skill 包（无入口的文件不会被模型读到）")
            orphan = 1
    if not orphan:
        ok("所有 .md 文件均有 SKILL 入口")

# ------------------------------------------------------------
# ⑤ 行数红线
# ------------------------------------------------------------
if LIMITS:
    print("--- ⑤ 行数红线 ---")
    for f, limit in LIMITS.items():
        if not os.path.isfile(f):
            fail(f"{f} 不存在（--limit 配置）",
                 hint="检查 --limit 里的文件名与相对路径（相对当前运行目录）")
            continue
        n = len(read(f).splitlines())
        if n > limit:
            fail(f"{f} {n} 行 > 上限 {limit}",
                 hint="精简该文件或把细节下沉到 reference/（行数红线用于控制单文件膨胀）")
        else:
            ok(f"{f} {n} 行 ≤ {limit}")

# ------------------------------------------------------------
# ⑦ 安全初检（默认启用；凭据 FAIL / 高危命令 WARN，人工复核为准）
# ------------------------------------------------------------
print("--- ⑦ 安全初检 ---")
PYFILES = [os.path.relpath(os.path.join(dp, fn), ".").replace("\\", "/")
           for dp, _, fns in os.walk(".") for fn in fns if fn.endswith(".py")]
# 排除本脚本自身（其模式定义字符串不应被自己的规则误报）；被测包的其他脚本照常扫描
SELF = os.path.basename(__file__)
SEC_FILES = ALL_MD + [f for f in PYFILES if os.path.basename(f) != SELF]

# 敏感凭据模式（命中即 FAIL，红线级，需人工复核后定级）
CREDENTIAL_PATTERNS = [
    (r"sk-[A-Za-z0-9]{16,}", "疑似 OpenAI 风格 API key"),
    (r"ghp_[A-Za-z0-9]{20,}", "疑似 GitHub token"),
    (r"AKIA[0-9A-Z]{16}", "疑似 AWS Access Key"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "疑似私钥块"),
    (r"(api[_-]?key|apikey|secret|password|passwd|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]", "疑似硬编码凭据"),
]
# 高危操作命令（命中即 WARN，提示人工复核上下文是否安全护栏完备）
HIGH_RISK_COMMANDS = [
    r"rm\s+-rf",
    r"Remove-Item[^\n]*(Recurse|Force)",
    r"del\s+/[SQ]",
    r"shutil\.rmtree",
    r"os\.remove\s*\(",
    r"os\.unlink\s*\(",
    r"\.git\s+push\s+--force",
    r"git\s+reset\s+--hard",
]

cred_hit = 0
for f in SEC_FILES:
    if not os.path.isfile(f):
        continue
    for lno, line in enumerate(read(f).splitlines(), 1):
        for pat, desc in CREDENTIAL_PATTERNS:
            if re.search(pat, line):
                fail(f"{f}:{lno} 敏感凭据 {desc}",
                     hint="移除硬编码凭据（改环境变量/外部配置），确认无残留后重跑")
                cred_hit = 1
if not cred_hit:
    ok("无敏感凭据模式")

risk_warn = 0
for f in SEC_FILES:
    if not os.path.isfile(f):
        continue
    for lno, line in enumerate(read(f).splitlines(), 1):
        for pat in HIGH_RISK_COMMANDS:
            if re.search(pat, line):
                warn(f"{f}:{lno} 高危操作命令（需人工复核护栏）: {pat}")
                risk_warn = 1
if not risk_warn:
    ok("无高危操作命令")

print()
if FAIL == 0:
    tail = f"（含 {WARN_COUNT} 个 WARN）" if WARN_COUNT else ""
    print(f"==> 形式层全部通过{tail}")
    sys.exit(0)
else:
    print("==> 存在失败项（见上，每条已附修复提示），exit 1")
    sys.exit(1)
