# 🚀 RepoGenAi

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **AI-Powered GitHub Repository Generator** — Upload your Python or Notebook code, and RepoGenAi uses Groq's Llama 3.3 70B to instantly generate a production-ready GitHub repository complete with README, Dockerfile, security scan, dependency diagrams, and more.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 **File Upload** | Upload `.py`, `.ipynb`, `.txt`, `.md`, `.json`, `.yaml` files |
| 🧠 **AI Analysis** | Project summary, architecture breakdown, improvement suggestions |
| 🛡️ **Security Scanner** | Detects hardcoded secrets, API keys, and credentials |
| 📁 **Repo Generator** | Auto-generates README, Dockerfile, `.gitignore`, LICENSE, `setup.py` |
| ✏️ **Live Editor** | Monaco-powered code editor with syntax highlighting |
| 📊 **Diagrams** | Interactive dependency graph, file type distribution, package chart |
| 💬 **AI Chat** | Multi-turn chat assistant with full codebase context |
| 📦 **ZIP Export** | One-click download of all generated files as a ZIP archive |

---

## 🏗️ Project Structure

```
RepoGenAi/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Production dependencies
├── README.md               # This file
└── modules/
    ├── __init__.py
    ├── utils.py            # Shared helpers (import extraction, ZIP, etc.)
    ├── security.py         # Secret detection & redaction engine
    ├── analyzer.py         # Groq LLM analysis functions
    ├── generator.py        # Repo file generation engine
    └── diagrams.py         # Plotly/NetworkX visualizations
```

---

## 🚀 Deployment on Streamlit Cloud

### Step 1 — Fork & Push to GitHub

Push this entire project folder to a **public or private GitHub repository**.

### Step 2 — Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repo and set **Main file path** to `app.py`
4. Click **"Deploy"**

### Step 3 — Add Your GROQ_API_KEY Secret ⚠️

This is **required** — the app will not start without it.

1. In your deployed app's dashboard, click **"⋮" → Settings**
2. Open the **"Secrets"** tab
3. Paste the following (replace with your real key):

```toml
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
```

4. Click **"Save"** — the app will automatically restart.

> **Get a free Groq API key at:** [console.groq.com](https://console.groq.com)

---

## 💻 Local Development

### Prerequisites
- Python 3.10+
- A Groq API key from [console.groq.com](https://console.groq.com)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/RepoGenAi.git
cd RepoGenAi

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your local secrets file
mkdir -p .streamlit
echo 'GROQ_API_KEY = "gsk_your_key_here"' > .streamlit/secrets.toml

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🔐 Security

- **Never commit `.streamlit/secrets.toml`** to Git — it is already covered by `.gitignore`.
- All API keys are loaded exclusively via `st.secrets["GROQ_API_KEY"]` — no hardcoding anywhere.
- The built-in Security Scanner will detect and flag any accidentally hardcoded secrets in files you upload.

---

## 🧠 AI Model

RepoGenAi uses **Groq's `llama-3.3-70b-versatile`** model for all AI features:

- Ultra-fast inference via Groq's LPU hardware
- 70B parameter model for high-quality code understanding
- Supports multi-turn conversation with full codebase context

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  Built with ❤️ using <strong>Streamlit</strong> + <strong>Groq</strong>
</div>
