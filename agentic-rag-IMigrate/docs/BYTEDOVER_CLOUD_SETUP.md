# 🌐 ByteDover Cloud Setup Guide

This guide shows you how to connect your SAP iFlow RAG Agent to ByteDover cloud instead of using local memory storage.

## 🔍 Current Status

**Currently Running**: Local Mode (Offline)
- ✅ Memory stored locally in `memory/rag_memory.json`
- ❌ No cloud sync
- ❌ No ByteDover account connection

## 🚀 Quick Setup (3 Steps)

### Step 1: Get ByteDover API Key
1. Visit [ByteDover Dashboard](https://byterover.dev)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`, `bt-`, or `bytedover-`)

### Step 2: Configure Cloud Connection
Run the setup script:
```bash
python setup_bytedover_cloud.py
```

Or manually set your API key:
```bash
python switch_memory_mode.py cloud YOUR_API_KEY_HERE
```

### Step 3: Test Connection
```bash
python run_agent.py
```

## 🔧 Manual Configuration

### Option A: Environment Variables
```bash
# Set for current session
export BYTEDOVER_API_KEY="your_api_key_here"

# Or create .env file
echo "BYTEDOVER_API_KEY=your_api_key_here" > .env
```

### Option B: Update config.py
```python
# In config.py, change this line:
BYTEDOVER_API_KEY = os.getenv("BYTEDOVER_API_KEY", "your_api_key_here")
```

## 📊 Mode Switching

### Switch to Cloud Mode
```bash
python switch_memory_mode.py cloud YOUR_API_KEY
```

### Switch to Local Mode
```bash
python switch_memory_mode.py local
```

### Check Current Mode
```bash
python switch_memory_mode.py status
```

## 🧪 Testing Your Setup

### Test Connection
```bash
python setup_bytedover_cloud.py status
```

### Test Memory Manager
```bash
python memory_manager.py stats
```

### Run Agent with Cloud Sync
```bash
python run_agent.py
```

## 🔍 What Changes When You Go Cloud?

### Local Mode (Current)
- 📁 Memory stored in `memory/rag_memory.json`
- 🏠 Works offline
- 🔒 No external dependencies
- 📊 Limited to local storage

### Cloud Mode (ByteDover)
- ☁️ Memory synced to ByteDover cloud
- 🌐 Access from anywhere
- 🔄 Real-time sync across devices
- 📈 Advanced analytics and insights
- 🔍 Cross-session memory sharing
- 🏷️ Better tagging and organization

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Authentication failed"
- ✅ Check your API key is correct
- ✅ Ensure key is active in ByteDover dashboard
- ✅ Verify key format (starts with `sk-`, `bt-`, or `bytedover-`)

#### 2. "Network error"
- ✅ Check internet connection
- ✅ Verify ByteDover service is available
- ✅ Check firewall/proxy settings

#### 3. "Access forbidden"
- ✅ Check API key permissions
- ✅ Ensure account is active
- ✅ Contact ByteDover support if needed

### Debug Mode
Enable debug logging to see detailed sync information:
```bash
export LOG_LEVEL=DEBUG
python run_agent.py
```

## 📈 Benefits of Cloud Mode

### Enhanced Memory Management
- **Persistent Storage**: Never lose your agent's memory
- **Cross-Device Sync**: Access memories from anywhere
- **Advanced Search**: Better semantic search across all interactions
- **Analytics**: Track agent performance and learning patterns

### Better User Experience
- **Context Continuity**: Agent remembers past conversations
- **Learning**: Agent improves over time with more data
- **Collaboration**: Share memories across team members
- **Backup**: Automatic cloud backup of all interactions

## 🔒 Security & Privacy

### Data Protection
- All data encrypted in transit (HTTPS)
- API keys stored securely
- Local backup maintained
- GDPR compliant storage

### Access Control
- API key-based authentication
- User-specific memory isolation
- Configurable data retention
- Audit logs available

## 📞 Support

### ByteDover Support
- 📧 Email: support@byterover.dev
- 📚 Documentation: https://docs.byterover.dev
- 💬 Community: https://community.byterover.dev

### Local Support
- 🐛 Issues: Check logs in `memory/rag_memory.json`
- 🔧 Debug: Run with `LOG_LEVEL=DEBUG`
- 📊 Stats: Use `python memory_manager.py stats`

---

## 🎯 Next Steps

1. **Get your ByteDover API key** from the dashboard
2. **Run the setup script**: `python setup_bytedover_cloud.py`
3. **Test the connection**: `python run_agent.py`
4. **Enjoy cloud-powered memory** for your RAG agent!

Your agent will now have persistent, cloud-synced memory that improves over time! 🚀
