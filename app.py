"""
🚀 RepoGenAi — AI-Powered GitHub Repository Generator
=======================================================
Model  : llama-3.3-70b-versatile (Groq)
Theme  : #0D0D1B / #F88973 warm gradient
Stack  : Streamlit · Groq · Plotly · NetworkX · nbformat
"""

import os, sys, re, ast, json, time, zipfile, tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict

import networkx as nx
import nbformat
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu
from groq import Groq

# ─────────────────────────────────────────────────────────────
#  MODEL
# ─────────────────────────────────────────────────────────────
MODEL = "llama-3.3-70b-versatile"

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RepoGenAi — AI Repo Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS  (glassmorphism / warm dark theme — fully preserved)
# ─────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

  /* ── Base ── */
  html, body, [data-testid="stAppViewContainer"] {
      background: linear-gradient(135deg, #0D0D1B 0%, #1a0e16 50%, #0D0D1B 100%) !important;
      font-family: 'Inter', sans-serif !important;
      color: #ffffff !important;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0D0D1B 0%, #1f0f18 100%) !important;
      border-right: 1px solid #3a2030 !important;
  }

  /* ── Hero Banner ── */
  .hero-banner {
      background: linear-gradient(135deg, #1a0e16 0%, #2d1520 50%, #1a0e16 100%);
      border: 1px solid #F88973;
      border-radius: 20px;
      padding: 2.5rem 3rem;
      margin-bottom: 2rem;
      text-align: center;
      box-shadow: 0 0 60px rgba(248,137,115,0.15);
  }
  .hero-title {
      font-size: 3rem; font-weight: 900; letter-spacing: -1px;
      background: linear-gradient(135deg, #F88973 0%, #ffb8a0 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin: 0; line-height: 1.1;
  }
  .hero-sub {
      font-size: 1.1rem; color: #c0a0a0; margin-top: 0.5rem; font-weight: 300;
  }

  /* ── Cards ── */
  .gc-card {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(248,137,115,0.25);
      border-radius: 16px;
      padding: 1.5rem;
      margin: 1rem 0;
      transition: all 0.3s ease;
  }
  .gc-card:hover {
      border-color: #F88973;
      box-shadow: 0 4px 30px rgba(248,137,115,0.2);
      transform: translateY(-2px);
  }

  /* ── Badge ── */
  .badge {
      display: inline-block;
      padding: 0.2rem 0.7rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      margin: 2px;
  }
  .badge-orange { background:#F88973; color:#0D0D1B; }
  .badge-red    { background:#c0392b; color:#fff; }
  .badge-green  { background:#27ae60; color:#fff; }
  .badge-blue   { background:#2980b9; color:#fff; }

  /* ── Metric Cards ── */
  .metric-row { display:flex; gap:1rem; margin-bottom:1rem; flex-wrap:wrap; }
  .metric-card {
      flex:1; min-width:140px;
      background: linear-gradient(135deg,#1f0f18,#2d1520);
      border:1px solid #3a2030; border-radius:12px;
      padding:1rem; text-align:center;
  }
  .metric-val { font-size:2rem; font-weight:900; color:#F88973; }
  .metric-lbl { font-size:0.8rem; color:#a08090; }

  /* ── Buttons ── */
  .stButton>button {
      background: linear-gradient(135deg, #F88973, #c06050) !important;
      color: white !important;
      border: none !important;
      border-radius: 10px !important;
      font-weight: 600 !important;
      padding: 0.5rem 1.5rem !important;
      transition: all 0.2s ease !important;
  }
  .stButton>button:hover {
      transform: translateY(-1px) !important;
      box-shadow: 0 4px 20px rgba(248,137,115,0.4) !important;
  }

  /* ── Inputs ── */
  .stTextInput>div>div>input,
  .stTextArea>div>div>textarea {
      background: rgba(255,255,255,0.06) !important;
      border: 1px solid #3a2030 !important;
      border-radius: 10px !important;
      color: white !important;
      font-family: 'JetBrains Mono', monospace !important;
  }

  /* ── File Uploader ── */
  [data-testid="stFileUploader"] {
      border: 2px dashed #F88973 !important;
      border-radius: 16px !important;
      background: rgba(248,137,115,0.04) !important;
      padding: 1rem !important;
  }

  /* ── Tab Styling ── */
  .stTabs [data-baseweb="tab-list"] {
      background: rgba(255,255,255,0.03);
      border-radius: 12px;
      padding: 4px;
      gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
      border-radius: 8px;
      color: #a08090 !important;
      font-weight: 600;
  }
  .stTabs [aria-selected="true"] {
      background: linear-gradient(135deg, #F88973, #c06050) !important;
      color: white !important;
  }

  /* ── Expander ── */
  .streamlit-expander {
      border: 1px solid #3a2030 !important;
      border-radius: 12px !important;
      background: rgba(255,255,255,0.03) !important;
  }

  /* ── Progress ── */
  .stProgress > div > div > div { background-color: #F88973 !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width:6px; }
  ::-webkit-scrollbar-track { background:#0D0D1B; }
  ::-webkit-scrollbar-thumb { background:#F88973; border-radius:3px; }

  /* ── Chat bubbles ── */
  .chat-user {
      background: linear-gradient(135deg,#F88973,#c06050);
      color: white; border-radius:16px 16px 4px 16px;
      padding: 0.75rem 1rem; margin: 0.5rem 0; max-width:80%; margin-left:auto;
  }
  .chat-bot {
      background: rgba(255,255,255,0.07);
      border: 1px solid #3a2030;
      border-radius:4px 16px 16px 16px;
      padding: 0.75rem 1rem; margin: 0.5rem 0; max-width:85%;
  }

  /* ── Security score ring ── */
  .score-ring {
      width:100px; height:100px;
      border-radius:50%;
      display:flex; align-items:center; justify-content:center;
      font-size:2rem; font-weight:900;
      margin:auto;
  }
  .score-high   { background:conic-gradient(#27ae60 var(--pct), #1a3a1a var(--pct)); color:#27ae60; }
  .score-medium { background:conic-gradient(#f39c12 var(--pct), #3a2a0a var(--pct)); color:#f39c12; }
  .score-low    { background:conic-gradient(#c0392b var(--pct), #3a0a0a var(--pct)); color:#c0392b; }

  /* ── Sidebar option menu ── */
  .nav-link { border-radius: 10px !important; }
  .nav-link-selected { background: linear-gradient(135deg,#F88973,#c06050) !important; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SECURE GROQ CLIENT  (st.secrets only — never hardcoded)
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_groq_client():
    """Return a cached Groq client loaded from Streamlit secrets."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        return Groq(api_key=api_key)
    except (KeyError, FileNotFoundError):
        return None
    except Exception:
        return None


_groq = get_groq_client()
GROQ_READY = _groq is not None

if not GROQ_READY:
    st.error(
        "⚠️ **GROQ_API_KEY is not configured.** RepoGenAi's AI features require a "
        "valid key.\n\nAdd it under **Settings → Secrets** in Streamlit Cloud, or "
        "create a local `.streamlit/secrets.toml` file. See the README for instructions."
    )

# ─────────────────────────────────────────────────────────────
#  INLINE MODULE: utils
# ─────────────────────────────────────────────────────────────
def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"# ERROR reading file: {e}"


def extract_imports(source: str) -> list:
    imports = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])
    except Exception:
        for line in source.splitlines():
            m = re.match(r"^(?:import|from)\s+([\w]+)", line.strip())
            if m:
                imports.append(m.group(1))
    return sorted(set(imports))


def extract_notebook(content: bytes) -> str:
    try:
        nb = nbformat.reads(content.decode("utf-8", errors="replace"), as_version=4)
        parts = []
        for i, cell in enumerate(nb.cells):
            cell_type = cell.cell_type.upper()
            source = cell.source
            parts.append(f"# --- CELL {i+1} [{cell_type}] ---\n{source}")
        return "\n\n".join(parts)
    except Exception as e:
        return f"# Notebook parse error: {e}"


FRAMEWORK_KEYWORDS = {
    "ML/AI":        ["sklearn","torch","tensorflow","keras","xgboost","lightgbm","transformers","huggingface"],
    "Web App":      ["flask","fastapi","django","streamlit","gradio","uvicorn"],
    "Data Science": ["pandas","numpy","matplotlib","seaborn","plotly","scipy","statsmodels"],
    "LLM/GenAI":    ["openai","groq","anthropic","langchain","llama","gemini"],
    "DevOps":       ["docker","kubernetes","terraform","ansible","boto3","azure"],
    "CLI Tool":     ["argparse","click","typer","rich","tqdm"],
}


def detect_project_type(imports: list) -> list:
    types_found = []
    imp_set = set(i.lower() for i in imports)
    for ptype, keywords in FRAMEWORK_KEYWORDS.items():
        if any(k in imp_set for k in keywords):
            types_found.append(ptype)
    return types_found if types_found else ["General Python"]


def create_zip(files: dict, zip_name: str = "repo") -> bytes:
    """Create a ZIP archive in memory and return its bytes."""
    buf = io.BytesIO() if "io" in dir() else __import__("io").BytesIO()
    import io as _io
    buf = _io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files.items():
            zf.writestr(fname, content)
    buf.seek(0)
    return buf.read()


STDLIB = {
    "os","sys","re","ast","json","math","time","copy","abc","io",
    "csv","xml","html","http","urllib","email","logging","warnings",
    "typing","dataclasses","functools","itertools","collections",
    "pathlib","shutil","tempfile","zipfile","tarfile","glob",
    "subprocess","threading","multiprocessing","asyncio","socket",
    "datetime","calendar","random","hashlib","hmac","base64",
    "struct","traceback","inspect","gc","weakref","contextlib",
    "unittest","doctest","pdb","profile","timeit","builtins",
    "string","textwrap","difflib","fnmatch","linecache","tokenize",
    "token","keyword","dis","code","codeop","compileall","py_compile",
    "pickle","shelve","sqlite3","configparser","tomllib","platform",
    "signal","ctypes","enum","graphlib","heapq","bisect","queue",
    "array","mmap","select","selectors","ssl","encodings","codecs",
    "unicodedata","locale","gettext","argparse","getopt","optparse",
    "curses","readline","rlcompleter","formatter","pprint",
}


def filter_pip_packages(imports: list) -> list:
    return [i for i in imports if i.lower() not in STDLIB and not i.startswith("_")]

# ─────────────────────────────────────────────────────────────
#  INLINE MODULE: security
# ─────────────────────────────────────────────────────────────
SECRET_PATTERNS: Dict[str, str] = {
    "AWS Access Key":   r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key":   r"(?i)aws.{0,20}['\"]([0-9a-zA-Z/+]{40})['\"]",
    "GitHub Token":     r"ghp_[0-9a-zA-Z]{36}",
    "OpenAI API Key":   r"sk-[a-zA-Z0-9]{32,}",
    "Groq API Key":     r"gsk_[a-zA-Z0-9]{40,}",
    "Google API Key":   r"AIza[0-9A-Za-z\-_]{35}",
    "Slack Token":      r"xox[baprs]-[0-9a-zA-Z\-]+",
    "Generic Password": r"(?i)(password|passwd|pwd)\s*[=:]+\s*['\"]([^'\"]{4,})['\"]",
    "Generic Secret":   r"(?i)(secret|api_key|apikey|token)\s*[=:]+\s*['\"]([^'\"]{4,})['\"]",
    "Database URL":     r"(?i)(postgresql|mysql|mongodb)(://[^\s]+)",
    "Private Key":      r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "ngrok Token":      r"[0-9a-zA-Z]{20,}_[0-9a-zA-Z_]{20,}",
}


class SecurityScanner:
    """Scans source code for hardcoded secrets and computes a security score."""

    def __init__(self, source: str, filename: str = "file"):
        self.source   = source
        self.filename = filename
        self.findings: List[Dict] = []

    def scan(self) -> List[Dict]:
        self.findings = []
        lines = self.source.splitlines()
        for line_no, line in enumerate(lines, 1):
            for secret_type, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, line):
                    self.findings.append({
                        "type":     secret_type,
                        "line":     line_no,
                        "snippet":  line.strip()[:120],
                        "file":     self.filename,
                        "severity": self._severity(secret_type),
                    })
        return self.findings

    def security_score(self) -> int:
        if not self.findings:
            return 100
        penalty = sum(20 if f["severity"] == "HIGH" else 10 for f in self.findings)
        return max(0, 100 - penalty)

    def redact(self) -> str:
        redacted = self.source
        for secret_type, pattern in SECRET_PATTERNS.items():
            placeholder = f'os.environ.get("{secret_type.upper().replace(" ","_")}")'
            redacted = re.sub(pattern, placeholder, redacted)
        return redacted

    def generate_env_example(self) -> str:
        env_vars = set()
        for f in self.findings:
            env_vars.add(f["type"].upper().replace(" ", "_"))
        if not env_vars:
            env_vars = {"API_KEY", "SECRET_KEY", "DATABASE_URL", "DEBUG"}
        lines = ["# .env.example — Auto-generated by RepoGenAi", ""]
        for var in sorted(env_vars):
            lines.append(f"{var}=your_{var.lower()}_here")
        lines += ["", "DEBUG=False", "APP_PORT=8501"]
        return "\n".join(lines)

    @staticmethod
    def _severity(secret_type: str) -> str:
        high = ["AWS Access Key","AWS Secret Key","Private Key","GitHub Token","OpenAI API Key","Groq API Key"]
        return "HIGH" if secret_type in high else "MEDIUM"

# ─────────────────────────────────────────────────────────────
#  INLINE MODULE: diagrams
# ─────────────────────────────────────────────────────────────
def build_dependency_graph(combined_source: str, project_name: str = "Project") -> go.Figure:
    imports = filter_pip_packages(extract_imports(combined_source))
    if not imports:
        imports = ["No external deps found"]

    G = nx.DiGraph()
    G.add_node(project_name, color="#F88973", size=30)
    for imp in imports[:25]:
        G.add_node(imp, color="#a05060", size=18)
        G.add_edge(project_name, imp)

    pos = nx.spring_layout(G, seed=42, k=2.0)
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]

    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_colors = [G.nodes[n].get("color","#6c6c8a") for n in G.nodes()]
    node_sizes  = [G.nodes[n].get("size", 18)  for n in G.nodes()]
    node_labels = list(G.nodes())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1, color="#5c4a5a"), hoverinfo="none"))
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text",
        text=node_labels, textposition="top center",
        marker=dict(size=node_sizes, color=node_colors, line=dict(width=1, color="#F88973")),
        hovertemplate="<b>%{text}</b><extra></extra>"))
    fig.update_layout(
        title=f"📦 Dependency Graph — {project_name}",
        paper_bgcolor="#0D0D1B", plot_bgcolor="#0D0D1B", font_color="#FFFFFF",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500,
    )
    return fig


def build_file_type_chart(filenames: list) -> go.Figure:
    ext_counts: dict = {}
    for f in filenames:
        ext = f.rsplit(".", 1)[-1].lower() if "." in f else "unknown"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    labels = list(ext_counts.keys()); values = list(ext_counts.values())
    colors = ["#F88973","#c06050","#8a3040","#5c1a2a","#3d0d1a"]
    fig = go.Figure(go.Pie(labels=labels, values=values,
        marker=dict(colors=colors[:len(labels)], line=dict(color="#0D0D1B", width=2)),
        hole=0.4, textfont=dict(color="white")))
    fig.update_layout(title="📄 File Types Distribution",
        paper_bgcolor="#0D0D1B", font_color="#FFFFFF", height=380)
    return fig


def build_imports_chart(combined_source: str) -> go.Figure:
    imports = filter_pip_packages(extract_imports(combined_source))[:20]
    if not imports:
        imports = ["none"]
    fig = go.Figure(go.Bar(x=imports, y=[1]*len(imports), marker_color="#F88973",
        text=imports, textposition="outside"))
    fig.update_layout(title="📦 Detected Packages",
        paper_bgcolor="#0D0D1B", plot_bgcolor="#0D0D1B", font_color="#FFFFFF",
        xaxis_tickangle=-45, yaxis=dict(showticklabels=False), height=380)
    return fig

# ─────────────────────────────────────────────────────────────
#  INLINE MODULE: analyzer  (all Groq calls via _groq client)
# ─────────────────────────────────────────────────────────────
def _chat(system: str, user: str, max_tokens: int = 2048) -> str:
    """Core Groq chat wrapper using the cached client."""
    if not GROQ_READY:
        return "⚠️ AI unavailable — GROQ_API_KEY is not configured in Secrets."
    try:
        resp = _groq.chat.completions.create(
            model=MODEL, max_tokens=max_tokens, temperature=0.3,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Groq API error: {e}"


SYS_ENGINEER = (
    "You are an elite senior software architect and Python expert. "
    "You analyse code thoroughly, produce structured Markdown output, "
    "and never hallucinate. Be concise, professional, and detailed."
)

SYS_DEV = (
    "You are an expert open-source developer. "
    "Generate professional, production-ready file content. "
    "Output ONLY the file content, no explanations, no code fences."
)


def generate_project_summary(combined_source: str, filenames: list) -> str:
    prompt = f"""\
Analyse this codebase (files: {', '.join(filenames)}) and produce a structured project summary:

```
{combined_source[:6000]}
```

Return Markdown with sections:
## 📋 Project Overview
## 🎯 Purpose & Goals
## 🛠️ Tech Stack Detected
## 🔄 Data Flow
## ✅ Strengths
## ⚠️ Issues Found
"""
    return _chat(SYS_ENGINEER, prompt, max_tokens=2000)


def generate_architecture_analysis(combined_source: str) -> str:
    prompt = f"""\
Analyse the software architecture of this codebase:

```
{combined_source[:5000]}
```

Return Markdown covering:
## 🏗️ Architecture Pattern
## 📦 Module Breakdown
## 🔗 Dependencies Map
## 🚀 Scalability Assessment
## 📌 Improvement Recommendations
"""
    return _chat(SYS_ENGINEER, prompt, max_tokens=1800)


def suggest_improvements(source: str) -> str:
    prompt = f"""\
Review this Python code and suggest concrete improvements:

```python
{source[:5000]}
```

Return numbered list of specific, actionable improvements covering:
- Code quality
- Performance
- Security
- Best practices
- Testing
"""
    return _chat(SYS_ENGINEER, prompt, max_tokens=1600)


def explain_notebook(notebook_text: str) -> str:
    prompt = f"""\
Explain this Jupyter Notebook cell by cell in plain English:

{notebook_text[:6000]}

Format as Markdown. For each cell give:
- **Purpose**: one sentence
- **What it does**: 2-3 sentences
- **Key concepts**: bullet list
"""
    return _chat(SYS_ENGINEER, prompt, max_tokens=2200)


def chat_with_codebase(history: list, user_message: str, context: str = "") -> str:
    """Multi-turn chat with optional codebase context."""
    system = (
        "You are RepoGenAi, a smart coding assistant. "
        "You have access to the user's uploaded codebase. "
        "Answer questions clearly using Markdown. "
        f'{"Codebase context: " + context[:3000] if context else ""}'
    )
    messages = [{"role": "system", "content": system}]
    for h in history[-8:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})
    if not GROQ_READY:
        return "⚠️ AI unavailable — GROQ_API_KEY is not configured in Secrets."
    try:
        resp = _groq.chat.completions.create(
            model=MODEL, max_tokens=1500, temperature=0.5, messages=messages
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"


def detect_duplicates(source: str) -> str:
    prompt = f"""\
Analyse this Python code for duplicate or redundant code blocks:

```python
{source[:5000]}
```

List:
1. Duplicate functions / logic
2. Refactoring opportunities
3. DRY principle violations
Provide specific line-level feedback.
"""
    return _chat(SYS_ENGINEER, prompt, max_tokens=1200)

# ─────────────────────────────────────────────────────────────
#  INLINE MODULE: generator
# ─────────────────────────────────────────────────────────────
def generate_readme(project_name: str, summary: str, imports: list, project_types: list) -> str:
    prompt = f"""\
Generate a professional GitHub README.md for this project:

Project Name : {project_name}
Project Type : {', '.join(project_types)}
Tech Stack   : {', '.join(imports[:30])}
Summary      : {summary[:1000]}

Include: badges, table of contents, features, installation, usage,
project structure, contributing, license sections.
Use emojis. Make it visually stunning. Output pure Markdown.
"""
    return _chat(SYS_DEV, prompt, max_tokens=2500)


def generate_requirements(imports: list) -> str:
    pip_pkgs = filter_pip_packages(imports)
    VERSION_MAP = {
        "streamlit":">=1.30.0","flask":">=3.0.0","fastapi":">=0.109.0",
        "pandas":">=2.0.0","numpy":">=1.26.0","sklearn":"scikit-learn>=1.4.0",
        "torch":">=2.2.0","tensorflow":">=2.15.0","keras":">=3.0.0",
        "groq":">=0.5.0","openai":">=1.12.0","plotly":">=5.18.0",
        "requests":">=2.31.0","sqlalchemy":">=2.0.0","pydantic":">=2.5.0",
        "langchain":">=0.1.0","transformers":">=4.38.0","gradio":">=4.0.0",
        "matplotlib":">=3.8.0","seaborn":">=0.13.0","scipy":">=1.12.0",
        "xgboost":">=2.0.0","lightgbm":">=4.2.0","networkx":">=3.2.0",
        "pillow":"Pillow>=10.0.0","cv2":"opencv-python>=4.9.0",
        "dotenv":"python-dotenv>=1.0.0","pymongo":">=4.6.0",
    }
    lines = ["# requirements.txt — Auto-generated by RepoGenAi\n"]
    for pkg in pip_pkgs:
        if pkg in VERSION_MAP:
            entry = VERSION_MAP[pkg]
            lines.append(entry if ">=" in entry else f"{pkg}{entry}")
        else:
            lines.append(pkg)
    return "\n".join(sorted(set(lines[1:]), key=str.lower))


def generate_gitignore(project_types: list) -> str:
    base = """\
# RepoGenAi — Auto-generated .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/

# Virtual Environments
venv/
.venv/
env/
.env
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Notebooks
.ipynb_checkpoints/
*.ipynb_checkpoints

# Data & Models
data/raw/
*.csv
*.pkl
*.h5
*.ckpt
*.pt
*.bin

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Secrets
.env
.env.*
secrets.json
config/local.py

# Deployment
*.tfstate
*.tfstate.backup
.terraform/
"""
    if "ML/AI" in project_types:
        base += "\n# ML artifacts\nwandb/\nmlruns/\n*.onnx\n"
    if "Web App" in project_types:
        base += "\n# Web\nnode_modules/\nstatic/\n*.min.js\n"
    return base


def generate_license(author: str = "RepoGenAi User", year: str = "2025") -> str:
    return f"""\
MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def generate_dockerfile(project_types: list, main_file: str = "app.py") -> str:
    port = "8501"
    cmd  = f'CMD ["streamlit", "run", "{main_file}", "--server.port={port}", "--server.address=0.0.0.0"]'
    return f"""\
# Dockerfile — Auto-generated by RepoGenAi
FROM python:3.11-slim

LABEL maintainer="RepoGenAi"
LABEL description="RepoGenAi generated project"

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    build-essential curl \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:{port}/ || exit 1

{cmd}
"""


def generate_setup_py(project_name: str, imports: list) -> str:
    pip_pkgs = filter_pip_packages(imports)
    install_requires = repr(pip_pkgs[:20])
    safe_name = project_name.lower().replace(" ", "-").replace("_", "-")
    return f"""\
# setup.py — Auto-generated by RepoGenAi
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name             = "{safe_name}",
    version          = "1.0.0",
    author           = "RepoGenAi User",
    description      = "Auto-generated by RepoGenAi",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages         = find_packages(),
    python_requires  = ">=3.9",
    install_requires = {install_requires},
    classifiers      = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
"""


def generate_contributing(project_name: str) -> str:
    return f"""\
# Contributing to {project_name}

Thank you for your interest in contributing! 🎉

## 🚀 Getting Started

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📋 Code Standards

- Follow PEP 8 style guide
- Write docstrings for all functions
- Add type hints where possible
- Write unit tests for new features
- Keep commits atomic and descriptive

## 🐛 Bug Reports

Open a GitHub Issue with description, steps to reproduce, expected vs actual behaviour.

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
"""


def generate_security_md(project_name: str) -> str:
    return f"""\
# Security Policy — {project_name}

## 🔒 Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x.x   | ✅        |
| < 1.0   | ❌        |

## 🚨 Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please report via GitHub Security Advisories or email security@yourdomain.com.

## ⏱️ Response Timeline

- Acknowledgement: within 48 hours
- Initial assessment: within 7 days
- Patch release: within 30 days (critical: within 7 days)

## 🛡️ Security Best Practices

- Never hardcode API keys or secrets
- Use environment variables via `.env` file
- Keep dependencies updated
- Enable 2FA on your GitHub account
"""


def generate_project_structure(files: dict) -> str:
    lines = ["# 📁 Project Structure\n", "```"]
    for fname in sorted(files.keys()):
        lines.append(f"├── {fname}")
    lines.append("```")
    lines.append("\n*Auto-generated by RepoGenAi*")
    return "\n".join(lines)


def generate_all_files(project_name: str, combined_source: str,
                       filenames: list, summary: str) -> dict:
    imports       = extract_imports(combined_source)
    project_types = detect_project_type(imports)
    files = {}
    files["README.md"]            = generate_readme(project_name, summary, imports, project_types)
    files["requirements.txt"]     = generate_requirements(imports)
    files[".gitignore"]           = generate_gitignore(project_types)
    files["LICENSE"]              = generate_license()
    files["Dockerfile"]           = generate_dockerfile(project_types)
    files["setup.py"]             = generate_setup_py(project_name, imports)
    files["CONTRIBUTING.md"]      = generate_contributing(project_name)
    files["SECURITY.md"]          = generate_security_md(project_name)
    files["project_structure.md"] = generate_project_structure(files)
    scanner = SecurityScanner(combined_source)
    scanner.scan()
    files[".env.example"] = scanner.generate_env_example()
    return files

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "uploaded_files":    {},
        "combined_source":   "",
        "project_name":      "MyProject",
        "generated_files":   {},
        "active_file":       None,
        "chat_history":      [],
        "analysis_done":     False,
        "summary":           "",
        "arch_analysis":     "",
        "security_findings": [],
        "security_score":    100,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# ─────────────────────────────────────────────────────────────
#  SIDEBAR NAV
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem;'>
      <span style='font-size:2.5rem;'>🚀</span><br>
      <span style='font-size:1.2rem;font-weight:900;background:linear-gradient(135deg,#F88973,#ffb8a0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>RepoGenAi</span><br>
      <span style='font-size:0.75rem;color:#a08090;'>AI Repo Generator</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if GROQ_READY:
        st.success("✅ Groq AI connected")
    else:
        st.error("🔴 Groq offline — add GROQ_API_KEY to Secrets")

    st.divider()

    page = option_menu(
        menu_title=None,
        options=["🏠 Home","📤 Upload","🧠 Analysis","🛡️ Security",
                 "📁 Repo Files","✏️ Editor","📊 Diagrams","💬 Chat","📦 Export"],
        icons=["house","cloud-upload","cpu","shield-check","folder",
               "pencil-square","bar-chart","chat-dots","file-zip"],
        default_index=0,
        styles={
            "container":         {"background":"transparent","padding":"0"},
            "icon":              {"color":"#F88973","font-size":"14px"},
            "nav-link":          {"color":"#c0a0a0","font-size":"14px","padding":"8px 16px"},
            "nav-link-selected": {"background":"linear-gradient(135deg,#F88973,#c06050)","color":"white","font-weight":"700"},
        }
    )

    st.divider()
    if st.session_state.uploaded_files:
        st.markdown('<p style="color:#a08090;font-size:0.75rem;">📂 Loaded Files</p>', unsafe_allow_html=True)
        for fname in st.session_state.uploaded_files:
            st.markdown(f'<div style="color:#F88973;font-size:0.8rem;">• {fname}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  PAGE: HOME
# ─────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
      <p class="hero-title">🚀 RepoGenAi</p>
      <p class="hero-sub">AI-Powered GitHub Repository Generator</p>
      <p style="color:#a08090;font-size:0.9rem;margin-top:0.5rem;">
        Upload your code &rarr; AI analyses it &rarr; Generates a production-ready GitHub repo in seconds
      </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("🤖", "AI Model",       "Llama 3.3 70B"),
        ("📄", "Files Generated","10+"),
        ("🛡️", "Security Scan",  "Built-in"),
        ("⚡", "Speed",          "Groq Fast"),
    ]
    for col, (icon, label, val) in zip([col1,col2,col3,col4], metrics):
        col.markdown(f"""
        <div class="gc-card" style="text-align:center;">
          <div style="font-size:2rem;">{icon}</div>
          <div style="font-size:1.2rem;font-weight:700;color:#F88973;">{val}</div>
          <div style="font-size:0.8rem;color:#a08090;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### ✨ What RepoGenAi Does")
        features = [
            "📤 Upload .py, .ipynb, .txt files",
            "🧠 AI-powered code analysis",
            "📝 Auto-generates README, Dockerfile, LICENSE",
            "🛡️ Security scan & secret detection",
            "📊 Dependency & architecture diagrams",
            "✏️ Live code editor with syntax highlighting",
            "💬 AI Chat assistant for your codebase",
            "📦 One-click ZIP download",
        ]
        for f in features:
            st.markdown(f'<div class="gc-card" style="padding:0.6rem 1rem;margin:0.3rem 0;">{f}</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        <div class="gc-card">
          <ol style="color:#c0a0a0;line-height:2;">
            <li>Click <strong style="color:#F88973">📤 Upload</strong> in the sidebar</li>
            <li>Upload your Python / Notebook files</li>
            <li>Click <strong style="color:#F88973">🧠 Analysis</strong> to run AI analysis</li>
            <li>Visit <strong style="color:#F88973">📁 Repo Files</strong> to see generated files</li>
            <li>Edit files in <strong style="color:#F88973">✏️ Editor</strong></li>
            <li>Download everything from <strong style="color:#F88973">📦 Export</strong></li>
          </ol>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎨 Theme Colors")
        st.markdown("""
        <div style="display:flex;gap:1rem;margin-top:1rem;">
          <div style="width:60px;height:60px;background:#0D0D1B;border-radius:12px;border:1px solid #444;
               display:flex;align-items:center;justify-content:center;color:white;font-size:0.6rem;">#0D0D1B</div>
          <div style="width:60px;height:60px;background:#F88973;border-radius:12px;
               display:flex;align-items:center;justify-content:center;color:#0D0D1B;font-size:0.6rem;font-weight:bold;">#F88973</div>
          <div style="width:60px;height:60px;background:linear-gradient(135deg,#0D0D1B,#F88973);border-radius:12px;
               display:flex;align-items:center;justify-content:center;color:white;font-size:0.6rem;">Gradient</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  PAGE: UPLOAD
# ─────────────────────────────────────────────────────────────
elif page == "📤 Upload":
    st.markdown("## 📤 Upload Your Files")
    st.markdown('<p style="color:#a08090;">Upload .py, .ipynb, or .txt files. Multiple files supported.</p>', unsafe_allow_html=True)

    proj_name = st.text_input("🏷️ Project Name", value=st.session_state.project_name,
                               placeholder="e.g. my-awesome-ml-project")
    st.session_state.project_name = proj_name

    uploaded = st.file_uploader(
        "Drag & drop files here",
        type=["py","ipynb","txt","md","json","yaml","yml"],
        accept_multiple_files=True,
        help="Supported: .py .ipynb .txt .md .json .yaml"
    )

    if uploaded:
        progress = st.progress(0, text="Reading files…")
        for i, f in enumerate(uploaded):
            try:
                raw = f.read()
                if f.name.endswith(".ipynb"):
                    content = extract_notebook(raw)
                else:
                    content = raw.decode("utf-8", errors="replace")
                st.session_state.uploaded_files[f.name] = content
            except Exception as e:
                st.error(f"⚠️ Could not read '{f.name}': {e}")
            progress.progress((i+1)/len(uploaded), text=f"Loaded {f.name}")
        time.sleep(0.3)
        progress.empty()

        st.session_state.combined_source = "\n\n".join(
            [f"# === FILE: {k} ===\n{v}" for k, v in st.session_state.uploaded_files.items()]
        )
        st.success(f"✅ {len(uploaded)} file(s) loaded successfully!")

    if st.session_state.uploaded_files:
        st.markdown("---")
        st.markdown("### 📂 Loaded Files")
        for fname, content in st.session_state.uploaded_files.items():
            with st.expander(f"📄 {fname}  ({len(content):,} chars)"):
                st.code(content[:3000], language="python")
                if len(content) > 3000:
                    st.info(f"Showing first 3,000 of {len(content):,} chars")

        if st.button("🗑️ Clear All Files", type="secondary"):
            st.session_state.uploaded_files = {}
            st.session_state.combined_source = ""
            st.session_state.analysis_done = False
            st.session_state.generated_files = {}
            st.rerun()

# ─────────────────────────────────────────────────────────────
#  PAGE: ANALYSIS
# ─────────────────────────────────────────────────────────────
elif page == "🧠 Analysis":
    st.markdown("## 🧠 AI Code Analysis")

    if not st.session_state.uploaded_files:
        st.warning("⚠️ Please upload files first (📤 Upload tab).")
        st.stop()

    src = st.session_state.combined_source
    imports = extract_imports(src)
    pip_pkgs = filter_pip_packages(imports)
    project_types = detect_project_type(imports)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 Files",        len(st.session_state.uploaded_files))
    col2.metric("📦 Packages",     len(pip_pkgs))
    col3.metric("📝 Lines",        len(src.splitlines()))
    col4.metric("🏷️ Project Types", len(project_types))

    st.markdown("**Detected Project Types:**")
    for pt in project_types:
        st.markdown(f'<span class="badge badge-orange">{pt}</span>', unsafe_allow_html=True)

    st.markdown("**Detected Packages:**")
    for pkg in pip_pkgs[:30]:
        st.markdown(f'<span class="badge badge-blue">{pkg}</span>', unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary","🏗️ Architecture","💡 Improvements","🔍 Duplicates","📓 Notebook"])

    with tab1:
        if st.button("🚀 Generate Project Summary", key="btn_summary"):
            with st.spinner("Analysing with Groq Llama 3.3 70B…"):
                result = generate_project_summary(src, list(st.session_state.uploaded_files.keys()))
                st.session_state.summary = result
                st.session_state.analysis_done = True
        if st.session_state.summary:
            st.markdown(st.session_state.summary)

    with tab2:
        if st.button("🏗️ Analyse Architecture", key="btn_arch"):
            with st.spinner("Building architecture analysis…"):
                result = generate_architecture_analysis(src)
                st.session_state.arch_analysis = result
        if st.session_state.arch_analysis:
            st.markdown(st.session_state.arch_analysis)

    with tab3:
        if st.button("💡 Suggest Improvements", key="btn_improve"):
            with st.spinner("Reviewing code quality…"):
                st.markdown(suggest_improvements(src))

    with tab4:
        if st.button("🔍 Detect Duplicates", key="btn_dup"):
            with st.spinner("Scanning for duplicate code…"):
                st.markdown(detect_duplicates(src))

    with tab5:
        nb_files = [k for k in st.session_state.uploaded_files if k.endswith(".ipynb")]
        if nb_files:
            selected_nb = st.selectbox("Select Notebook", nb_files)
            if st.button("📓 Explain Notebook", key="btn_nb"):
                with st.spinner("Explaining notebook cells…"):
                    st.markdown(explain_notebook(st.session_state.uploaded_files[selected_nb]))
        else:
            st.info("No .ipynb files uploaded.")

# ─────────────────────────────────────────────────────────────
#  PAGE: SECURITY
# ─────────────────────────────────────────────────────────────
elif page == "🛡️ Security":
    st.markdown("## 🛡️ Security Scanner")

    if not st.session_state.uploaded_files:
        st.warning("⚠️ Please upload files first.")
        st.stop()

    src = st.session_state.combined_source
    scanner = SecurityScanner(src, "all_files")

    if st.button("🔍 Run Security Scan", type="primary"):
        with st.spinner("Scanning for secrets and vulnerabilities…"):
            findings = scanner.scan()
            score    = scanner.security_score()
            st.session_state.security_findings = findings
            st.session_state.security_score    = score

    score    = st.session_state.security_score
    findings = st.session_state.security_findings

    col1, col2 = st.columns([1, 3])
    with col1:
        color = "#27ae60" if score >= 80 else "#f39c12" if score >= 50 else "#c0392b"
        badge_cls = "badge-green" if score >= 80 else "badge-red"
        badge_txt = "✅ CLEAN" if score >= 80 else "⚠️ ISSUES FOUND"
        st.markdown(f"""
        <div class="gc-card" style="text-align:center;">
          <div style="font-size:0.9rem;color:#a08090;margin-bottom:0.5rem;">Security Score</div>
          <div style="font-size:4rem;font-weight:900;color:{color};">{score}</div>
          <div style="font-size:0.8rem;color:#a08090;">/100</div>
          <div style="margin-top:0.5rem;">
            <span class="badge {badge_cls}">{badge_txt}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if findings:
            st.markdown(f"**⚠️ {len(findings)} issue(s) detected:**")
            for f in findings:
                sev_badge = "badge-red" if f["severity"]=="HIGH" else "badge-blue"
                st.markdown(f"""
                <div class="gc-card">
                  <span class="badge {sev_badge}">{f['severity']}</span>
                  <strong> {f['type']}</strong> — Line {f['line']} in <code>{f['file']}</code><br>
                  <code style="color:#a08090;font-size:0.8rem;">{f['snippet'][:100]}</code>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No secrets detected in uploaded files!")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔏 Generate Redacted Version"):
            redacted = scanner.redact()
            st.code(redacted[:3000], language="python")
    with col_b:
        if st.button("📄 Generate .env.example"):
            env_ex = scanner.generate_env_example()
            st.code(env_ex, language="bash")
            st.download_button("⬇️ Download .env.example", data=env_ex, file_name=".env.example")

# ─────────────────────────────────────────────────────────────
#  PAGE: REPO FILES
# ─────────────────────────────────────────────────────────────
elif page == "📁 Repo Files":
    st.markdown("## 📁 Generated Repository Files")

    if not st.session_state.uploaded_files:
        st.warning("⚠️ Please upload files first.")
        st.stop()

    if st.button("⚡ Generate All Repo Files", type="primary"):
        with st.spinner("🤖 Generating repository files with AI…"):
            try:
                summary = st.session_state.summary or "A Python project."
                files = generate_all_files(
                    st.session_state.project_name,
                    st.session_state.combined_source,
                    list(st.session_state.uploaded_files.keys()),
                    summary,
                )
                for k, v in st.session_state.uploaded_files.items():
                    files[k] = v
                st.session_state.generated_files = files
                st.success(f"✅ {len(files)} files generated!")
            except Exception as e:
                st.error(f"⚠️ Generation error: {e}")

    if st.session_state.generated_files:
        files = st.session_state.generated_files
        st.markdown(f"**{len(files)} files in repository:**")
        ICONS = {
            "md":"📝","txt":"📄","py":"🐍","ipynb":"📓","json":"📋",
            "yaml":"⚙️","yml":"⚙️","dockerfile":"🐳","gitignore":"🙈",
            "env":"🔐","toml":"⚙️","cfg":"⚙️","sh":"💻","license":"⚖️",
        }
        cols = st.columns(3)
        for idx, (fname, content) in enumerate(files.items()):
            ext  = fname.lower().rsplit(".", 1)[-1] if "." in fname else fname.lower().lstrip(".")
            icon = ICONS.get(ext, "📄")
            col  = cols[idx % 3]
            with col:
                with st.expander(f"{icon} {fname}"):
                    lang = "python" if fname.endswith(".py") else "markdown" if fname.endswith(".md") else "bash"
                    st.code(content[:2000], language=lang)
                    if len(content) > 2000:
                        st.caption(f"+{len(content)-2000:,} more chars")
                    st.download_button(f"⬇️ Download {fname}", data=content,
                                       file_name=fname, key=f"dl_{fname}")

# ─────────────────────────────────────────────────────────────
#  PAGE: EDITOR
# ─────────────────────────────────────────────────────────────
elif page == "✏️ Editor":
    st.markdown("## ✏️ File Editor")

    all_files = {**st.session_state.uploaded_files, **st.session_state.generated_files}
    if not all_files:
        st.warning("⚠️ No files available. Upload or generate files first.")
        st.stop()

    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 📂 File Explorer")
        file_list = list(all_files.keys())
        selected  = st.radio("Select file to edit", file_list, label_visibility="collapsed")
        st.session_state.active_file = selected

        st.markdown("---")
        st.markdown("### ➕ New File")
        new_name = st.text_input("Filename", placeholder="e.g. utils.py")
        if st.button("Create") and new_name:
            st.session_state.generated_files[new_name] = f"# {new_name}\n"
            st.rerun()

        if selected:
            if st.button("🗑️ Delete File", key="del_file"):
                st.session_state.generated_files.pop(selected, None)
                st.session_state.uploaded_files.pop(selected, None)
                st.rerun()

    with col2:
        if selected:
            st.markdown(f"### 📝 Editing: `{selected}`")
            content = all_files.get(selected, "")
            lang    = "python" if selected.endswith(".py") else "markdown"

            try:
                from streamlit_ace import st_ace
                edited = st_ace(value=content, language=lang, theme="monokai",
                                key=f"ace_{selected}", height=500, font_size=14,
                                show_gutter=True, wrap=False, auto_update=True)
            except ImportError:
                edited = st.text_area("Edit content", value=content, height=500, key=f"ta_{selected}")

            col_s, col_r = st.columns(2)
            with col_s:
                if st.button("💾 Save", type="primary"):
                    if selected in st.session_state.generated_files:
                        st.session_state.generated_files[selected] = edited
                    else:
                        st.session_state.uploaded_files[selected] = edited
                    st.success("✅ Saved!")
            with col_r:
                st.download_button("⬇️ Download", data=edited, file_name=selected)

            if selected.endswith(".md"):
                with st.expander("👁️ Markdown Preview"):
                    st.markdown(edited)

# ─────────────────────────────────────────────────────────────
#  PAGE: DIAGRAMS
# ─────────────────────────────────────────────────────────────
elif page == "📊 Diagrams":
    st.markdown("## 📊 Visual Diagrams")

    if not st.session_state.uploaded_files:
        st.warning("⚠️ Please upload files first.")
        st.stop()

    src = st.session_state.combined_source
    tab1, tab2, tab3 = st.tabs(["🔗 Dependency Graph","📄 File Types","📦 Packages"])

    with tab1:
        try:
            st.plotly_chart(build_dependency_graph(src, st.session_state.project_name), use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Dependency graph error: {e}")
    with tab2:
        try:
            st.plotly_chart(build_file_type_chart(list(st.session_state.uploaded_files.keys())), use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ File type chart error: {e}")
    with tab3:
        try:
            st.plotly_chart(build_imports_chart(src), use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Imports chart error: {e}")

    if st.session_state.generated_files:
        st.markdown("---")
        st.markdown("### 📁 Repository Structure")
        files = list(st.session_state.generated_files.keys())
        tree  = f"```\n{st.session_state.project_name}/\n"
        for f in sorted(files):
            tree += f"├── {f}\n"
        tree += "```"
        st.markdown(tree)

# ─────────────────────────────────────────────────────────────
#  PAGE: CHAT
# ─────────────────────────────────────────────────────────────
elif page == "💬 Chat":
    st.markdown("## 💬 AI Chat Assistant")
    st.markdown('<p style="color:#a08090;">Chat with your codebase using Groq Llama 3.3 70B.</p>', unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Prompts")
    quick_prompts = [
        "📋 Explain the project",
        "🏗️ Explain architecture",
        "💡 Suggest improvements",
        "🚀 Suggest optimizations",
        "🛡️ Security analysis",
        "📦 List all dependencies",
    ]
    cols = st.columns(3)
    for i, qp in enumerate(quick_prompts):
        if cols[i % 3].button(qp, key=f"qp_{i}"):
            st.session_state.chat_history.append({"role":"user","content":qp})
            with st.spinner("Thinking…"):
                reply = chat_with_codebase(st.session_state.chat_history, qp,
                                           st.session_state.combined_source)
            st.session_state.chat_history.append({"role":"assistant","content":reply})
            st.rerun()

    st.markdown("---")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask anything about your codebase…")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.spinner("🤖 Thinking…"):
            reply = chat_with_codebase(st.session_state.chat_history, user_input,
                                       st.session_state.combined_source)
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ─────────────────────────────────────────────────────────────
#  PAGE: EXPORT
# ─────────────────────────────────────────────────────────────
elif page == "📦 Export":
    st.markdown("## 📦 Export Repository")

    all_files = {**st.session_state.generated_files, **st.session_state.uploaded_files}
    if not all_files:
        st.warning("⚠️ No files to export. Generate repo files first.")
        st.stop()

    st.markdown(f"""
    <div class="gc-card">
      <div style="font-size:0.9rem;color:#a08090;">Repository ready for export</div>
      <div style="font-size:2rem;font-weight:900;color:#F88973;">{len(all_files)} files</div>
      <div style="font-size:0.85rem;color:#a08090;">{st.session_state.project_name}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Select Files to Export")
    selected_files = {}
    cols = st.columns(3)
    for i, (fname, content) in enumerate(all_files.items()):
        checked = cols[i % 3].checkbox(f"📄 {fname}", value=True, key=f"chk_{fname}")
        if checked:
            selected_files[fname] = content

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📦 ZIP Download")
        if st.button("🔨 Build ZIP Archive", type="primary"):
            with st.spinner("Zipping files…"):
                try:
                    zip_bytes = create_zip(selected_files, st.session_state.project_name)
                    st.download_button(
                        label=f"⬇️ Download {st.session_state.project_name}.zip",
                        data=zip_bytes,
                        file_name=f"{st.session_state.project_name}.zip",
                        mime="application/zip",
                    )
                    st.success(f"✅ ZIP ready: {len(selected_files)} files")
                except Exception as e:
                    st.error(f"⚠️ ZIP error: {e}")

    with col2:
        st.markdown("### 📄 Individual Downloads")
        for fname, content in list(selected_files.items())[:8]:
            st.download_button(label=f"⬇️ {fname}", data=content,
                               file_name=fname, key=f"exp_{fname}")

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#5a4050;font-size:0.8rem;">
  🚀 <strong>RepoGenAi</strong> — AI-Powered GitHub Repository Generator &nbsp;•&nbsp;
  Powered by <strong>Groq Llama 3.3 70B</strong> &nbsp;•&nbsp;
  Theme: #0D0D1B / #F88973
</div>
""", unsafe_allow_html=True)
