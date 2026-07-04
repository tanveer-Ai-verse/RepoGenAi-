"""
RepoGenAi — Main Streamlit Application
AI-Powered GitHub Repository Generator
Model   : llama-3.3-70b-versatile (Groq)
Theme   : #0D0D1B / #F88973 warm gradient
"""

import os, sys, json, time
from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

from modules.utils     import safe_read, extract_imports, extract_notebook, detect_project_type, filter_pip_packages, create_zip, timestamp
from modules.security  import SecurityScanner
from modules.analyzer  import generate_project_summary, generate_architecture_analysis, suggest_improvements, explain_notebook, chat_with_codebase, detect_duplicates
from modules.generator import generate_all_files, generate_readme, generate_requirements
from modules.diagrams  import build_dependency_graph, build_file_type_chart, build_imports_chart

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "RepoGenAi — AI Repo Generator",
    page_icon  = "🚀",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ─────────────────────────────────────────────────────────────
#  GROQ API KEY — from Streamlit Secrets (production-safe)
# ─────────────────────────────────────────────────────────────
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "⚠️ **GROQ_API_KEY** not found in Streamlit Secrets.\n\n"
        "Go to **Settings → Secrets** in your Streamlit Cloud dashboard and add:\n"
        "```toml\nGROQ_API_KEY = \"your_groq_api_key_here\"\n```"
    )
    st.stop()

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS
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
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "uploaded_files"    : {},
        "combined_source"   : "",
        "project_name"      : "MyProject",
        "generated_files"   : {},
        "active_file"       : None,
        "chat_history"      : [],
        "analysis_done"     : False,
        "summary"           : "",
        "arch_analysis"     : "",
        "security_findings" : [],
        "security_score"    : 100,
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
      <span style='font-size:0.75rem;color:#a08090;'>AI Repository Generator</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = option_menu(
        menu_title = None,
        options    = ["🏠 Home", "📤 Upload", "🧠 Analysis", "🛡️ Security", "📁 Repo Files", "✏️ Editor", "📊 Diagrams", "💬 Chat", "📦 Export"],
        icons      = ["house", "cloud-upload", "cpu", "shield-check", "folder", "pencil-square", "bar-chart", "chat-dots", "file-zip"],
        default_index = 0,
        styles = {
            "container"        : {"background": "transparent", "padding": "0"},
            "icon"             : {"color": "#F88973", "font-size": "14px"},
            "nav-link"         : {"color": "#c0a0a0", "font-size": "14px", "padding": "8px 16px"},
            "nav-link-selected": {"background": "linear-gradient(135deg,#F88973,#c06050)", "color": "white", "font-weight": "700"},
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
      <p class="hero-sub">AI-Powered GitHub Repository Generator &nbsp;•&nbsp; Powered by <strong>Groq Llama 3.3 70B</strong></p>
      <p style="color:#a08090;font-size:0.9rem;margin-top:0.5rem;">
        Upload your code &rarr; AI analyses it &rarr; Generates a production-ready GitHub repo in seconds
      </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("🤖", "AI Model", "Llama 3.3 70B"),
        ("📄", "Files Generated", "10+"),
        ("🛡️", "Security Scan", "Built-in"),
        ("⚡", "Speed", "Groq Fast"),
    ]
    for col, (icon, label, val) in zip([col1, col2, col3, col4], metrics):
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
        type     = ["py", "ipynb", "txt", "md", "json", "yaml", "yml"],
        accept_multiple_files = True,
        help     = "Supported: .py .ipynb .txt .md .json .yaml"
    )

    if uploaded:
        progress = st.progress(0, text="Reading files…")
        for i, f in enumerate(uploaded):
            raw = f.read()
            if f.name.endswith(".ipynb"):
                content = extract_notebook(raw)
            else:
                content = raw.decode("utf-8", errors="replace")
            st.session_state.uploaded_files[f.name] = content
            progress.progress((i + 1) / len(uploaded), text=f"Loaded {f.name}")
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
    col1.metric("📄 Files", len(st.session_state.uploaded_files))
    col2.metric("📦 Packages", len(pip_pkgs))
    col3.metric("📝 Lines", len(src.splitlines()))
    col4.metric("🏷️ Project Types", len(project_types))

    st.markdown("**Detected Project Types:**")
    for pt in project_types:
        st.markdown(f'<span class="badge badge-orange">{pt}</span>', unsafe_allow_html=True)

    st.markdown("**Detected Packages:**")
    for pkg in pip_pkgs[:30]:
        st.markdown(f'<span class="badge badge-blue">{pkg}</span>', unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary", "🏗️ Architecture", "💡 Improvements", "🔍 Duplicates", "📓 Notebook"])

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
                sev_badge = "badge-red" if f["severity"] == "HIGH" else "badge-blue"
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

    if st.session_state.generated_files:
        files = st.session_state.generated_files
        st.markdown(f"**{len(files)} files in repository:**")

        ICONS = {
            "md": "📝", "txt": "📄", "py": "🐍", "ipynb": "📓", "json": "📋",
            "yaml": "⚙️", "yml": "⚙️", "dockerfile": "🐳", "gitignore": "🙈",
            "env": "🔐", "toml": "⚙️", "cfg": "⚙️", "sh": "💻", "license": "⚖️",
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
                    st.download_button(
                        f"⬇️ Download {fname}",
                        data      = content,
                        file_name = fname,
                        key       = f"dl_{fname}",
                    )

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

        selected = st.radio(
            "Select file to edit",
            file_list,
            label_visibility="collapsed"
        )
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
            lang    = "python" if selected.endswith(".py") or selected.endswith(".ipynb") else "markdown"

            try:
                from streamlit_ace import st_ace
                edited = st_ace(
                    value       = content,
                    language    = lang,
                    theme       = "monokai",
                    key         = f"ace_{selected}",
                    height      = 500,
                    font_size   = 14,
                    show_gutter = True,
                    wrap        = False,
                    auto_update = True,
                )
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

    tab1, tab2, tab3 = st.tabs(["🔗 Dependency Graph", "📄 File Types", "📦 Packages"])

    with tab1:
        fig = build_dependency_graph(src, st.session_state.project_name)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig2 = build_file_type_chart(list(st.session_state.uploaded_files.keys()))
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        fig3 = build_imports_chart(src)
        st.plotly_chart(fig3, use_container_width=True)

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
            st.session_state.chat_history.append({"role": "user", "content": qp})
            with st.spinner("Thinking…"):
                reply = chat_with_codebase(
                    st.session_state.chat_history,
                    qp,
                    st.session_state.combined_source
                )
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    st.markdown("---")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask anything about your codebase…")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("🤖 Thinking…"):
            reply = chat_with_codebase(
                st.session_state.chat_history,
                user_input,
                st.session_state.combined_source
            )
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
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
                import io, zipfile as zf_lib
                buf = io.BytesIO()
                with zf_lib.ZipFile(buf, "w", zf_lib.ZIP_DEFLATED) as zf:
                    for fname, content in selected_files.items():
                        zf.writestr(fname, content)
                buf.seek(0)
            st.download_button(
                label     = f"⬇️ Download {st.session_state.project_name}.zip",
                data      = buf.read(),
                file_name = f"{st.session_state.project_name}.zip",
                mime      = "application/zip",
            )
            st.success(f"✅ ZIP ready: {len(selected_files)} files")

    with col2:
        st.markdown("### 📄 Individual Downloads")
        for fname, content in list(selected_files.items())[:8]:
            st.download_button(
                label     = f"⬇️ {fname}",
                data      = content,
                file_name = fname,
                key       = f"exp_{fname}",
            )

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#5a4050;font-size:0.8rem;">
  🚀 <strong>RepoGenAi</strong> &nbsp;•&nbsp;
  Powered by <strong>Groq Llama 3.3 70B</strong> &nbsp;•&nbsp;
  Theme: #0D0D1B / #F88973
</div>
""", unsafe_allow_html=True)
