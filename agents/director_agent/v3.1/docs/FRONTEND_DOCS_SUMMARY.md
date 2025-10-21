# Frontend Integration Documentation - Summary

**Created**: 2025-10-12
**Status**: ✅ Complete and Ready for Frontend Team
**Location**: `./docs/` folder

---

## 📦 What's Been Created

### 3 New Documents for Frontend Integration

| Document | Purpose | Who Should Read |
|----------|---------|-----------------|
| **docs/README.md** | Documentation index & navigation | Everyone (start here) |
| **docs/FRONTEND_QUICKSTART.md** | 5-minute integration guide | Frontend devs (quick start) |
| **docs/FRONTEND_INTEGRATION.md** | Complete integration reference | Frontend devs (full details) |

---

## 🎯 For Your Frontend Team

### **Give them these 2 files:**

1. **`docs/FRONTEND_QUICKSTART.md`** - Start here (5 minutes)
   - WebSocket connection code
   - Message sending/receiving
   - All 4 message types
   - Quick browser test
   - Integration checklist

2. **`docs/FRONTEND_INTEGRATION.md`** - Full reference (30 minutes)
   - Complete API specification
   - All message types with examples
   - UI layout recommendations
   - Full code examples (JS, TS, React)
   - Error handling patterns
   - Best practices
   - Troubleshooting guide

---

## 🚀 What Frontend Needs to Do

### 1. Create Split UI Layout

```
┌─────────────────────────────────────────────────┐
│              Director v2.0                      │
├──────────────────────┬──────────────────────────┤
│ CHAT (40%)           │ PRESENTATION (60%)       │
│                      │                          │
│ • Messages           │ • Empty initially        │
│ • Questions          │ • Loads iframe when      │
│ • Action buttons     │   presentation_url       │
│ • Status/progress    │   received               │
│                      │                          │
└──────────────────────┴──────────────────────────┘
```

### 2. Connect to WebSocket

```javascript
const ws = new WebSocket(
  `wss://directorv20-production.up.railway.app/ws?session_id=${UUID}&user_id=${USER_ID}`
);
```

### 3. Send Messages

```javascript
ws.send(JSON.stringify({
  type: 'user_message',
  data: { text: 'User message here' }
}));
```

### 4. Handle 4 Message Types

- **`chat_message`** - Display text & optional bullet points
- **`action_request`** - Show buttons for user to click
- **`status_update`** - Show loading spinner & progress bar
- **`presentation_url`** - Load URL in iframe (THIS IS THE KEY!)

### 5. Load Presentation in Iframe

```javascript
if (message.type === 'presentation_url') {
  const iframe = document.getElementById('presentation-iframe');
  iframe.src = message.payload.url;
  iframe.style.display = 'block';
}
```

---

## 📋 Key Information

### Production WebSocket URL
```
wss://directorv20-production.up.railway.app/ws
```

### Required Parameters
- `session_id` - UUID (generate client-side with `crypto.randomUUID()`)
- `user_id` - User identifier (can be username or UUID)

### Example Connection
```
wss://directorv20-production.up.railway.app/ws?session_id=550e8400-e29b-41d4-a716-446655440000&user_id=user_12345
```

### Message Format (Client → Server)
```json
{
  "type": "user_message",
  "data": {
    "text": "I need a presentation about AI in healthcare"
  }
}
```

### Presentation URL Message (Server → Client)
```json
{
  "type": "presentation_url",
  "payload": {
    "url": "https://web-production-f0d13.up.railway.app/p/abc-123",
    "presentation_id": "abc-123",
    "slide_count": 8,
    "message": "Your presentation is ready!"
  }
}
```

---

## 🎨 UI Design Guidelines

### Chat Panel (Left Side - 40%)
- **Background**: White or light gray
- **Messages**:
  - User messages: Right-aligned, colored background
  - AI messages: Left-aligned, with avatar icon 🤖
- **Buttons**: Primary (blue/green), Secondary (gray/white)
- **List items**: Bullets (•) with slight indentation
- **Input**: Text input + Send button at bottom

### Presentation Panel (Right Side - 60%)
- **Initial state**: Gray background with "Presentation will appear here" text
- **After URL**: Full-screen iframe with presentation
- **Optional**: "Open in new tab" button above iframe

### Loading States
- **Thinking**: Show "..." or spinner
- **Generating**: Show progress bar if `progress` field present
- **Complete**: Briefly show ✅ checkmark

---

## 🧪 Quick Test (Browser Console)

Frontend devs can test instantly in browser console:

```javascript
// 1. Connect
const ws = new WebSocket('wss://directorv20-production.up.railway.app/ws?session_id=' + crypto.randomUUID() + '&user_id=test');

// 2. Log all messages
ws.onmessage = (e) => console.log(JSON.parse(e.data));

// 3. Send topic
ws.send(JSON.stringify({
  type: 'user_message',
  data: { text: 'I need a presentation about AI' }
}));

// 4. Answer questions when asked
ws.send(JSON.stringify({
  type: 'user_message',
  data: { text: 'Healthcare professionals, 20 minutes' }
}));

// 5. Confirm plan
ws.send(JSON.stringify({
  type: 'user_message',
  data: { text: 'Yes, that looks great' }
}));

// 6. Wait ~20 seconds
// 7. You'll receive presentation_url message with the URL!
```

---

## ✅ Integration Checklist for Frontend

- [ ] Read FRONTEND_QUICKSTART.md
- [ ] Create split UI layout (chat + presentation)
- [ ] Implement WebSocket connection
- [ ] Generate session_id and user_id
- [ ] Implement message sending
- [ ] Handle chat_message (display text + list_items)
- [ ] Handle action_request (display buttons)
- [ ] Handle status_update (show loading/progress)
- [ ] Handle presentation_url (load in iframe) ⭐ **MOST IMPORTANT**
- [ ] Add error handling (connection lost, reconnect)
- [ ] Test complete conversation flow
- [ ] Test presentation loads correctly in iframe
- [ ] Add "Open in new tab" button (optional)
- [ ] Style UI to match design system

---

## 📊 Expected Conversation Flow

```
1. User opens app
   ↓
2. Frontend connects to WebSocket
   ↓
3. Server sends chat_message: "Hello! I'm Deckster..."
   ↓
4. User types: "I need a presentation about X"
   ↓
5. Server sends chat_message with questions (list_items)
   ↓
6. User answers questions
   ↓
7. Server sends chat_message with plan summary
   ↓
8. Server sends action_request: "Does this work?"
   ↓
9. User clicks "Yes" button (sends "Yes, let's build it!")
   ↓
10. Server sends status_update: "Creating presentation..." (with progress)
    ↓
11. Server sends presentation_url with the URL
    ↓
12. Frontend loads URL in iframe
    ↓
13. User sees reveal.js presentation!
```

---

## 🎁 What's Included in the Documentation

### FRONTEND_QUICKSTART.md
- ✅ WebSocket connection setup
- ✅ Message sending/receiving code
- ✅ All 4 message types with examples
- ✅ UI layout recommendation
- ✅ Complete flow diagram
- ✅ Quick browser console test
- ✅ Integration checklist
- ✅ Common issues & solutions

### FRONTEND_INTEGRATION.md
- ✅ Complete WebSocket API reference
- ✅ All message types with full payload specs
- ✅ Detailed UI implementation guide
- ✅ Full JavaScript code examples
- ✅ TypeScript types and interfaces
- ✅ React component example
- ✅ Error handling patterns
- ✅ Reconnection logic
- ✅ Best practices
- ✅ Testing procedures
- ✅ Troubleshooting guide

### docs/README.md
- ✅ Documentation navigation
- ✅ Quick links for all audiences
- ✅ Documentation by use case
- ✅ Key concepts summary
- ✅ Quick start summary
- ✅ Testing instructions

---

## 🔗 Important URLs

### Production
- **WebSocket**: `wss://directorv20-production.up.railway.app/ws`
- **Health Check**: https://directorv20-production.up.railway.app/health
- **Presentation URLs**: `https://web-production-f0d13.up.railway.app/p/{id}`

### Documentation
- **GitHub Repo**: https://github.com/Pramod-Potti-Krishnan/director_v2.0
- **Docs Folder**: `./docs/`

---

## 💡 Key Points to Tell Frontend Team

1. **WebSocket URL**: `wss://directorv20-production.up.railway.app/ws?session_id={UUID}&user_id={ID}`

2. **Send Format**: Always `{ type: 'user_message', data: { text: '...' }}`

3. **Receive 4 Types**:
   - `chat_message` - Show text
   - `action_request` - Show buttons
   - `status_update` - Show loading
   - `presentation_url` - **Load in iframe!**

4. **The Iframe**: When `presentation_url` received, set `iframe.src = payload.url`

5. **Complete Flow**: ~30 seconds from connection to presentation display

6. **Test First**: Use browser console test before building full UI

---

## 🚦 Current Status

✅ **Backend**: Fully operational on Railway
✅ **API**: Complete and tested
✅ **Documentation**: Complete (3 new docs)
✅ **Test Scripts**: Available (`test_railway_auto.py`, `test_railway_simple.py`)
✅ **Examples**: JavaScript, TypeScript, React included

**Frontend can start integration immediately!**

---

## 📞 Support

If frontend team has questions:
1. Check docs/FRONTEND_INTEGRATION.md
2. Test with browser console
3. Check common issues section
4. Run automated test: `python3 test_railway_auto.py`

---

**Ready to Share**: Send frontend team `docs/FRONTEND_QUICKSTART.md` and `docs/FRONTEND_INTEGRATION.md`

**Integration Time**: ~2-3 hours for experienced frontend developer

**Status**: ✅ **Ready for Production Integration**
