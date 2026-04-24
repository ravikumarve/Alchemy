# ALCHEMY PRD - Temporal Content Transmuter

**Version:** 0.1
**Status:** Draft
**Last Updated:** 2026-04-24

---

## Problem Statement

**The Problem:** Valuable long-form content (public domain texts, archives, PDFs) sits unused because:
- It's too time-consuming to manually extract and modernize
- Content creators lack the tools to transform legacy content into modern formats
- The gap between "raw text" and "marketable asset" is too wide

**The Solution:** An autonomous pipeline that mines forgotten content and transmutes it into ready-to-sell digital assets for Gumroad.

---

## Target Users

### Primary Users
1. **Content Creators / YouTubers**
   - Need constant supply of high-quality, factual content
   - Want 60-second scripts with visual cues
   - Don't have time to research and script manually

2. **Digital Product Sellers**
   - Sell content packs on Gumroad
   - Need bulk, high-quality assets
   - Want to monetize public domain content

3. **Educators / Course Creators**
   - Need educational content in modern formats
   - Want to repurpose existing materials
   - Need visual assets for video lessons

### User Workflow (Current)
1. Find public domain content (manual search)
2. Read and extract key points (manual)
3. Write script (manual)
4. Create visual cues (manual)
5. Format for Gumroad (manual)
6. **Time per asset:** 2-4 hours

### User Workflow (With ALCHEMY)
1. Drop PDF/TXT into `raw_ore/` directory
2. Wait 60 seconds
3. Find ready-to-sell asset in `processed_gold/`
4. Upload to Gumroad
5. **Time per asset:** 2 minutes

---

## Success Metrics

### Technical Metrics
- **Pipeline Success Rate:** >95% of files processed successfully
- **Processing Time:** <60 seconds per file
- **Asset Quality:** Scripts pass human review (85%+ approval)
- **Uptime:** >99% for unattended operation

### Business Metrics
- **Gumroad Sales:** $500/month in first 3 months
- **Asset Volume:** 100+ assets generated in first month
- **Customer Satisfaction:** 4.5/5 star rating on Gumroad
- **Time to Revenue:** <30 days from first asset

### User Metrics
- **Adoption Rate:** 10+ active users in first month
- **Retention:** 70% of users generate 10+ assets
- **NPS:** >40 (promoter score)

---

## MVP Features (v0.1)

**Goal:** Prove the concept works end-to-end with one content type.

### Core Features
- [ ] **PDF Ingestion:** Accept PDF files in `raw_ore/` directory
- [ ] **Text Extraction:** Extract text from PDFs using unstructured.io
- [ ] **Archaeologist Agent:** Identify evergreen facts, ignore outdated context
- [ ] **Trend-Jacker Agent:** Restructure into 60-second hook framework
- [ ] **Visionary Agent:** Generate B-roll prompts and visual cues
- [ ] **Asset Packaging:** Output as zip file with script + visual cues
- [ ] **Basic Dashboard:** View processing queue and completed assets

### Content Types (MVP)
- [ ] Public domain historical texts
- [ ] Educational PDFs
- [ ] Archive documents

### Constraints
- CPU-only (no GPU)
- Single file processing (no batch)
- Manual file placement (no web upload)

---

## v1.0 Features

**Goal:** Production-ready system for Gumroad sellers.

### Enhanced Features
- [ ] **Multi-Format Support:** PDF, TXT, HTML, DOCX
- [ ] **Batch Processing:** Process entire directories
- [ ] **Web Upload:** Upload files via dashboard
- [ ] **Content Categories:** Tag assets by topic (history, science, education)
- [ ] **Quality Scoring:** Rate assets by engagement potential
- [ ] **Retry Logic:** Automatic retry on transient failures
- [ ] **Error Recovery:** Partial failure handling with cleanup
- [ ] **Monitoring:** Prometheus + Grafana dashboards
- [ ] **Alerting:** Slack/email on failures

### Content Types (v1.0)
- [ ] Public domain books
- [ ] Academic papers
- [ ] Government reports
- [ ] Wikipedia articles
- [ ] Blog posts

### Automation
- [ ] **Cron Job:** Scheduled processing every 15 minutes
- [ ] **Daemon Mode:** Continuous monitoring of `raw_ore/`
- [ ] **Auto-Backup:** Backup processed assets to cloud storage

---

## Future Roadmap (v2.0+)

### Advanced Features
- [ ] **AI Voiceover:** Generate voice narration scripts
- [ ] **Thumbnail Generation:** AI-generated thumbnails for videos
- [ ] **Multi-Language:** Support non-English content
- [ ] **Custom Templates:** User-defined script formats
- [ ] **Marketplace Integration:** Direct Gumroad API upload
- [ ] **Analytics Dashboard:** Track asset performance on Gumroad

### Content Types (v2.0+)
- [ ] Video transcripts
- [ ] Podcast episodes
- [ ] Social media posts
- [ ] News articles

---

## Business Model

### Revenue Streams

**1. Gumroad Asset Sales**
- Sell content packs (10 scripts + visual cues) for $9.99
- Sell premium packs (50 scripts + voiceover) for $29.99
- Sell subscription (unlimited access) for $19.99/month

**2. SaaS Subscription (Future)**
- Free tier: 5 assets/month
- Pro tier: 50 assets/month for $9.99
- Enterprise tier: Unlimited for $49.99

### Pricing Strategy
- **MVP:** Free (validate product-market fit)
- **v1.0:** Pay-per-asset ($0.99 each)
- **v2.0:** Subscription model

### Competitive Advantage
- **Speed:** 60 seconds vs 2-4 hours manual
- **Quality:** AI-powered hook optimization
- **Automation:** Zero-maintenance operation
- **Cost:** Fraction of hiring content writers

---

## Edge Cases & Failure Modes

### Input Failures
- **Corrupted PDFs:** Log error, move to `failed/` directory, alert user
- **Empty Files:** Skip with warning
- **Unsupported Formats:** Reject with clear error message
- **Password-Protected Files:** Reject with error message

### Processing Failures
- **Extraction Timeout:** Retry 3x with exponential backoff, then fail
- **Agent Failure:** Fallback to simpler processing, log degradation
- **Memory Issues:** Process in chunks, monitor memory usage
- **Network Issues:** Queue for retry, process when connection restored

### Output Failures
- **Asset Too Long:** Truncate to 60-second limit, log warning
- **Asset Too Short:** Flag for manual review
- **Low Quality Score:** Flag for manual review
- **Duplicate Content:** Detect and skip

### System Failures
- **Disk Full:** Alert user, pause processing
- **Database Corruption:** Restore from backup, alert user
- **Service Crash:** Auto-restart via systemd, log crash
- **Cron Job Failure:** Alert via Slack, manual intervention

---

## Acceptance Criteria

### MVP (v0.1)
- [ ] Can process a PDF and output a zip file with script + visual cues
- [ ] Script is approximately 60 seconds when read aloud
- [ ] Visual cues are actionable (can be used for B-roll)
- [ ] Dashboard shows processing status
- [ ] System runs unattended for 24 hours without manual intervention

### v1.0
- [ ] Can process 100+ files in batch without errors
- [ ] 95%+ of assets pass human quality review
- [ ] System uptime >99% over 30 days
- [ ] Processing time <60 seconds per file
- [ ] Monitoring and alerting are functional
- [ ] Can recover from failures without data loss

---

## Open Questions

1. **Content Sources:** Where do we get initial public domain content for testing?
2. **Quality Threshold:** What's the minimum quality score for auto-approval?
3. **Pricing:** What's the optimal price point for Gumroad assets?
4. **Legal:** Are there any copyright concerns with public domain content?
5. **Scalability:** How many concurrent files can the CPU handle?

---

## Next Steps

1. **Week 1:** Implement Archaeologist agent (text extraction)
2. **Week 2:** Implement Trend-Jacker agent (hook optimization)
3. **Week 3:** Implement Visionary agent (visual cues)
4. **Week 4:** Build basic dashboard and testing
5. **Week 5:** Generate 100 test assets and validate quality
6. **Week 6:** Launch on Gumroad and iterate based on feedback

---

**Status:** Ready for implementation
**Owner:** Solo Developer
**Review Date:** 2026-05-01
