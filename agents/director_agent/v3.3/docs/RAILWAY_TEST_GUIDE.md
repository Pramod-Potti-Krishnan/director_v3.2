# Railway Deployment Test Guide

## Quick Start

Test your Director v2.0 Railway deployment with WebSocket connection.

### Prerequisites

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure websockets is installed (should already be in requirements.txt)
pip install websockets
```

### Run Test

```bash
# Run the Railway deployment test
python test_railway_deployment.py
```

### Test Modes

#### 1. Automated Test (Recommended for first test)
- Runs complete conversation flow automatically
- Tests all 6 stages: Greeting → Topic → Questions → Answers → Plan → Generation → Refinement
- Shows v2.0 presentation URL responses

#### 2. Interactive Test
- Manual control over conversation
- Type messages and see responses in real-time
- Type 'quit' to exit

### Expected Output

When deck-builder v2.0 integration is working, you should see:

```
🎉 Presentation URL Generated! (v2.0)
══════════════════════════════════════════════════════════
📊 Presentation URL:
https://web-production-f0d13.up.railway.app/p/[uuid]

Details:
  • Presentation ID: [uuid]
  • Number of Slides: [count]
  • Message: Your presentation is ready! View it at: [url]
══════════════════════════════════════════════════════════

💡 Open the URL in your browser to view the presentation!
```

### Configuration

The test connects to: `wss://directorv20-production.up.railway.app/ws`

To test a different URL:
```bash
python test_railway_deployment.py your-custom-url.up.railway.app
```

### What It Tests

✅ WebSocket connection to Railway deployment
✅ Session initialization
✅ All conversation stages (1-6)
✅ State transitions
✅ v2.0 deck-builder URL responses
✅ Refinement workflow
✅ Error handling

### Troubleshooting

**Connection Failed**
- Check Railway deployment is running
- Verify URL: `directorv20-production.up.railway.app`
- Check Railway logs for errors

**Timeout**
- AI response can take 30-60 seconds for generation
- Test has 60-second timeout per message
- Check Railway logs if consistent timeouts

**No URL Response**
- Check DECK_BUILDER_ENABLED=true in Railway environment
- Verify DECK_BUILDER_API_URL is set correctly
- Check deck-builder API is accessible from Railway

**JSON Response Instead of URL**
- Indicates deck-builder integration is disabled or failed
- Check Railway environment variables
- Review Director logs for deck-builder errors

### Next Steps

After successful test:
1. Open the presentation URL in browser
2. Verify slides are correctly formatted
3. Test refinement workflow
4. Check layout selection (should use 8 MVP layouts)

### Railway Environment Check

Ensure these are set in Railway:
```bash
DECK_BUILDER_ENABLED=true
DECK_BUILDER_API_URL=https://web-production-f0d13.up.railway.app
DECK_BUILDER_TIMEOUT=30
```

---

**Ready to test!** Run `python test_railway_deployment.py` and choose your test mode.
