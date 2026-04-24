# 🌐 ALCHEMY - Temporal Content Transmuter

Autonomous multi-agent pipeline converting legacy content (PDFs, archives, public domain texts) into modern digital assets for Gumroad deployment.

## 🎯 Project Overview

ALCHEMY is a production-ready content transmutation system that extracts evergreen data from legacy documents while intelligently filtering outdated context. The system uses a coordinated multi-agent architecture to process content through a 7-step workflow, preparing it for modern content distribution platforms.

### Key Features

- **🤖 Multi-Agent Architecture**: 3 specialized agents (Archaeologist, Trend-Jacker, Visionary) working in coordination
- **⏱️ 60-Second Engine**: Perfectly timed content processing for short-form video content
- **🔄 Zero-Maintenance**: Runs as cron job or background daemon for unattended operation
- **📦 Ready-to-Ship**: Outputs prepped for direct Gumroad deployment
- **💻 CPU-Only**: Optimized for Dell Latitude 3460 (no GPU required)

## 🏗️ Architecture

### Phase 1: Architecture & Workflow Design ✅
- **Software Architect**: System design and technical decisions
- **Workflow Architect**: Complete workflow mapping with failure modes
- **Automation Governance Architect**: Unattended operation patterns

### Phase 2: Backend & Pipeline Development ✅
- **Backend Architect**: FastAPI, SQLite, Celery, Redis stack
- **AI Engineer**: LangGraph orchestration, unstructured.io integration
- **Data Consolidation Agent**: ETL pipelines and data aggregation

### Phase 3: Frontend & Dashboard Development 🚧
- **Frontend Developer**: Next.js 14+ with App Router
- **UI Designer**: shadcn/ui components
- **UX Architect**: User experience design

### Phase 4: Three-Agent Core Implementation ✅
- **Archaeologist**: Data Miner (SemanticChunker, TableExtractor)
- **Trend-Jacker**: Contextualizer (HookLibrary, AttentionMetrics)
- **Visionary**: Media Architect (PromptGenerator, StoryBoarder)

### Phase 5: Testing & Quality Assurance 🚧
- **API Tester**: Integration tests and edge case coverage
- **Performance Benchmarker**: 60-second timing validation
- **Code Reviewer**: Security audits and best practices

### Phase 6: DevOps & Deployment 🚧
- **DevOps Automator**: CI/CD pipelines and monitoring
- **Backend Architect**: Production deployment
- **Workflow Architect**: Operational workflows

## 📁 Directory Structure

```
alchemy/
├── raw_ore/             # Input: PDFs, TXT, HTML files
├── processed_gold/      # Output: Finalized assets (zip files)
├── src/
│   ├── agents/          # OpenCode agent definitions
│   │   ├── archaeologist.py
│   │   ├── archaeologist_state.py
│   │   ├── trend_jacker.py
│   │   └── visionary.py
│   ├── pipeline/        # Core extraction/transmutation logic
│   │   ├── text_extractor.py
│   │   ├── semantic_chunker.py
│   │   ├── table_extractor.py
│   │   └── data_packager.py
│   ├── api/             # FastAPI backend
│   │   ├── main.py
│   │   └── routes/
│   └── ui/              # shadcn/ui dashboard
│       ├── app/
│       └── components/
├── tests/               # Test suites
├── docs/
│   ├── architecture/    # Architecture specifications
│   └── workflows/       # Workflow specifications
├── requirements.txt     # Python dependencies
├── package.json         # Dashboard dependencies
└── docker-compose.yml   # Local development setup
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/alchemy.git
   cd alchemy
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies** (for dashboard)
   ```bash
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Usage

#### Process a Single File

```python
from src.agents.archaeologist import ArchaeologistAgent

# Initialize agent
agent = ArchaeologistAgent()

# Process a file
result = agent.process_file("raw_ore/document.pdf")

if result['success']:
    print(f"✓ Processing completed in {result['processing_time']:.2f}s")
    print(f"  Package ID: {result['package']['package_id']}")
    print(f"  Chunks: {len(result['package']['content'])}")
    print(f"  Tables: {len(result['package']['tables'])}")
else:
    print(f"✗ Processing failed: {result['errors']}")
```

#### Command Line Usage

```bash
# Process a file
python -m src.agents.archaeologist raw_ore/document.pdf

# Run tests
pytest tests/ -v

# Start API server
uvicorn src.api.main:app --reload

# Start dashboard
npm run dev
```

#### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🤖 Agent Workflow

### Archaeologist Agent (Data Miner)

**7-Step Workflow:**

1. **File Validation (5s)** - Verify file format and integrity
2. **Content Extraction (2s)** - Extract raw text using unstructured.io
3. **Semantic Analysis (30s)** - Identify evergreen vs outdated content
4. **Data Structuring (20s)** - Organize into chunks and tables
5. **Quality Filtering (15s)** - Filter low-quality or irrelevant content
6. **Metadata Enrichment (5s)** - Add source, timestamp, confidence scores
7. **Package Generation (3s)** - Create JSON package for Trend-Jacker

**Total Time Budget:** 80 seconds (with safety margin)

### Trend-Jacker Agent (Contextualizer)

**Workflow Steps:**

1. **Hook Generation** - Create attention-grabbing hooks
2. **Context Mapping** - Map evergreen content to modern trends
3. **Narrative Structuring** - Structure content for engagement
4. **Attention Optimization** - Optimize for retention metrics

### Visionary Agent (Media Architect)

**Workflow Steps:**

1. **Visual Analysis** - Analyze content for visual opportunities
2. **B-Roll Generation** - Generate B-roll prompts
3. **Story Boarding** - Create visual storyboards
4. **Asset Packaging** - Package visual assets for production

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_archaeologist.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Integration Tests

```bash
# Test complete workflow
pytest tests/test_integration.py -v

# Test API endpoints
pytest tests/test_api.py -v
```

### Performance Testing

```bash
# Validate 60-second timing constraint
pytest tests/test_performance.py -v

# Load testing
pytest tests/test_load.py -v
```

## 📊 Monitoring

### Prometheus Metrics

The system exposes Prometheus metrics for monitoring:

- `alchemy_processing_time_total` - Total processing time
- `alchemy_step_time_seconds` - Time per processing step
- `alchemy_evergreen_score` - Evergreen content score
- `alchemy_quality_assessment` - Quality assessment rating
- `alchemy_errors_total` - Total error count

### Grafana Dashboards

Pre-configured Grafana dashboards are available for:

- Pipeline health monitoring
- Performance metrics
- Error tracking
- Resource utilization

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./alchemy.db

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000

# Processing
MAX_FILE_SIZE=104857600  # 100MB
TIMEOUT_SECONDS=80
RETRY_COUNT=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/alchemy.log
```

### Agent Configuration

Each agent can be configured via YAML files in `config/agents/`:

```yaml
# config/agents/archaeologist.yaml
time_budgets:
  validate_file: 5
  extract_content: 2
  analyze_semantics: 30
  structure_data: 20
  filter_quality: 15
  enrich_metadata: 5
  generate_package: 3

quality_thresholds:
  min_evergreen_score: 0.5
  min_confidence_score: 0.5
  min_chunk_length: 50
```

## 🚢 Deployment

### Production Deployment

1. **Build Docker images**
   ```bash
   docker-compose build
   ```

2. **Run database migrations**
   ```bash
   docker-compose run api alembic upgrade head
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

### Cron Job Setup

```bash
# Add to crontab for automated processing
*/5 * * * * cd /path/to/alchemy && python -m src.agents.archaeologist /path/to/raw_ore/*.pdf
```

## 📝 API Documentation

### REST API Endpoints

#### Process File
```http
POST /api/v1/process
Content-Type: multipart/form-data

{
  "file": <binary>
}
```

#### Get Job Status
```http
GET /api/v1/jobs/{job_id}
```

#### Get Package
```http
GET /api/v1/packages/{package_id}
```

#### Health Check
```http
GET /health
```

For full API documentation, see `docs/api/README.md`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Python: Follow PEP 8, use Black for formatting
- JavaScript: Follow ESLint rules
- Commits: Follow Conventional Commits specification

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph** - Agent orchestration framework
- **unstructured.io** - Text extraction library
- **FastAPI** - Modern Python web framework
- **shadcn/ui** - Beautiful UI components

## 📞 Support

For support, please open an issue on GitHub or contact [your-email@example.com].

---

**Built with ❤️ for solo indie developers**
