# Quick Test Guide - Enhanced Features

## 🚀 Quick Start Testing

### 1. Start the Server

```bash
# Make sure you're in the project directory
cd /home/venomblood1207/Desktop/Maerskv2

# Activate your environment
conda activate gda-corp-ai-agent  # or your environment name

# Start the backend server
python main.py
```

You should see:
```
✓ Applied Pydantic v1 Python 3.12 compatibility patch
============================================================
E-commerce Intelligence Agent Starting...
============================================================
✓ Server running on http://0.0.0.0:8000
✓ API docs available at http://0.0.0.0:8000/docs
============================================================
```

### 2. Test Enhanced Features

Open a new terminal and try these commands:

#### Test 1: Personalized Greeting (First Time)
```bash
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello", "session_id": "test_user_1"}'
```

**Expected:** Welcome message with full introduction

#### Test 2: Ask for Help
```bash
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "What can you do?", "session_id": "test_user_1"}'
```

**Expected:** Comprehensive help with capabilities list

#### Test 3: Definition Lookup
```bash
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "Define conversion rate", "session_id": "test_user_1"}'
```

**Expected:** Clear definition in e-commerce context

#### Test 4: Get User Profile
```bash
curl http://localhost:8000/session/test_user_1/profile
```

**Expected:** JSON with user stats and preferences

#### Test 5: Translation
```bash
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "Translate cama_mesa_banho to English", "session_id": "test_user_1"}'
```

**Expected:** Translation with context

#### Test 6: Time Query
```bash
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "What time is it?", "session_id": "test_user_1"}'
```

**Expected:** Current date and time

#### Test 7: Returning User Greeting
```bash
# Make several more queries first to build up interaction count
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "Show top products", "session_id": "test_user_1"}'

curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "What about reviews?", "session_id": "test_user_1"}'

# Now say hello again
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello", "session_id": "test_user_1"}'
```

**Expected:** Personalized welcome back message

#### Test 8: Context Awareness
```bash
# First query
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about furniture products", "session_id": "test_user_2"}'

# Follow-up (tests context retention)
curl -X POST http://localhost:8000/query/enhanced \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top sellers?", "session_id": "test_user_2"}'
```

**Expected:** Second response should reference furniture context

### 3. Test with Frontend

#### Start Frontend:
```bash
cd frontend
npm run dev
```

Open browser: http://localhost:3000

#### Try these in the chat:
1. "Hello" - See personalized greeting
2. "What can you help me with?" - See capabilities
3. "Define churn rate" - See definition
4. "Translate moveis_decoracao" - See translation
5. "Show top products" then "What about their reviews?" - Test context

### 4. Check User Profile

After several interactions:
```bash
curl http://localhost:8000/session/test_user_1/profile | jq
```

You should see:
```json
{
  "session_id": "test_user_1",
  "profile": {
    "total_interactions": 8,
    "query_types": {
      "utility": 4,
      "translation": 1,
      "data_query": 2,
      "knowledge_search": 1
    },
    "topics_of_interest": {
      "product": 2,
      "review": 1
    },
    "last_interaction": "2024-01-15T10:30:00"
  },
  "stats": {
    "total_messages": 16,
    "has_summary": false
  }
}
```

### 5. Test System Stats

```bash
curl http://localhost:8000/stats | jq
```

Expected output:
```json
{
  "tables": {
    "orders": 99441,
    "order_items": 112650,
    "customers": 99441,
    ...
  },
  "active_sessions": 2,
  "enhanced_sessions": 2,
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🎯 What to Look For

### Personalization
- ✅ First greeting is welcoming and detailed
- ✅ Returning user greetings reference past interactions
- ✅ Responses adapt to user experience level

### Context Retention
- ✅ Follow-up questions understand previous context
- ✅ "What about X?" queries work without repeating info
- ✅ Conversation flows naturally

### Knowledge Depth
- ✅ Definitions are clear and contextual
- ✅ Product queries include multiple data sources
- ✅ External information is integrated

### Smart Utilities
- ✅ Help is comprehensive and organized
- ✅ Translations work both ways
- ✅ Time/date queries respond correctly
- ✅ Location queries provide insights

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Restart
python main.py
```

### Database Errors
```bash
# Create database directory
mkdir -p database

# If you have data, reingest
python scripts/ingest_data.py
```

### Import Errors
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

### Pydantic Errors
The `fix_pydantic.py` should handle Python 3.12 compatibility automatically.
If you still see errors, check that the import is first in `main.py`:
```python
import fix_pydantic  # Must be first!
```

## 📊 Performance Benchmarks

Expected response times:
- Utility queries: < 0.5s
- Translation: < 1s
- Data queries: 1-2s
- Knowledge queries: 2-3s (multi-source)

## 🎉 Success Indicators

You'll know it's working when:
1. ✅ Greetings change based on interaction count
2. ✅ User profile shows accumulated data
3. ✅ Follow-up questions understand context
4. ✅ Definitions and utilities work smoothly
5. ✅ No errors in server logs

## 📝 Test Checklist

- [ ] Server starts without errors
- [ ] First greeting is welcoming
- [ ] Help command shows all capabilities
- [ ] Definitions work correctly
- [ ] Translations work both ways
- [ ] Time queries respond
- [ ] User profile accumulates data
- [ ] Context is retained across queries
- [ ] Returning user greeting is personalized
- [ ] Frontend connects and works
- [ ] WebSocket streaming works
- [ ] System stats show correct data

## 🚀 Next Steps

Once basic tests pass:
1. Try complex multi-turn conversations
2. Test with actual data queries (if database is populated)
3. Explore the API docs at http://localhost:8000/docs
4. Read [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) for detailed features
5. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details

---

**Happy Testing! 🎉**

If you encounter any issues, check the server logs for detailed error messages.
