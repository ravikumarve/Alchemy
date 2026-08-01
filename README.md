# 🌐 ALCHEMY — Temporal Content Transmuter

> **Turn ideas and old content into ready-to-sell digital products. Automatically.**

ALCHEMY is an autonomous multi-agent pipeline that transforms legacy content (PDFs, archives, public domain texts) — or any topic idea — into modern, Gumroad-ready digital asset packs. It runs on a laptop, costs nothing to operate, and delivers production-ready outputs in seconds.

---

## 🎯 The Problem It Solves

Creating sellable digital products is slow. You need to:
1. Research content
2. Extract what's still relevant
3. Write attention-grabbing hooks
4. Plan a video storyboard
5. Generate B-roll image prompts
6. Design audio cues
7. Package everything for sale

This takes hours per product. ALCHEMY does it in **~1.5 seconds** — fully autonomously.

---

## 🤖 The Three-Agent Core

```
INPUT ──► Archaeologist ──► Trend-Jacker ──► Visionary ──► OUTPUT
             │                   │                │
         Extracts            Generates        Creates
         evergreen           viral hooks,     storyboard,
         content             narrative,       B-roll prompts,
                             engagement       audio design,
                             optimization     Gumroad listing
```

### Agent 1: Archaeologist
Extracts evergreen data from PDFs, TXT, and HTML files — intelligently filters out outdated content, extracts tables, and structures everything for the next stage.

### Agent 2: Trend-Jacker
Restructures content into modern frameworks: 8 hook types (question, surprise, story, controversy, how-to, mistake, secret, comparison), narrative sections, attention optimization, engagement scoring.

### Agent 3: Visionary
Generates production-ready media assets: scene-by-scene storyboard, AI image/video prompts (Midjourney/DALL-E/Stable Diffusion), audio design spec (mood, BPM, genre per scene), thumbnail prompts, and a complete Gumroad listing with pricing.

---

## 📦 What You Get

Each processed pack includes everything you need to create and sell a short-form video asset:

| Asset | Format | Description |
|-------|--------|-------------|
| **Storyboard** | Timed scene list | What to show, in what order, with transitions |
| **B-Roll Prompts** | Text (copy-paste) | Ready for Midjourney, DALL-E, Stable Diffusion |
| **Audio Design** | Mood + BPM + genre | Per-scene audio direction |
| **Thumbnail Prompts** | Text (copy-paste) | For YouTube/thumbnail generators |
| **Gumroad Listing** | Title + description + hashtags + SEO + pricing | Copy-paste ready |
| **Transition Map** | Visual cue timing | Exactly when each scene changes |

---

## 🏗️ Two Products, One Engine

ALCHEMY is designed as a dual-product system from a single core architecture:

### 🖥️ LOCAL — Personal Content Factory

**What it does:** Drop files into a folder, get sellable asset packs out.

```
raw_ore/file.pdf ──► ALCHEMY pipeline ──► processed_gold/pack.json
                                              └── Ready for Gumroad
```

**Run mode:** Unattended daemon (cron or systemd) — zero maintenance.

**Best for:** Solo creators building their own Gumroad product catalog.

**Cost:** $0 (runs on your machine)

### ☁️ GLOBAL — SaaS Platform (Phase 7 — Planned)

**What it does:** User types an idea → system researches, processes, delivers a downloadable pack.

```
User: "Stoicism for modern life"
         │
         ▼
Researcher Agent (web search + AI synthesis)
         │
         ▼
Trend-Jacker → Visionary (unchanged)
         │
         ▼
Downloadable ZIP with all assets
```

**New agent needed:** **Researcher** — replaces Archaeologist for the SaaS mode. Uses web search (Tavily/Firecrawl) to research any topic, then feeds into the same Trend-Jacker → Visionary pipeline.

**Key insight:** Trend-Jacker and Visionary remain **completely unchanged** — the shared data contract between agents is the architectural moat.

**Estimated launch:** ~1 month build time

---

## ✅ Current Status — Phase 6 Complete

| Component | Status |
|-----------|--------|
| **Archaeologist Agent** | ✅ Complete — 7-step LangGraph workflow |
| **Trend-Jacker Agent** | ✅ Complete — Hooks, narrative, attention optimization |
| **Visionary Agent** | ✅ Complete — Storyboard, B-roll, audio, Gumroad packaging |
| **FastAPI Backend** | ✅ Complete — 8 REST endpoints, SQLite, Prometheus metrics |
| **Next.js Dashboard** | ✅ Complete — shadcn/ui, dark mode, real-time monitoring |
| **Docker Deployment** | ✅ Complete — Multi-stage build, docker-compose |
| **CI/CD Pipeline** | ✅ Complete — GitHub Actions, mypy, lint, coverage |
| **Unattended Daemon** | ✅ Complete — Cron, systemd, oneshot/watch/file modes |
| **Test Suite** | ✅ Complete — 121 tests, mypy clean, all passing |
| **Performance** | ✅ Verified — End-to-end pipeline in ~1.5s (well under 60s budget) |

---

## 🔮 Phase 7 Roadmap — Local → Global

Full upgrade plan: [`docs/architecture/LOCAL-TO-GLOBAL-UPGRADE-PLAN.md`](docs/architecture/LOCAL-TO-GLOBAL-UPGRADE-PLAN.md)

| Phase | Milestone | Timeline |
|-------|-----------|----------|
| **7a** | Researcher Agent (web search + AI synthesis) | Week 1 |
| **7b** | Wire Researcher into orchestrator + API | Week 1 |
| **7c** | Cloud migration (PostgreSQL, auth, rate limits) | Week 1-2 |
| **7d** | SaaS frontend pages (Create from Idea, Library, Pricing) | Week 2 |
| **7e** | ZIP delivery (actual assets, not blueprints) | Week 2-3 |
| **7f** | Billing (Stripe: Free/Creator/Pro tiers) | Week 3 |
| **7g** | Gumroad one-click publish | Week 3-4 |
| | **Total to SaaS** | **~1 month** |

### New Feature: Researcher Agent

The only new agent needed for SaaS mode:

```
Step 1: Parse user topic → generate search queries
Step 2: Web search (Tavily/Firecrawl MCP)
Step 3: AI-synthesize into structured content chunks
Step 4: Quality filter
Step 5: Output package (same schema as Archaeologist)
```

**Output contract matches Archaeologist exactly** — Trend-Jacker and Visionary require zero changes.

### Pricing Model (Planned)

| Tier | Price | Limit |
|------|-------|-------|
| Free | $0 | 2 packs (trial) |
| Creator | $19/mo | 10 packs/month |
| Pro | $49/mo | Unlimited + image generation |

### Estimated Monthly Costs (SaaS Mode)

| Service | Cost |
|---------|------|
| Railway (backend) | $5-20/mo |
| Vercel (frontend) | Free tier |
| Supabase (auth + DB) | Free tier |
| Tavily (web search) | Free up to 1k packs |
| **Total base** | **$5-20/mo** |

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.9+
- Docker (optional)

### Install
```bash
pip install -r requirements.txt
```

### Process a File
```python
from src.pipeline.orchestrator import AlchemyOrchestrator

orc = AlchemyOrchestrator()
result = orc.process_file("raw_ore/sample_art_of_war.txt")
print(f"Done in {result['total_time']:.2f}s — output: {result['output_path']}")
```

### Or Run the Daemon
```bash
# One-shot (for cron)
python scripts/process-daemon.py --oneshot

# Continuous watch mode
python scripts/process-daemon.py --watch

# Process specific file
python scripts/process-daemon.py --file raw_ore/document.txt
```

### Or Use the API
```bash
# Start server
uvicorn src.api.main:app --reload

# Upload file
curl -X POST http://localhost:8000/api/v1/process \
  -F "file=@raw_ore/document.txt"

# Check status
curl http://localhost:8000/api/v1/jobs/{job_id}
```

### Docker
```bash
docker-compose up -d
```

---

## 🧪 Test Suite

```bash
pytest tests/ -v
# 121 passed in 4.27s
```

---

## 📁 Project Structure

```
alchemy/
├── raw_ore/                  # Input files (PDF, TXT, HTML)
├── processed_gold/           # Output packs (Visionary JSON)
├── src/
│   ├── agents/               # Three AI agents
│   │   ├── archaeologist.py  # Data miner
│   │   ├── trend_jacker.py   # Contextualizer
│   │   └── visionary.py      # Media architect
│   ├── pipeline/             # 11 pipeline modules
│   ├── api/                  # FastAPI backend
│   └── ui/                   # Next.js dashboard
├── scripts/
│   ├── process-daemon.py     # Unattended daemon
│   └── install-service.sh    # Cron/systemd installer
├── tests/                    # 121 tests
├── Dockerfile                # Multi-stage build
├── docker-compose.yml
└── requirements.txt
```

---

## 📊 Infrastructure

| Layer | Tech | Status |
|-------|------|--------|
| **Orchestration** | LangGraph (with fallback) | ✅ |
| **API** | FastAPI + uvicorn | ✅ |
| **Database** | SQLite (SQLAlchemy) | ✅ |
| **Monitoring** | Prometheus `/metrics` | ✅ |
| **Logging** | Structured JSON | ✅ |
| **Container** | Docker multi-stage | ✅ |
| **Deployment** | docker-compose | ✅ |
| **CI/CD** | GitHub Actions (test + lint + coverage) | ✅ |
| **Service** | Cron or systemd | ✅ |
| **Frontend** | Next.js 14 App Router + shadcn/ui | ✅ (build on Vercel) |

---

## 🧠 Architecture Highlights

- **Shared data contract**: All three agents communicate via a standardized JSON schema. This is why Trend-Jacker and Visionary need zero changes for the SaaS mode.
- **LangGraph with fallback**: Every agent can run with or without LangGraph — no hard dependency.
- **Lightweight extraction**: Uses PyPDF2 + BeautifulSoup instead of heavyweight `unstructured` — brought extraction from 6.5s down to ~0.1s.
- **Idempotent daemon**: ProcessingTracker uses MD5 hashes to never re-process the same file.

---

## 🔗 Links

- [Full Upgrade Plan: Local → Global](docs/architecture/LOCAL-TO-GLOBAL-UPGRADE-PLAN.md)
- [Backend Architecture](docs/architecture/BACKEND-ARCHITECTURE.md)
- [API Documentation](docs/api/README.md)
- [Workflow Specs](docs/workflows/)

---

## 📄 License

MIT — free to use, modify, and sell outputs from.

---

*Built with ❤️ for solo indie creators who want to ship digital products without the grind.*
