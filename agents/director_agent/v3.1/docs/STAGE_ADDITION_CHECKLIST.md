# Stage Addition Checklist for Director Agent

**Purpose**: Comprehensive checklist for adding new stages to the Director Agent workflow (e.g., v3.2 for images, v3.3 for diagrams, etc.)

**Created**: 2025-01-20
**Based on**: v3.1 Stage 6 (CONTENT_GENERATION) implementation gaps

---

## 📋 Complete File Update Checklist

When adding a new stage (e.g., `IMAGE_GENERATION`, `DIAGRAM_GENERATION`, etc.), update these **7 files + 1 new file**:

### 🔴 CRITICAL - Model Updates (Blocking)

#### 1. **src/models/agents.py**
- **What**: Add new state to `StateContext.current_state` Literal type
- **Line**: ~29-36
- **Pattern**:
```python
current_state: Literal[
    "PROVIDE_GREETING",
    "ASK_CLARIFYING_QUESTIONS",
    "CREATE_CONFIRMATION_PLAN",
    "GENERATE_STRAWMAN",
    "REFINE_STRAWMAN",
    "LAYOUT_GENERATION",
    "CONTENT_GENERATION",  # v3.1
    "IMAGE_GENERATION"     # v3.2 EXAMPLE
]
```

#### 2. **src/models/session.py**
- **What**: Add new state to `Session.current_state` Literal type
- **Line**: ~13-19
- **Pattern**: Same as agents.py
- **Impact**: Enables session persistence to Supabase

---

### 🟡 HIGH PRIORITY - Core Functionality

#### 3. **src/workflows/state_machine.py**
- **What**: Add to `VALID_STATES` list and define transitions in `STATE_TRANSITIONS`
- **Lines**: ~25 (VALID_STATES), ~33-35 (STATE_TRANSITIONS)
- **Pattern**:
```python
VALID_STATES = [
    # ... existing states ...
    "CONTENT_GENERATION",
    "IMAGE_GENERATION"  # v3.2 EXAMPLE
]

STATE_TRANSITIONS = {
    # ... existing transitions ...
    "CONTENT_GENERATION": ["IMAGE_GENERATION"],  # v3.1 -> v3.2
    "IMAGE_GENERATION": []  # Terminal state
}
```

#### 4. **src/agents/director.py** - Prompt Loading
- **What #1**: Add to `state_prompt_map` dictionary
- **Line**: ~113-119
- **Pattern**:
```python
state_prompt_map = {
    # ... existing mappings ...
    'CONTENT_GENERATION': 'content_generation.md',
    'IMAGE_GENERATION': 'image_generation.md'  # v3.2 EXAMPLE
}
```

- **What #2**: Add to `state_prompt_tokens` dictionary
- **Line**: ~142-148
- **Pattern**:
```python
self.state_prompt_tokens = {
    # ... existing states ...
    "CONTENT_GENERATION": 0,  # Doesn't use LLM
    "IMAGE_GENERATION": 0     # Doesn't use LLM if service-based
}
```
**Note**: Set to 0 if stage uses external service instead of LLM

#### 5. **src/agents/director.py** - Stage Processing Logic
- **What**: Add `elif` block in `process()` method for new stage
- **Line**: After existing stage blocks (~346+)
- **Pattern**:
```python
elif state_context.current_state == "IMAGE_GENERATION":
    # v3.2: Stage 7 - Image Service integration
    logger.info("Starting Stage 7: Image Generation")

    # Get enriched presentation from session
    enriched_data = state_context.session_data.get("enriched_presentation")

    # Call image service
    image_results = await self._generate_images(enriched_data, session_id)

    # Package and return response
    response = {
        "type": "presentation_url",
        "url": final_url,
        "images_generated": True,
        # ... metadata ...
    }
```

#### 6. **config/prompts/modular/[stage_name].md** (NEW FILE)
- **What**: Create new prompt file for the stage
- **Location**: `config/prompts/modular/`
- **Name**: `image_generation.md`, `diagram_generation.md`, etc.
- **Template**:
```markdown
# Stage X: [Stage Name]

**STATE**: [STATE_NAME]

[Purpose and role description]

## Your Role

[What this stage does]

## Service Integration

- Service URL: [service_url]
- [Service capabilities]
- [Timing expectations]

## Success Criteria

- [What defines success]

## Error Handling

- [How to handle failures]
```

#### 7. **src/utils/context_builder.py**
- **What #1**: Create new Strategy class
- **Line**: After existing strategies (~184+)
- **Pattern**:
```python
class ImageGenerationStrategy(StateContextStrategy):
    """IMAGE_GENERATION needs enriched presentation for image generation"""

    def build_context(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        # Extract what this stage needs from session_data
        return {
            "enriched_presentation": session_data.get("enriched_presentation"),
            "presentation_strawman": session_data.get("presentation_strawman"),
            # ... other required context ...
        }

    def get_required_fields(self) -> List[str]:
        return ["enriched_presentation"]

    def _extract_enriched_from_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        # Extraction logic
        pass
```

- **What #2**: Register strategy in `ContextBuilder.__init__`
- **Line**: ~219-227
- **Pattern**:
```python
self.strategies = {
    # ... existing strategies ...
    "CONTENT_GENERATION": ContentGenerationStrategy(),
    "IMAGE_GENERATION": ImageGenerationStrategy()  # v3.2 EXAMPLE
}
```

- **What #3**: Add prompt generation in `_generate_prompt()`
- **Line**: ~294+
- **Pattern**:
```python
elif state == "IMAGE_GENERATION":
    presentation = context.get('enriched_presentation', {})
    return f"""Generate images for presentation slides.

Current presentation: {presentation.get('title', '')}
Slides needing images: {len(presentation.get('slides', []))}

This stage generates visual assets using the Image Service."""
```

---

### 🟢 MEDIUM PRIORITY - User Experience

#### 8. **src/utils/streamlined_packager.py** - Message Packaging
- **What #1**: Add case in `package()` method
- **Line**: ~61-81
- **Pattern**:
```python
elif state == "IMAGE_GENERATION":
    return self._package_image_generation(session_id, agent_output)
```

- **What #2**: Create packaging method
- **Line**: After existing package methods
- **Pattern**:
```python
def _package_image_generation(self, session_id: str, agent_output: Any) -> List[StreamlinedMessage]:
    """Package image generation messages."""
    if isinstance(agent_output, dict) and agent_output.get("type") == "presentation_url":
        successful = agent_output.get("images_generated", 0)
        total = agent_output.get("total_images_needed", 0)

        text = f"✅ Images generated for your presentation!\n\n"
        text += f"🖼️  {successful}/{total} images created\n"
        text += f"🔗 View: {agent_output['url']}"

        return [create_chat_message(session_id=session_id, text=text)]
    else:
        return [create_chat_message(
            session_id=session_id,
            text="Processing image generation..."
        )]
```

#### 9. **src/utils/streamlined_packager.py** - Pre-Generation Status
- **What**: Add case in `create_pre_generation_status()`
- **Line**: ~411-421
- **Pattern**:
```python
elif state == "IMAGE_GENERATION":
    return create_chat_message(
        session_id=session_id,
        text="⏳ Generating images for your slides (10-30s per image)..."
    )
```

---

### 🟣 OPTIONAL - State Transitions

#### 10. **src/handlers/websocket.py** (if applicable)
- **What**: Update intent-to-state transitions if new intents needed
- **Line**: ~382-390
- **Pattern**:
```python
intent_to_next_state = {
    # ... existing mappings ...
    "Accept_Content": "IMAGE_GENERATION",  # New intent if needed
}
```

- **What**: Add to pre-generation status check
- **Line**: ~290
- **Pattern**:
```python
if use_streamlined and session.current_state in [
    "GENERATE_STRAWMAN",
    "REFINE_STRAWMAN",
    "CONTENT_GENERATION",
    "IMAGE_GENERATION"  # v3.2 EXAMPLE
]:
```

---

### 🔵 LOW PRIORITY - Documentation

#### 11. **src/agents/intent_router.py** (if new intents added)
- **What**: Document new intent types if applicable
- **Line**: Where intents are documented
- **Pattern**: Update intent descriptions to mention new stage

---

## 📊 Quick Reference Matrix

| Component | File | Action | Critical? |
|-----------|------|--------|-----------|
| Model - StateContext | `models/agents.py` | Add to Literal | 🔴 Yes |
| Model - Session | `models/session.py` | Add to Literal | 🔴 Yes |
| State Machine | `workflows/state_machine.py` | Add to lists + transitions | 🟡 Yes |
| Prompt Map | `agents/director.py` | Add mapping | 🟡 Yes |
| Token Count | `agents/director.py` | Add token count | 🟡 Yes |
| Processing Logic | `agents/director.py` | Add elif block | 🟡 Yes |
| Prompt File | `config/prompts/modular/` | Create new .md | 🟡 Yes |
| Context Strategy | `utils/context_builder.py` | Create + register | 🟡 Yes |
| Context Prompt | `utils/context_builder.py` | Add prompt gen | 🟡 Yes |
| Message Package | `utils/streamlined_packager.py` | Add handler | 🟢 Optional |
| Pre-Gen Status | `utils/streamlined_packager.py` | Add status | 🟢 Optional |
| WS Transitions | `handlers/websocket.py` | Update if needed | 🟣 Rare |

---

## 🎯 Implementation Template

### Step-by-Step for Adding New Stage

**Preparation**:
1. Define stage name (e.g., `IMAGE_GENERATION`)
2. Define stage purpose and service integration
3. Define required session data inputs
4. Define expected outputs

**Phase 1 - Enable State** (Critical):
```bash
1. Update models/agents.py - Add to Literal
2. Update models/session.py - Add to Literal
3. Update workflows/state_machine.py - Add to VALID_STATES + transitions
4. Test: Verify StateContext can be created with new state
```

**Phase 2 - Add Functionality** (High Priority):
```bash
5. Create config/prompts/modular/[stage_name].md
6. Update agents/director.py - state_prompt_map
7. Update agents/director.py - state_prompt_tokens
8. Update agents/director.py - Add processing logic (elif block)
9. Update utils/context_builder.py - Create Strategy class
10. Update utils/context_builder.py - Register strategy
11. Update utils/context_builder.py - Add prompt generation
12. Test: Run isolated stage test
```

**Phase 3 - Polish UX** (Medium Priority):
```bash
13. Update utils/streamlined_packager.py - package() handler
14. Update utils/streamlined_packager.py - pre-generation status
15. Update handlers/websocket.py - Add to pre-gen state list
16. Test: Verify WebSocket messages
```

**Phase 4 - Documentation** (Low Priority):
```bash
17. Update this checklist with any new patterns
18. Update relevant README files
19. Document API changes if applicable
```

---

## 🔍 Verification Checklist

After adding a new stage, verify:

- [ ] Can create StateContext with new state (no ValidationError)
- [ ] Can create Session with new state (no ValidationError)
- [ ] State machine accepts state and transitions work
- [ ] Director can load prompt for new state (no FileNotFoundError)
- [ ] Context builder has strategy registered (no ValueError)
- [ ] Processing logic executes without errors
- [ ] Streamlined messages are properly formatted
- [ ] Session can be persisted to Supabase
- [ ] Full workflow test passes end-to-end
- [ ] WebSocket messages display correctly in frontend

---

## 📝 Examples from v3.1 (CONTENT_GENERATION)

### What Worked Well
✅ Stage 6 processing logic in director.py (comprehensive)
✅ State machine transitions defined
✅ WebSocket handler updated
✅ Text Service client implementation

### What Was Missed (Fixed in this document)
❌ StateContext Literal not updated
❌ Session Literal not updated
❌ Prompt file not created
❌ state_prompt_map not updated
❌ state_prompt_tokens not updated
❌ Context builder strategy not created initially
❌ Streamlined packager not updated

---

## 🚀 Future Stage Planning

### v3.2 - Image Generation
- State: `IMAGE_GENERATION`
- Service: Image Builder Service
- Input: Enriched presentation with text
- Output: Presentation with images + text

### v3.3 - Diagram Generation
- State: `DIAGRAM_GENERATION`
- Service: Diagram Generator Service
- Input: Enriched presentation with text + images
- Output: Presentation with diagrams + images + text

### v3.4 - Chart Generation
- State: `CHART_GENERATION`
- Service: Charting Agent Service
- Input: Enriched presentation with text + images + diagrams
- Output: Complete presentation with all content types

---

## 💡 Key Insights

1. **States must be added to ALL Literal type definitions** - This is easy to miss!
2. **Every state needs a prompt file** - Even if it doesn't use LLM (for consistency)
3. **Context builder needs both Strategy class AND registration** - Two places to update
4. **Streamlined packager should have dedicated handlers** - Better UX than fallback
5. **Test each phase independently** - Don't wait until end to test

---

**Last Updated**: 2025-01-20
**Next Review**: When adding v3.2 (IMAGE_GENERATION)
