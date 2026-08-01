# ALCHEMY — Local to Global: Upgrade Plan

> **From personal content factory → SaaS platform**
> Planned: June 2026 | Target: Phase 7

---

## 🎯 Strategic Vision

```
LOCAL (Current)                    GLOBAL (Target)
──────────────────────────────────────────────────────
  Personal use                      Multi-tenant SaaS
  CPU-only Latitude                 Cloud-hosted (Vercel + Railway)
  File drops only                   Topic ideas + File uploads
  Manual Gumroad upload             Auto-publish via API
  3 Agents                          4 Agents (added Researcher)
  Local SQLite                      Cloud PostgreSQL
  JSON blueprints                   Zip downloads with assets
  Free                              $19/mo or $4.99/pack
```

---

## 📋 Phase Breakdown

### Phase 7a: Foundation — Researcher Agent (Week 1)

**Goal:** Add web research capability so users can create packs from IDEAS, not just files.

**New Module:**
```
src/agents/researcher.py     # 5-step Researcher Agent
src/pipeline/web_researcher.py  # Web search + synthesis
tests/test_researcher.py     # Test suite
```

**Researcher Agent Workflow:**
```
1. Parse user idea → generate 5 search queries
2. Web search via Tavily MCP / Firecrawl
3. Extract full text from top 3-5 results
4. AI-synthesize into structured content chunks
5. Output: Archaeologist-compatible data pack
```

**Key Constraint:** Output format must EXACTLY match `ArchaeologistState` package schema so Trend-Jacker and Visionary require ZERO changes.

**New API Endpoint:**
```
POST /api/v1/explore
Body: { "topic": "Stoicism for modern life", "asset_type": "youtube_short" }
Response: { "job_id": "...", "status": "processing" }
```

**Acceptance:** `POST /api/v1/explore` returns a valid package within 60s.

---

### Phase 7b: Researcher Integration (Day 4-5)

**Goal:** Wire Researcher into existing orchestrator and API.

**Changes:**
- `src/pipeline/orchestrator.py` — Add `process_topic(topic: str)` method
- `src/api/main.py` — Add `/api/v1/explore` endpoint with background task
- Both file-upload AND topic-explore routes converge into same Trend-Jacker → Visionary pipeline

**Orchestrator becomes:**
```
Orchestrator
├── process_file(path)     → Archaeologist → Trend-Jacker → Visionary
└── process_topic(topic)   → Researcher   → Trend-Jacker → Visionary
                              (new)          (unchanged)    (unchanged)
```

---

### Phase 7c: Backend Cloud Migration (Week 1-2)

**Goal:** Production-ready backend for multi-tenant SaaS.

| Change | What | Why |
|--------|------|-----|
| SQLite → PostgreSQL | Swap connection string | Concurrency, scale, Vercel compat |
| Auth layer | JWT + Supabase/NextAuth | Multi-tenant isolation |
| Rate limiting | Slow down abusive requests | Fair use |
| File upload limits | 10MB max per upload | Cost control |
| User <-> Job FK | Add `user_id` to tables | Per-user data isolation |

**Estimated cloud costs:**
- Railway (backend): $5-20/mo
- Vercel (frontend): Free tier (Hobby)
- Supabase (auth + DB): Free tier
- Tavily/Firecrawl (web search): ~$0.01-0.05 per search → ~$5-15/mo at 1k packs

---

### Phase 7d: Frontend SaaS Pages (Week 2)

**Goal:** New user-facing pages for the SaaS product.

**New Pages (to add in `src/ui/app/`):**

| Page | Route | Purpose |
|---|---|---|
| **Create from Idea** | `/create` | Topic input → triggers Researcher Agent |
| **Pack Detail / Download** | `/downloads/[packId]` | View and download finished pack |
| **My Library** | `/library` | History of all generated packs |
| **Pricing** | `/pricing` | Subscription plans |
| **Account / Settings** | `/account` | Auth, API keys, billing |
| **Landing Page** | `/landing` | Marketing page for non-users |

**Reuse existing:** Dashboard (`/`) remains as-is for admin monitoring.

**Deployment:** Vercel (free tier — Hobby plan handles this easily)

---

### Phase 7e: Asset Delivery — From Blueprint to Zip (Week 2-3)

**Goal:** Deliver actual assets, not just instructions.

**New Endpoint:**
```
GET /api/v1/download/{pack_id}
Response: ZIP file containing:
├── broll_prompts.txt
├── thumbnail_prompts.txt
├── storyboard.json + storyboard_summary.txt
├── audio_spec.txt
├── gumroad_listing.txt
└── preview_thumbnail.png (if we generate it)
```

**Image generation (optional — adds cloud cost):**
- API: Replicate / Stability AI / Fal.ai
- Cost: ~$0.01-0.05 per image
- Per pack: 5-10 images = ~$0.10-0.25
- Only do this for paid users (subscription tier)

---

### Phase 7f: Billing & Monetization (Week 3)

**Goal:** Users pay, we earn.

**Tiers:**

| Tier | Price | Limit |
|---|---|---|
| Free | $0 | 2 packs (trial) |
| Creator | $19/mo | 10 packs/month |
| Pro | $49/mo | Unlimited + image generation included |

**Pay-per-pack:** $4.99 (no subscription, one-off)

**Payment provider:** Stripe (global) + Razorpay (India)

**Implementation:** Stripe Checkout sessions → webhooks to unlock pack downloads

---

### Phase 7g: Gumroad Direct Publishing (Week 3-4)

**Goal:** One-click publish to Gumroad from inside the app.

**Feature:** "Publish to Gumroad" button
- User connects their Gumroad API key
- We auto-create the listing (title, description, price, file)
- User just clicks "publish"

**API:** Gumroad API (token-based, create product → upload file)

---

## 🧩 New Architecture Diagram (Target)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        ALCHEMY SAAS (GLOBAL)                              │
│                                                                           │
│  ┌─────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │  User   │──►│  RESEARCHER  │──►│ TREND-JACKER │──►│   VISIONARY   │   │
│  │  Topic  │   │  (New Agent) │   │  (Existing)  │   │  (Existing)   │   │
│  └─────────┘   └──────────────┘   └──────────────┘   └──────┬───────┘   │
│                                                              │           │
│  ┌─────────┐   ┌──────────────┐                               │           │
│  │  User   │──►│ ARCHAEOLOGIST│  (same pipeline)               │           │
│  │  File   │   │  (Existing)  │──────────────────────────────┘           │
│  └─────────┘   └──────────────┘                                         │
│                                                                          │
│                          ┌──────────────────┐                            │
│                          │   ZIP PACKAGER   │                            │
│                          │  (New Feature)   │                            │
│                          └────────┬─────────┘                            │
│                                   ▼                                      │
│                    ┌──────────────────────────┐                          │
│                    │  Download / Gumroad Push │                          │
│                    └──────────────────────────┘                          │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Frontend: Vercel (Next.js)                                      │   │
│  │  ├── Dashboard (existing)                                        │   │
│  │  ├── Create from Idea (new)                                      │   │
│  │  ├── My Library (new)                                            │   │
│  │  ├── Pricing + Auth (new)                                        │   │
│  │  └── Landing Page (new)                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Backend: Railway (FastAPI)                                       │   │
│  │  ├── PostgreSQL (instead of SQLite)                               │   │
│  │  ├── Supabase (auth)                                              │   │
│  │  ├── Stripe (billing)                                             │   │
│  │  └── Web Search API (Tavily/Firecrawl)                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ Migration Path — Safe Steps

### Step 1: No Breaking Changes
- Add Researcher Agent alongside Archaeologist (don't remove anything)
- New endpoint only (`/api/v1/explore`)
- Existing local daemon continues working

### Step 2: Optional Cloud DB
- PostgreSQL becomes available but SQLite remains default
- `DATABASE_URL` env var switches between them

### Step 3: Frontend on Vercel
- Existing dashboard deploys unchanged
- New pages added incrementally

### Step 4: Add Billing Last
- Only after product-market fit is validated with beta users

---

## 🛠️ New Agent: Researcher — Detailed Spec

This is the ONLY new agent needed. Everything else is reused.

```
Agent: Researcher
Input: User topic string (e.g., "Stoicism for modern entrepreneurs")
Output: Standardized package with same schema as Archaeologist

Workflow:
  Step 1 — Query Generation (1s)
     Generate 3-5 search queries from the user topic
     Examples:
     - "Stoicism entrepreneurship habits"
     - "Marcus Aurelius modern business lessons"
     - "Stoic philosophy productivity tips"

  Step 2 — Web Search (5-15s)
     Run queries via Tavily MCP / Firecrawl
     Collect top 3-5 full-text results

  Step 3 — Content Synthesis (5-10s)
     AI-extract key concepts, principles, quotes
     Structure into content_chunks format
     Calculate evergreen_score based on content type

  Step 4 — Quality Filter (3s)
     Remove low-quality or irrelevant chunks
     Assign confidence scores

  Step 5 — Package Generation (2s)
     Output package matching ArchaeologistState schema
     Trend-Jacker accepts it without changes

Time Budget: ~30-60s (dominated by web search latency)
```

---

## 📊 New Features & Functions — Complete List

### User-Facing Features (Global SaaS)

| Feature | Description | Priority |
|---|---|---|
| **Create from Idea** | User types a topic → system researches + generates pack | P0 |
| **Create from File** | Already exists (file upload) — keep as-is | P0 |
| **Download ZIP** | Download generated pack as a ready-to-use bundle | P0 |
| **Pack Preview** | View pack contents in browser before download | P1 |
| **User Library** | History of all generated packs | P1 |
| **Pricing Page** | Free / Creator / Pro tiers | P1 |
| **Stripe Payments** | Subscription + one-time purchase | P1 |
| **Gumroad Push** | One-click publish to Gumroad | P2 |
| **Image Generation** | Auto-generate B-roll images + thumbnails | P2 |
| **Multiple Languages** | Generate packs in any language | P2 |
| **API Access** | API key for programmatic pack generation | P2 |

### Backend Upgrades

| Feature | Description | Priority |
|---|---|---|
| **Researcher Agent** | Web search + AI synthesis agent | P0 |
| **PostgreSQL Support** | Switchable via env var | P1 |
| **User Auth** | JWT + email/password or Google OAuth | P1 |
| **Rate Limiting** | Per-user API limits | P1 |
| **Usage Tracking** | Track packs/month per user | P1 |
| **Analytics** | Dashboard for admin (popular topics, conversion) | P2 |

### Frontend Pages (New)

| Page | Route | Priority |
|---|---|---|
| Create from Idea | `/create` | P0 |
| Pack Download | `/downloads/[id]` | P0 |
| Landing Page | `/` (redesign) | P1 |
| Pricing | `/pricing` | P1 |
| Login/Signup | `/auth/login`, `/auth/signup` | P1 |
| User Library | `/library` | P1 |
| Account Settings | `/account` | P2 |
| Admin Dashboard | `/admin` | P2 |

---

## 💰 Cost Estimates (Monthly)

| Service | Free Tier | Paid Tier Needed | Est. Cost |
|---|---|---|---|
| **Vercel** (Frontend) | 100GB bandwidth, 6000 build min | Hobby = $0 | $0 |
| **Railway** (Backend) | $5 credit | Starter = $5/mo | $5-20/mo |
| **Supabase** (Auth + DB) | 500MB DB, 50K users | Free = $0 | $0 |
| **Tavily** (Web search) | 1000 searches/mo | Free = $0 | $0 (up to 1000 packs) |
| **Stripe** (Payments) | 2.9% + $0.30 per tx | Standard | Variable |
| **Replicate** (Image gen) | — | Pay-per-use | $0.10-0.25/pack if enabled |

**Total base cost:** $5-20/month — viable from day 1 with just a few paying users.

---

## ⏱️ Timeline Summary

```
Week 1:  Researcher Agent + API endpoint     (Phase 7a + 7b)
Week 2:  Cloud backend + SaaS frontend pages  (Phase 7c + 7d)
Week 3:  Asset ZIP delivery + Billing         (Phase 7e + 7f)
Week 4:  Gumroad integration + Polish         (Phase 7g)
```

**Total: ~1 month to go from local factory → global SaaS.**
