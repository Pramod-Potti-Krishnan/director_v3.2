# AI Model Configuration Guide

**Director Agent v3.3** - Granular Model Configuration (Gemini-Only)

---

## Overview

As of v3.3, the Director Agent provides **granular per-stage model configuration** via environment variables. Each of the 5 presentation stages plus the intent router can use a different Gemini model, allowing you to:

- **Optimize costs** by using cheaper models for simple tasks
- **Maximize quality** by using advanced models for complex generation
- **Experiment freely** by testing different models per stage
- **Fine-tune performance** for your specific use case

---

## Model Configuration Philosophy

### 6-Model Granular Approach

The Director Agent uses **6 independent models**:

| Model Variable | Stage | Task Complexity | Recommended Model |
|---------------|-------|-----------------|-------------------|
| `GCP_MODEL_GREETING` | Stage 1: Greeting | Simple, short | `gemini-1.5-flash` |
| `GCP_MODEL_QUESTIONS` | Stage 2: Questions | Structured JSON | `gemini-1.5-flash` |
| `GCP_MODEL_PLAN` | Stage 3: Plan | Structured JSON | `gemini-1.5-flash` |
| `GCP_MODEL_STRAWMAN` | Stage 4: Strawman | Complex, detailed | `gemini-2.0-flash-exp` |
| `GCP_MODEL_REFINE` | Stage 5: Refinement | Complex, iterative | `gemini-2.0-flash-exp` |
| `GCP_MODEL_ROUTER` | Intent Routing | Fast, high-volume | `gemini-1.5-flash` |

### Why Per-Stage Models?

**Cost Optimization Example:**
- Stages 1-3 use `gemini-1.5-flash` (cheap, fast): ~$0.075 per 1M tokens
- Stages 4-5 use `gemini-2.0-flash-exp` (advanced): ~$0.30 per 1M tokens
- **Result**: Save ~60% compared to using `gemini-2.0-flash-exp` everywhere

**Performance Tuning:**
- Use faster models for stages with tight latency requirements
- Use advanced models for stages requiring deep reasoning
- Test experimental models on specific stages without affecting others

---

## Environment Variables

### GCP/Vertex AI Models (Gemini Only)

```bash
# Stage 1: Greeting generation (simple, short response)
GCP_MODEL_GREETING=gemini-1.5-flash

# Stage 2: Clarifying questions (structured JSON output)
GCP_MODEL_QUESTIONS=gemini-1.5-flash

# Stage 3: Confirmation plan (structured JSON output)
GCP_MODEL_PLAN=gemini-1.5-flash

# Stage 4: Strawman generation (complex, detailed presentation outline)
GCP_MODEL_STRAWMAN=gemini-2.0-flash-exp

# Stage 5: Strawman refinement (complex, detailed modifications)
GCP_MODEL_REFINE=gemini-2.0-flash-exp

# Intent classification router (fast, high-volume classification)
GCP_MODEL_ROUTER=gemini-1.5-flash
```

---

## Important Notes

### ⚠️ Model Name Format

**DO NOT include provider prefixes in environment variables:**

```bash
# ❌ WRONG
GCP_MODEL_GREETING=google-vertex:gemini-1.5-flash

# ✅ CORRECT
GCP_MODEL_GREETING=gemini-1.5-flash
```

The provider prefix (`google-vertex:`) is added automatically by the code.

### 🎯 GCP/Vertex AI Only

**v3.3 is Gemini-only.** OpenAI and Anthropic support has been removed for:
- Enhanced security (Application Default Credentials)
- Simplified configuration
- Cost optimization with Gemini Flash models
- Single provider consistency

---

## Configuration Examples

### Example 1: Cost-Optimized Production (Recommended)

Use cheaper models for simple tasks, advanced for complex generation:

```bash
GCP_ENABLED=true

# Simple stages: Use cheap, fast Gemini 1.5 Flash
GCP_MODEL_GREETING=gemini-1.5-flash       # $0.075/1M tokens
GCP_MODEL_QUESTIONS=gemini-1.5-flash      # $0.075/1M tokens
GCP_MODEL_PLAN=gemini-1.5-flash           # $0.075/1M tokens
GCP_MODEL_ROUTER=gemini-1.5-flash         # $0.075/1M tokens

# Complex stages: Use advanced Gemini 2.0 Flash
GCP_MODEL_STRAWMAN=gemini-2.0-flash-exp   # $0.30/1M tokens
GCP_MODEL_REFINE=gemini-2.0-flash-exp     # $0.30/1M tokens
```

**Cost Savings:** ~60% vs using Gemini 2.0 everywhere

### Example 2: Maximum Quality (Most Expensive)

Use best model for all stages:

```bash
GCP_ENABLED=true

# All stages: Use advanced Gemini 2.0 Flash
GCP_MODEL_GREETING=gemini-2.0-flash-exp
GCP_MODEL_QUESTIONS=gemini-2.0-flash-exp
GCP_MODEL_PLAN=gemini-2.0-flash-exp
GCP_MODEL_STRAWMAN=gemini-2.0-flash-exp
GCP_MODEL_REFINE=gemini-2.0-flash-exp
GCP_MODEL_ROUTER=gemini-2.0-flash-exp
```

**Use Case:** Maximum quality for critical presentations, cost is secondary

### Example 3: Maximum Cost Savings

Use cheapest model everywhere:

```bash
GCP_ENABLED=true

# All stages: Use cheap, fast Gemini 1.5 Flash
GCP_MODEL_GREETING=gemini-1.5-flash
GCP_MODEL_QUESTIONS=gemini-1.5-flash
GCP_MODEL_PLAN=gemini-1.5-flash
GCP_MODEL_STRAWMAN=gemini-1.5-flash
GCP_MODEL_REFINE=gemini-1.5-flash
GCP_MODEL_ROUTER=gemini-1.5-flash
```

**Cost Savings:** Maximum savings, but quality may be lower for complex generation

### Example 4: Experimental Testing

Test experimental models for specific stages:

```bash
GCP_ENABLED=true

# Standard stages: Use stable models
GCP_MODEL_GREETING=gemini-1.5-flash
GCP_MODEL_QUESTIONS=gemini-1.5-flash
GCP_MODEL_PLAN=gemini-1.5-flash
GCP_MODEL_ROUTER=gemini-1.5-flash

# Complex generation: Test experimental thinking model
GCP_MODEL_STRAWMAN=gemini-2.0-flash-thinking-exp-1219  # If available
GCP_MODEL_REFINE=gemini-2.0-flash-exp                  # Stable fallback
```

**Use Case:** Experiment with new models without affecting entire workflow

### Example 5: Development vs Production

**Development (.env):**
```bash
# Use cheaper models for local testing
GCP_MODEL_GREETING=gemini-1.5-flash
GCP_MODEL_QUESTIONS=gemini-1.5-flash
GCP_MODEL_PLAN=gemini-1.5-flash
GCP_MODEL_STRAWMAN=gemini-1.5-flash
GCP_MODEL_REFINE=gemini-1.5-flash
GCP_MODEL_ROUTER=gemini-1.5-flash
```

**Production (Railway environment variables):**
```bash
# Use optimal balanced configuration
GCP_MODEL_GREETING=gemini-1.5-flash
GCP_MODEL_QUESTIONS=gemini-1.5-flash
GCP_MODEL_PLAN=gemini-1.5-flash
GCP_MODEL_STRAWMAN=gemini-2.0-flash-exp
GCP_MODEL_REFINE=gemini-2.0-flash-exp
GCP_MODEL_ROUTER=gemini-1.5-flash
```

---

## Available Gemini Models

### Current Models (January 2025)

| Model | Speed | Cost (per 1M tokens) | Best For |
|-------|-------|---------------------|----------|
| `gemini-1.5-flash` | ⚡⚡⚡ Very Fast | 💰 $0.075 | Greeting, Questions, Plan, Router |
| `gemini-2.0-flash-exp` | ⚡⚡ Fast | 💰💰 $0.30 | Strawman, Refine (complex generation) |
| `gemini-2.0-flash-thinking-exp-1219` | ⚡ Slower | 💰💰💰 Expensive | Experimental only (if available) |

### Model Selection Guide

**For Simple Stages (Greeting, Questions, Plan, Router):**
- ✅ **Recommended**: `gemini-1.5-flash` - Fast, cheap, perfectly adequate
- ⚠️ **Overkill**: `gemini-2.0-flash-exp` - Unnecessary quality, 4x cost

**For Complex Stages (Strawman, Refine):**
- ✅ **Recommended**: `gemini-2.0-flash-exp` - Best quality for generation
- ⚠️ **May struggle**: `gemini-1.5-flash` - Cheaper but lower quality
- 🧪 **Experimental**: `gemini-2.0-flash-thinking-exp-*` - Test carefully

---

## How It Works

### Code Implementation

When the Director Agent initializes, it:

1. Reads the 6 model environment variables from settings
2. Adds the `google-vertex:` prefix automatically
3. Assigns each model to its corresponding agent
4. Logs which models are being used

**Example Log Output:**

```
✓ Using Google Gemini via Vertex AI (Project: deckster-xyz)
  Authentication: ADC (local)
  Greeting model: gemini-1.5-flash
  Questions model: gemini-1.5-flash
  Plan model: gemini-1.5-flash
  Strawman model: gemini-2.0-flash-exp
  Refine model: gemini-2.0-flash-exp
✓ IntentRouter using Google Gemini via Vertex AI (Project: deckster-xyz)
  Router model: gemini-1.5-flash
```

### Agent Assignment

```python
# Automatically assigned based on environment variables:
greeting_agent = Agent(model='google-vertex:gemini-1.5-flash')        # Stage 1
questions_agent = Agent(model='google-vertex:gemini-1.5-flash')       # Stage 2
plan_agent = Agent(model='google-vertex:gemini-1.5-flash')            # Stage 3
strawman_agent = Agent(model='google-vertex:gemini-2.0-flash-exp')    # Stage 4
refine_strawman_agent = Agent(model='google-vertex:gemini-2.0-flash-exp')  # Stage 5
router_agent = Agent(model='google-vertex:gemini-1.5-flash')          # Intent router
```

---

## Testing Your Configuration

### 1. Quick Test

Run the deployment test suite:

```bash
python test_v33_deployment.py
```

This verifies:
- Models load correctly from environment
- Authentication works
- Agents initialize successfully

### 2. Full End-to-End Test

Run the standalone test with all stages:

```bash
python tests/test_director_standalone.py --scenario default --no-stage-6
```

This tests:
- All 5 stages of presentation generation
- Model performance with real workload
- Individual model selection per stage

### 3. Check Logs

Look for model initialization messages:

```bash
grep "model:" logs/app.log
```

You should see entries like:
```
Greeting model: gemini-1.5-flash
Questions model: gemini-1.5-flash
Plan model: gemini-1.5-flash
Strawman model: gemini-2.0-flash-exp
Refine model: gemini-2.0-flash-exp
Router model: gemini-1.5-flash
```

---

## Troubleshooting

### Issue: Model Not Found (404)

**Error:** `Publisher Model 'projects/.../models/gemini-xyz' not found`

**Solution:**
- Check model name spelling
- Verify model is available in your GCP region (us-central1)
- Try a different model (e.g., `gemini-1.5-flash`)
- Check model availability: https://ai.google.dev/models/gemini

### Issue: Models Not Loading from .env

**Error:** System uses wrong models despite .env values

**Solution:**
1. Ensure `.env` file exists in project root
2. Restart the application (environment variables load at startup)
3. Check for typos in variable names
4. Verify no hardcoded values in code

### Issue: GCP Not Enabled

**Error:** `GCP/Vertex AI must be enabled`

**Solution:**
1. Set `GCP_ENABLED=true` in .env
2. Verify Vertex AI API is enabled in GCP console
3. Check authentication:
   - Local: `gcloud auth application-default login`
   - Railway: Set `GCP_SERVICE_ACCOUNT_JSON` environment variable

### Issue: High Costs

**Error:** API costs higher than expected

**Solution:**
1. Check your model configuration - are you using expensive models everywhere?
2. Switch to cost-optimized configuration (Example 1 above)
3. Use `gemini-1.5-flash` for stages 1-3 and router
4. Monitor usage in GCP Console → APIs & Services → Enabled APIs → Vertex AI

---

## Migration from v3.2

### Changes from Previous Version

**Before (v3.2):**
- 3-tier system: STANDARD, TURBO, ROUTER
- STANDARD used for: greeting, questions, plan
- TURBO used for: strawman, refine

**After (v3.3):**
- 6-model granular system: one per stage + router
- Individual control over each stage
- GCP/Vertex AI only (OpenAI/Anthropic removed)

### Migration Steps

1. **Update .env file** - Add the 6 new model variables:
   ```bash
   GCP_MODEL_GREETING=gemini-1.5-flash
   GCP_MODEL_QUESTIONS=gemini-1.5-flash
   GCP_MODEL_PLAN=gemini-1.5-flash
   GCP_MODEL_STRAWMAN=gemini-2.0-flash-exp
   GCP_MODEL_REFINE=gemini-2.0-flash-exp
   GCP_MODEL_ROUTER=gemini-1.5-flash
   ```

2. **Remove old variables** - Delete from .env:
   - `GCP_MODEL_STANDARD`
   - `GCP_MODEL_TURBO`
   - All `OPENAI_MODEL_*` variables
   - All `ANTHROPIC_MODEL_*` variables
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`

3. **Test** - Run `python tests/test_director_standalone.py --scenario default --no-stage-6` to verify

4. **Optimize** (optional) - Adjust models per stage for cost/performance

---

## Best Practices

### ✅ DO

- Use cheaper models (`gemini-1.5-flash`) for simple stages (1-3, router)
- Use advanced models (`gemini-2.0-flash-exp`) for complex stages (4-5)
- Test model changes in development before production
- Monitor costs and performance after model changes
- Document your model choices in deployment docs
- Use cost-optimized configuration (Example 1) as your default

### ❌ DON'T

- Include provider prefixes in environment variables (`google-vertex:`)
- Use expensive models for all stages (unnecessary cost)
- Use cheapest models for strawman/refine (quality suffers)
- Change models in production without testing
- Use experimental models in production without fallback
- Hardcode model names in code

---

## Cost Analysis

### Typical Presentation Generation Cost (5 stages)

**Assumptions:**
- 50,000 tokens total across all stages
- Stage 1-3: 5,000 tokens each (simple)
- Stage 4-5: 15,000 tokens each (complex)
- Router: 2,500 tokens per user message

**Cost-Optimized Configuration (Example 1):**
- Stages 1-3: 15,000 tokens × $0.075/1M = $0.001125
- Stages 4-5: 30,000 tokens × $0.30/1M = $0.009
- Router: 2,500 tokens × $0.075/1M = $0.000188
- **Total: ~$0.0103 per presentation**

**All Gemini 2.0 Configuration (Example 2):**
- All stages: 50,000 tokens × $0.30/1M = $0.015
- Router: 2,500 tokens × $0.30/1M = $0.00075
- **Total: ~$0.0158 per presentation**

**Savings:** ~35% with cost-optimized configuration

---

## Support

For issues with model configuration:

1. Check this guide's Troubleshooting section
2. Review [V3.3_CHANGELOG.md](./V3.3_CHANGELOG.md) for changes
3. See [SECURITY.md](./SECURITY.md) for authentication
4. Check [README.md](./README.md) for general setup

---

**Status**: ✅ Available in v3.3+
**Last Updated**: October 31, 2025
**Architecture**: Granular 6-model per-stage configuration (Gemini-only)
