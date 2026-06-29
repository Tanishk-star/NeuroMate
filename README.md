# 🧠 NeuroMate — Your AI Daily Decision Companion

> **Kaggle AI Agents Capstone Project**  
> Built with Python · Streamlit · Google Gemini API · Multi-Agent Architecture

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![Gemini API](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 Project Overview

**NeuroMate** is a multi-agent AI personal assistant designed to eliminate decision fatigue from daily life. Instead of being a generic chatbot, NeuroMate uses a pipeline of six specialised AI agents that collaborate to understand your tasks, prioritise them intelligently, schedule your day, monitor your wellbeing, and deliver personalised recommendations — all in one seamless experience.

---

## 🧩 Problem Statement

Modern professionals face **decision fatigue** — the mental exhaustion caused by making too many decisions throughout the day. By the afternoon, even simple choices become overwhelming. This leads to:

- Procrastination and task avoidance
- Poor prioritisation and time wasting
- Burnout from insufficient recovery time
- Lack of self-awareness about productivity patterns

Most existing apps address only one piece of this problem. NeuroMate addresses all of them.

---

## 💡 Solution Overview

NeuroMate acts as your **AI Chief of Staff**. You tell it what's on your plate, and it:

1. **Extracts and structures** your tasks and events from natural language
2. **Prioritises** them using the Eisenhower Matrix (urgent × important)
3. **Schedules** your day with intelligent time blocking
4. **Monitors** your schedule for overload and stress signals
5. **Recommends** personalised actions tailored to your goals
6. **Reflects** your day back to you with empathetic, actionable insights

---

## ✨ Planned Features

| Feature | Status |
|---|---|
| Task & Event Management | ✅ Foundation Complete |
| Multi-Agent Pipeline (6 agents) | ✅ Architecture Complete |
| MCP Tool Layer | ✅ Complete |
| Dashboard & Analytics | ✅ UI Foundation |
| AI Companion Chat | 🚧 Phase 2 — Gemini Integration |
| AI Scheduling | 🚧 Phase 2 |
| Wellness Monitoring | 🚧 Phase 2 |
| Password-Protected Journal | ✅ Foundation Complete |
| Mood Trend Analysis | 🚧 Phase 3 |
| Weekly Insights | 🚧 Phase 3 |
| Notification System | 🚧 Phase 4 |

---

## 🤖 Multi-Agent Architecture

NeuroMate uses a **sequential multi-agent pipeline** where each agent has exactly one responsibility.

```
User Input
    │
    ▼
┌─────────────────┐
│  Intake Agent   │  Parses raw text → structured tasks & events
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Priority Agent  │  Ranks tasks using urgency × importance
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ Scheduler Agent  │  Time-blocks the day, checks calendar conflicts
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Wellness Agent  │  Detects overload, injects break recommendations
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Recommendation Agent │  Generates personalised action suggestions
└────────┬─────────────┘
         │
         ▼
┌──────────────────┐
│ Reflection Agent │  Composes the final user-facing response
└──────────────────┘
         │
         ▼
    Final Response
```

All agents interact with data exclusively through the **MCP Tool Layer** (`mcp_server.py`), never directly with the database.

---

## 📁 Project Structure

```
NeuroMate/
├── app.py                    # 🚀 Main Streamlit entry point
├── config.py                 # ⚙️  Environment configuration
├── mcp_server.py             # 🔧 MCP Tool Layer (agent ↔ data interface)
├── database.py               # 🗄️  Data models & storage layer
├── scheduler.py              # 📅 Schedule generation & optimisation
├── utils.py                  # 🛠️  Shared utilities
│
├── agents/
│   ├── __init__.py
│   ├── intake_agent.py       # 🎯 Input parsing agent
│   ├── priority_agent.py     # 📊 Task ranking agent
│   ├── scheduler_agent.py    # 🗓  Schedule building agent
│   ├── wellness_agent.py     # 🧘 Wellbeing monitoring agent
│   ├── recommendation_agent.py # 💡 Suggestion generation agent
│   └── reflection_agent.py   # 🪞 Final response agent
│
├── pages/
│   ├── Dashboard.py          # 📊 Daily overview
│   ├── Planner.py            # ➕ Task & event management
│   ├── Companion.py          # 💬 AI chat interface
│   ├── Insights.py           # 📈 Analytics & trends
│   ├── Journal.py            # 📓 Password-protected diary
│   └── Settings.py           # ⚙️  User preferences
│
├── assets/                   # 🖼️  Static assets (images, icons)
├── data/                     # 💾 Local JSON data (gitignored)
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/neuromate.git
cd neuromate
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:
```env
GEMINI_API_KEY=your_gemini_api_key_here
JOURNAL_PASSWORD_HASH=your_sha256_password_hash
```

Generate a journal password hash:
```bash
python -c "import hashlib; print(hashlib.sha256(b'yourpassword').hexdigest())"
```

---

## ▶️ Running the Project

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push your project to a **public GitHub repository**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set your **Secrets** in the Streamlit dashboard (equivalent to `.env`):
   ```toml
   GEMINI_API_KEY = "your_key"
   JOURNAL_PASSWORD_HASH = "your_hash"
   ```
4. Click **Deploy**.

> ⚠️ Never commit your `.env` file. It is excluded by `.gitignore`.

---

## 🔮 Future Improvements

- **Phase 2**: Full Google Gemini integration across all agents
- **Phase 3**: Mood trend analysis, weekly reflection summaries
- **Phase 4**: Email/push notification system
- **Phase 5**: Calendar integrations (Google Calendar, Outlook)
- **Phase 6**: Voice input support
- **Phase 7**: Team/shared workspace mode

---

## 🛡️ Security

- API keys loaded exclusively from environment variables
- Journal entries password-protected with SHA-256 hashing
- Journal data stored separately from all other application data
- No secrets committed to version control (enforced by `.gitignore`)
- Designed for future AES encryption of journal entries at rest

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for the Kaggle AI Agents Capstone**

</div>
