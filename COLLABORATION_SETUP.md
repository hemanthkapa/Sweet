# 🤝 Collaboration Setup Guide

This guide helps your teammate get up and running with the ilovesugar MCP server project.

## 🚀 Quick Start for Teammate

### 1. **Clone the Repository**
```bash
git clone https://github.com/hemanthkapa/ilovesugar.git
cd ilovesugar
```

### 2. **Set Up Python Environment**
```bash
# Create virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. **Test the Server Locally**
```bash
# Start the server
python src/server.py

# In another terminal, test it
python test_server.py
```

### 4. **Set Up ngrok (for Poke testing)**
```bash
# Install ngrok if not already installed
# https://ngrok.com/download

# Sign up for free account at https://dashboard.ngrok.com/signup
# Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken

# Configure ngrok
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE

# Expose your server
ngrok http 8000
```

### 5. **Connect to Poke**
1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add new connection:
   - **Name**: `ilovesugar`
   - **URL**: `https://YOUR_NGROK_URL.ngrok-free.app/mcp`
3. Test with: "Test the ilovesugar connection"

## 🔧 Development Workflow

### **Working on Features**
1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** to `src/server.py` or add new files

3. **Test locally**:
   ```bash
   python src/server.py
   python test_server.py
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request** on GitHub

### **Testing with Poke**
- Always test your changes with Poke before committing
- Use the test commands:
  - "Test the ilovesugar connection"
  - "Get server info from ilovesugar"
  - "Echo 'Hello from Poke!'"

## 📁 Project Structure

```
ilovesugar/
├── src/
│   └── server.py          # Main MCP server
├── test_server.py         # Local testing script
├── requirements.txt       # Python dependencies
├── render.yaml           # Deployment config
└── README.md             # Project documentation
```

## 🛠️ Available Tools

The server currently has these tools:
- `test_poke_connection()` - Test Poke connectivity
- `greet(name)` - Personalized greeting
- `get_server_info()` - Server details
- `echo(message)` - Echo test

## 🚨 Important Notes

### **Environment Variables**
- No sensitive data in the code (good!)
- All configuration is in the code or environment

### **ngrok Considerations**
- Each developer needs their own ngrok account
- ngrok URLs change each time you restart ngrok
- Update Poke connection URL when ngrok restarts

### **Git Workflow**
- Always work on feature branches
- Test locally before pushing
- Use descriptive commit messages

## 🆘 Troubleshooting

### **Server won't start**
```bash
# Check Python version
python --version  # Should be 3.12+

# Check virtual environment
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### **Poke connection fails**
1. Check ngrok is running: `ngrok http 8000`
2. Verify server is running: `python src/server.py`
3. Test locally: `python test_server.py`
4. Update Poke connection URL with new ngrok URL

### **Git issues**
```bash
# Pull latest changes
git pull origin main

# Reset to clean state
git checkout main
git pull origin main
```

## 📞 Getting Help

- Check the main README.md for project overview
- Test with `python test_server.py` first
- Verify Poke connection with "Test the ilovesugar connection"

---

**Happy coding! 🎉**
