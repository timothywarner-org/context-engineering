# 🚀 Getting Started Checklist - Context Journal MCP

## ⏱️ Quick Start (15 Minutes)

Use this checklist to get the MCP server running before your O'Reilly session.

---

## ✅ Pre-Flight Checklist

### **Step 1: Verify Prerequisites (3 min)**

- [ ] **Python 3.10+** installed
  ```bash
  python --version
  # Should show: Python 3.10.x or higher
  ```

- [ ] **Claude Desktop** installed and running
  - Download from: https://claude.ai/download
  - Launch app at least once

- [ ] **GitHub repo** created (optional but recommended)
  ```bash
  git init context-engineering
  cd context-engineering
  ```

### **Step 2: Install Dependencies (2 min)**

- [ ] Create project directory
  ```bash
  mkdir -p ~/context-journal-mcp
  cd ~/context-journal-mcp
  ```

- [ ] Copy all files from deliverables:
  - `context_journal_mcp.py`
  - `requirements.txt`
  - `README.md`
  - `INSTRUCTOR_GUIDE.md`
  - `QUICK_REFERENCE.md`
  - `PROJECT_SUMMARY.md`
  - `ARCHITECTURE_DIAGRAMS.md`

- [ ] Install Python packages
  ```bash
  pip install -r requirements.txt
  
  # Or install individually:
  pip install mcp pydantic httpx
  ```

- [ ] Verify server runs
  ```bash
  python context_journal_mcp.py --help
  # Should show help and exit immediately (not hang)
  ```

### **Step 3: Configure Claude Desktop (5 min)**

- [ ] **Find config file location:**
  
  **macOS:**
  ```bash
  open ~/Library/Application\ Support/Claude/
  # Look for: claude_desktop_config.json
  ```
  
  **Windows:**
  ```powershell
  explorer %APPDATA%\Claude\
  # Look for: claude_desktop_config.json
  ```

- [ ] **Edit config file** (create if doesn't exist):
  ```json
  {
    "mcpServers": {
      "context-journal": {
        "command": "python",
        "args": ["/ABSOLUTE/PATH/TO/context_journal_mcp.py"]
      }
    }
  }
  ```
  
  ⚠️ **CRITICAL:** Use absolute path, not relative!
  
  **Get absolute path:**
  ```bash
  # macOS/Linux
  pwd
  # Then: /full/path/from/pwd/context_journal_mcp.py
  
  # Windows
  cd
  # Then: C:\full\path\from\cd\context_journal_mcp.py
  ```

- [ ] **Save config file**

- [ ] **Completely quit Claude Desktop** (not just close window)
  - macOS: Cmd+Q
  - Windows: Right-click system tray icon → Quit

- [ ] **Restart Claude Desktop**

### **Step 4: Verify MCP Connection (3 min)**

- [ ] Look for **🔌 icon** in Claude Desktop
  - Should appear in bottom-right or sidebar

- [ ] Click **🔌 icon** to see tools
  - Should show: "context-journal"
  - Expand to see 6 tools:
    - create_context_entry
    - read_context_entry
    - update_context_entry
    - delete_context_entry
    - list_context_entries
    - search_context_entries

- [ ] **Test basic functionality** in Claude:
  ```
  Prompt: "Create a context entry titled 'Test Entry' with the context 
  'This is a test of the MCP server' and tag it with 'test' and 'demo'"
  ```

- [ ] Verify you see:
  - Claude making a tool call
  - Success response with entry_id
  - No errors

### **Step 5: Create Demo Data (2 min)**

- [ ] Create sample entries for demos:
  
  **Entry 1: Architecture Decision**
  ```
  "Create a context entry titled 'FastAPI Architecture Decision' with context 
  'Team chose FastAPI over Flask for async support and automatic OpenAPI docs. 
  Using Pydantic for validation. Deployment target: Azure Container Apps.' 
  Tag it with 'python', 'fastapi', 'architecture', 'azure'."
  ```

  **Entry 2: Database Choice**
  ```
  "Create a context entry titled 'Database Selection: PostgreSQL' with context 
  'Selected PostgreSQL 15 for ACID compliance and JSON support. Using async 
  driver asyncpg. Connection pooling via pgbouncer.' 
  Tag it with 'postgresql', 'database', 'architecture'."
  ```

  **Entry 3: Deployment Notes**
  ```
  "Create a context entry titled 'Azure Deployment Notes' with context 
  'Container Apps in West US 2. Managed identity for authentication. 
  Cosmos DB for context storage. Key Vault for secrets. Monitor via 
  Application Insights.' 
  Tag it with 'azure', 'deployment', 'production'."
  ```

- [ ] Verify entries created successfully (3 entries total)

---

## 🧪 Test Scenarios

Run these tests to ensure everything works:

### **Test 1: Create and Read**
- [ ] Create an entry (see Step 5 above)
- [ ] Note the entry_id returned (e.g., "ctx_0001")
- [ ] Read it back: "Read entry ctx_0001 in markdown format"
- [ ] Verify content matches

### **Test 2: Search**
- [ ] "Search for entries about 'azure'"
- [ ] Should find Azure-related entries
- [ ] Results show in markdown format

### **Test 3: List with Filters**
- [ ] "List all entries tagged with 'python'"
- [ ] Should filter to Python entries
- [ ] Pagination info shown

### **Test 4: Update**
- [ ] "Update entry ctx_0001 to add a note: 'Reviewed on 2025-10-20'"
- [ ] Verify update successful
- [ ] Read entry again to confirm note added

### **Test 5: Memory Persistence** ⭐ **KEY DEMO**
- [ ] Close Claude Desktop completely
- [ ] Reopen Claude Desktop
- [ ] Ask: "What architecture decisions have we documented?"
- [ ] Claude should search and find entries
- [ ] **This proves persistent memory works!**

---

## 🐛 Troubleshooting

### **MCP Server Not Showing**

**Problem:** No 🔌 icon in Claude Desktop

**Solutions:**
1. Check config file location
   ```bash
   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   type %APPDATA%\Claude\claude_desktop_config.json
   ```

2. Verify JSON is valid
   - Use JSONLint.com to validate
   - Check for missing commas, quotes

3. Check Python path is absolute
   ```bash
   # Test: Should print full path
   python -c "import os; print(os.path.abspath('context_journal_mcp.py'))"
   ```

4. Check Claude logs
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   
   # Windows
   Get-Content $env:APPDATA\Claude\logs\mcp*.log -Wait
   ```

### **Import Errors**

**Problem:** ModuleNotFoundError: No module named 'mcp'

**Solution:**
```bash
pip install --upgrade mcp pydantic httpx
```

### **Server Hangs**

**Problem:** Running `python context_journal_mcp.py` hangs forever

**Why:** MCP servers are long-running processes waiting for input via stdio

**Solution:** This is normal! Use `--help` flag to verify it works:
```bash
python context_journal_mcp.py --help
```

### **Tool Not Being Called**

**Problem:** Claude doesn't use the tools

**Solutions:**
1. Check tool descriptions are clear
2. Ask Claude explicitly: "Use the create_context_entry tool to..."
3. Check annotations are set correctly
4. Verify Pydantic validation isn't rejecting inputs

---

## 📚 Files Explained

| File | Purpose | When to Use |
|------|---------|-------------|
| `context_journal_mcp.py` | Main server code | Run locally, customize |
| `requirements.txt` | Dependencies | Install with pip |
| `README.md` | Full documentation | Reference during course |
| `INSTRUCTOR_GUIDE.md` | Teaching script | Use while teaching |
| `QUICK_REFERENCE.md` | Student cheat sheet | Hand out to students |
| `PROJECT_SUMMARY.md` | Overview & outcomes | Course planning |
| `ARCHITECTURE_DIAGRAMS.md` | Visual diagrams | Presentations |

---

## 🎓 Pre-Course Final Checks

**The Night Before:**
- [ ] All files in course repo
- [ ] Dependencies installed
- [ ] Server tested and working
- [ ] Demo data created
- [ ] Presentation slides prepared
- [ ] Azure account ready (for Segment 4)
- [ ] Backup plan prepared (pre-recorded demo if tech fails)

**5 Minutes Before Class:**
- [ ] Claude Desktop running with MCP connected
- [ ] Demo data visible when listing entries
- [ ] VS Code open with code file
- [ ] Azure Portal open (logged in)
- [ ] GitHub repo URL ready to share

**During Introduction:**
- [ ] Share screen with Claude Desktop
- [ ] Show the amnesia problem first
- [ ] Then enable MCP and show the solution
- [ ] Point to 🔌 icon

---

## 🎯 Success Criteria

**By end of setup, you should:**
- ✅ See 🔌 icon in Claude Desktop
- ✅ Have 6 tools listed under "context-journal"
- ✅ Successfully create and read an entry
- ✅ See persistence after closing/reopening Claude
- ✅ Have demo data ready to showcase

**Students should be able to:**
- ✅ Install and configure the server (15 min)
- ✅ Create their first context entry (5 min)
- ✅ Understand why MCP solves the amnesia problem (5 min)

---

## 🚀 You're Ready!

If all checkboxes are checked, you're ready to teach Context Engineering with MCP!

**Time to demo?** Start with:
1. Show the problem (amnesia)
2. Enable the solution (MCP)
3. Prove it works (persistence)
4. Explain how it works (code walkthrough)
5. Guide students to build their own

**Remember:** The "aha!" moment is when they close and reopen Claude and it **remembers**.

---

**Questions?** Check:
- README.md for full documentation
- INSTRUCTOR_GUIDE.md for teaching script
- QUICK_REFERENCE.md for commands

**Ready to crush this training!** 🎉
