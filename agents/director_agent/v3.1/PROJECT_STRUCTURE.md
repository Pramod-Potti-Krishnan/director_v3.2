# Director Agent v3.1 - Project Structure

**Last Updated**: 2025-01-20

This document provides a quick reference for the organized v3.1 directory structure.

---

## 📂 Directory Structure

```
v3.1/
├── 📄 README.md                    # Main project documentation
├── 📄 main.py                      # Application entry point
├── 📄 checkpoint_manager.py        # Checkpoint management
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment template
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 📁 config/                      # Configuration files
│   └── settings.py                # Application settings
│
├── 📁 src/                         # Source code
│   ├── agents/                    # Agent implementations
│   │   ├── director.py           # Main Director agent (Stage 6 logic here)
│   │   └── intent_router.py      # User intent classification
│   ├── handlers/                  # Request handlers
│   │   └── websocket.py          # WebSocket handler (state transitions)
│   ├── models/                    # Data models
│   │   ├── agents.py             # Core agent models
│   │   ├── content.py            # v3.1: Content generation models
│   │   └── websocket_messages.py # WebSocket message models
│   ├── storage/                   # Data persistence
│   │   └── supabase.py           # Supabase integration
│   ├── utils/                     # Utility modules
│   │   ├── text_service_client.py # v3.1: Text Service client
│   │   ├── content_transformer.py # v3.1: Enhanced with enriched data
│   │   ├── layout_mapper.py      # Layout selection logic
│   │   ├── deck_builder_client.py # Deck-Builder API client
│   │   └── logger.py             # Logging configuration
│   └── workflows/                 # Workflow management
│       └── state_machine.py      # v3.1: Added CONTENT_GENERATION state
│
├── 📁 docs/                        # 📚 All documentation (15 files)
│   ├── V3.1_CHANGELOG.md          # ✨ v3.1 changes and features
│   ├── V3.1_IMPLEMENTATION_PLAN.md # ✨ v3.1 implementation blueprint
│   ├── BUILD_SUMMARY.md           # Build and deployment notes
│   ├── DEPLOYMENT_SUCCESS.md      # Deployment guide
│   ├── FRONTEND_DOCS_SUMMARY.md   # Frontend integration summary
│   ├── RAILWAY_TEST_GUIDE.md      # Railway deployment testing
│   ├── DECK_BUILDER_INTEGRATION.md # Deck-Builder API integration
│   ├── FRONTEND_INTEGRATION.md    # Complete frontend guide
│   ├── FRONTEND_QUICKSTART.md     # Quick start for frontend
│   ├── README.md                  # Documentation index
│   ├── README_v2.0.md             # v2.0 documentation
│   └── [Phase 1 architecture docs] # Original architecture specs
│
└── 📁 tests/                       # 🧪 All test files (9 files)
    ├── test_text_service_integration.py # ✨ v3.1 Stage 6 integration tests
    ├── test_director_standalone.py      # Director unit tests
    ├── test_deck_builder_integration.py # Deck-Builder integration
    ├── test_imports.py                  # Import verification
    ├── test_utils.py                    # Utility test helpers
    ├── test_railway_auto.py             # Railway auto deployment tests
    ├── test_railway_deployment.py       # Railway deployment tests
    ├── test_railway_health.py           # Railway health checks
    ├── test_railway_simple.py           # Simple Railway tests
    └── test_scenarios.json              # Test scenario data
```

---

## 🚀 Running Tests

### From Project Root
```bash
# Run v3.1 integration tests
python3 tests/test_text_service_integration.py

# Run all tests
python3 -m pytest tests/

# Run specific test
python3 tests/test_director_standalone.py
```

### From tests/ Directory
```bash
cd tests
python3 test_text_service_integration.py
```

---

## 📖 Reading Documentation

### v3.1 Specific Docs
- **What changed in v3.1?** → `docs/V3.1_CHANGELOG.md`
- **How was v3.1 built?** → `docs/V3.1_IMPLEMENTATION_PLAN.md`

### Integration Guides
- **Frontend integration** → `docs/FRONTEND_INTEGRATION.md`
- **Deck-Builder API** → `docs/DECK_BUILDER_INTEGRATION.md`
- **Railway deployment** → `docs/RAILWAY_TEST_GUIDE.md`

### Architecture
- **Overall architecture** → `docs/Overall_Architecture_Phase_1.md`
- **WebSocket protocol** → `docs/WebSocket_Communication_Protocol_Phase_1.md`
- **Director agent design** → `docs/Director_IN_Architecture.md`

---

## 🔑 Key Files for v3.1

### New in v3.1
1. **src/utils/text_service_client.py** - Text Service integration
2. **src/models/content.py** - Content generation models
3. **tests/test_text_service_integration.py** - v3.1 tests
4. **docs/V3.1_CHANGELOG.md** - Change documentation
5. **docs/V3.1_IMPLEMENTATION_PLAN.md** - Implementation guide

### Modified for v3.1
1. **src/agents/director.py** - Added Stage 6 (CONTENT_GENERATION) logic
2. **src/utils/content_transformer.py** - Enhanced to inject real text
3. **src/workflows/state_machine.py** - Added CONTENT_GENERATION state
4. **src/handlers/websocket.py** - Updated state transitions
5. **config/settings.py** - Added TEXT_SERVICE_* settings

---

## 📊 File Organization Summary

| Category | Location | Count | Description |
|----------|----------|-------|-------------|
| **Documentation** | `docs/` | 15 | All .md files except README.md |
| **Tests** | `tests/` | 9 | All test_*.py files + test data |
| **Source Code** | `src/` | ~20 | Core application modules |
| **Configuration** | Root + config/ | 5 | Settings and env files |

---

## 🎯 Quick Navigation

Need to...
- **Understand v3.1 changes?** → `docs/V3.1_CHANGELOG.md`
- **Run integration tests?** → `python3 tests/test_text_service_integration.py`
- **Configure Text Service?** → `.env.example` (TEXT_SERVICE_* vars)
- **See Stage 6 logic?** → `src/agents/director.py:CONTENT_GENERATION`
- **Deploy to Railway?** → `docs/RAILWAY_TEST_GUIDE.md`
- **Integrate frontend?** → `docs/FRONTEND_INTEGRATION.md`

---

**Status**: ✅ Organized and ready for development
