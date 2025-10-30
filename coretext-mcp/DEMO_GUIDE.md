# 🎓 Demo Script Guide for Instructors

> **Quick Reference for Teaching Context Engineering with MCP**
> Perfect for instructors who are not confident developers!

## 🚀 Pre-Class Setup (5 minutes)

### Before Your Class Starts

```bash
# 1. Navigate to project
cd C:\github\coretext-mcp

# 2. Ensure dependencies are installed
npm install

# 3. Test that everything works
npm test

# 4. Reset to clean state
npm run demo:reset

# 5. Populate with example data
npm run demo:populate
```

✅ **Success Indicator**: `npm test` shows 14/14 tests passing

---

## 📋 Available Demo Scripts

### Core Scripts

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `npm run demo:reset` | Wipe all memories, start fresh | Before class, between segments, when stuck |
| `npm run demo:populate` | Add 10 example memories | Quick recovery, showing variety |
| `npm run demo:segment1` | Run Segment 1 demos | Teaching basic CRUD + persistence |
| `npm run demo:segment2` | Run Segment 2 demos | Teaching memory types + enrichment |
| `npm run demo:segment3` | Run Segment 3 demos | Teaching knowledge graphs + multi-agent |
| `npm run demo:all` | Run all segments automatically | Student self-paced learning |
| `npm run inspector` | Open MCP Inspector UI | Live demos, visual exploration |
| `npm test` | Validate all 8 tools work | Before class, troubleshooting |

---

## 🎬 How to Use Demo Scripts During Class

### Interactive Mode (Default - Best for Teaching)

```bash
# Start a segment demo
npm run demo:segment1

# What happens:
# 1. Shows demo title and description
# 2. Runs the demo code
# 3. Displays results
# 4. PAUSES and waits for you to press Enter
# 5. Moves to next demo when you're ready
```

**Benefits**:

- ✅ You control the pace
- ✅ Can explain each step
- ✅ Students can read output
- ✅ Can answer questions between demos

### Automatic Mode (For Student Self-Paced)

```bash
# Run without pauses
npm run demo:segment1 -- --auto

# Or run all segments
npm run demo:all
```

**Benefits**:

- ✅ Students can run at home
- ✅ No manual intervention needed
- ✅ Great for review/practice

---

## 📚 Segment-by-Segment Teaching Guide

### Segment 1: From Prompts to Persistent Context (55 min)

**Goal**: Show that MCP solves AI amnesia

#### Teaching Flow

1. **Start with the Problem** (10 min)
   - Open ChatGPT in browser
   - Tell it: "Remember my favorite color is blue"
   - Start new session
   - Ask: "What's my favorite color?"
   - **Point**: It forgot! AI has amnesia.

2. **Show the Solution** (10 min)

   ```bash
   # Start server in one terminal
   npm run dev

   # Open Inspector in another terminal
   npm run inspector
   # Browser opens to http://localhost:5173
   ```

   - Show 8 tools in Inspector
   - Show 3 resources
   - **Point**: MCP provides persistent memory

3. **Run Segment 1 Demos** (25 min)

   ```bash
   npm run demo:segment1
   ```

   - Press Enter after each demo
   - Explain what happened
   - Answer student questions

4. **Prove Persistence** (10 min)

   ```bash
   # In the server terminal, press Ctrl+C to stop

   # Restart server
   npm run dev

   # Run Inspector again
   npm run inspector

   # Call memory_list tool
   # Show that all memories are still there!
   ```

   - **Point**: This is the "aha!" moment

#### Student Exercise (10 min)

Have students run on their own machines:

```bash
npm run demo:segment1 -- --auto
```

Then ask them to:

1. Create one semantic memory about themselves
2. Create one episodic memory about today
3. Search for their memories
4. Restart server and verify persistence

---

### Segment 2: Building Your Context Stack (55 min)

**Goal**: Understand memory types and enrichment

#### Teaching Flow

1. **Explain Memory Types** (10 min)
   - **Episodic**: Events on a timeline (WHEN)
   - **Semantic**: Facts and knowledge (WHAT)
   - Like human memory!

2. **Run Segment 2 Demos** (35 min)

   ```bash
   npm run demo:segment2
   ```

   - Press Enter after each demo
   - Highlight the enrichment demo (with/without API key)
   - Show resources (overview, context-stream)

3. **Deep Dive: Enrichment** (10 min)
   - If you have Deepseek API key: Show AI analysis
   - If no API key: Show fallback mode still works
   - **Point**: Graceful degradation for production

#### Student Exercise (10 min)

Have students:

1. Create 3 memories on same topic
2. Make them related (use same tags)
3. Try enrichment with `enrich: true`
4. View context-stream resource

---

### Segment 3: Advanced Patterns (55 min)

**Goal**: Knowledge graphs and multi-agent memory

#### Teaching Flow

1. **Run Segment 3 Demos** (45 min)

   ```bash
   npm run demo:segment3
   ```

   - Pause after knowledge graph demo
   - Show how tags create connections
   - Explain clusters
   - Demo multi-agent scenario

2. **Visualize the Graph** (10 min)

   ```bash
   # In Inspector, read resource: memory://knowledge-graph
   ```

   - Show JSON structure
   - Explain nodes, edges, clusters
   - **Point**: AI can navigate this network

#### Student Exercise (15 min)

Challenge students to:

1. Create 5 related memories
2. Use consistent tags
3. View knowledge graph
4. Find the cluster they created

---

## 🆘 Troubleshooting During Class

### Common Issues & Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| "Cannot find module" | `npm install` |
| "Port already in use" | Kill other server: `npx kill-port 3000 5173` |
| "Memory not persisting" | Check `data/memory.json` exists and has write permissions |
| "Demo script stuck" | Press `Ctrl+C` and run `npm run demo:reset` |
| "Inspector not opening" | Manually visit: `http://localhost:5173` |
| "Students lost/confused" | Run `npm run demo:populate` to reset to known state |

### Nuclear Option (When Everything Breaks)

```bash
# Stop all servers
# Press Ctrl+C in all terminals

# Complete reset
npm run demo:reset
npm install
npm run demo:populate
npm test

# Verify: Should show 14/14 tests passing
```

---

## 💡 Teaching Tips

### Before Each Segment

1. ✅ Run `npm test` to verify server works
2. ✅ Check `data/memory.json` exists
3. ✅ Have Inspector open in browser
4. ✅ Have demo script ready in terminal

### During Demos

1. ✅ Read the output aloud (helps visual and auditory learners)
2. ✅ Pause after each demo to ask: "What just happened?"
3. ✅ Use the emojis in output as visual cues (📅 = episodic, 💡 = semantic)
4. ✅ If script fails, no panic - just run `npm run demo:reset` and continue

### After Each Segment

1. ✅ Ask students to run the segment demo themselves
2. ✅ Give them 5-10 minutes to explore
3. ✅ Offer a student exercise
4. ✅ Reset before next segment: `npm run demo:reset && npm run demo:populate`

---

## 📊 Segment 4: Production Reality (45 min)

**Note**: This segment uses Azure Portal, not demo scripts

### Teaching Flow

1. **Show Dockerfile** (5 min)

   ```bash
   cat Dockerfile
   ```

   - Point out health check
   - Explain production settings

2. **Health Endpoint** (5 min)

   ```bash
   # Start server in background
   npm run dev

   # In another terminal, check health
   curl http://localhost:3000/health
   ```

   - Show JSON response
   - Explain Azure uses this

3. **Azure Deployment** (30 min)
   - Use Azure Portal or CLI
   - See TEACHING_GUIDE.md Demo 14-16
   - This is manual/live demo, not scripted

4. **Wrap-up** (5 min)
   - Review migration path
   - JSON → Cosmos DB
   - Local → Container Apps

---

## 🎯 Quick Command Reference Card

**Print this out and keep it visible during class!**

```
┌─────────────────────────────────────────────────────────┐
│  ESSENTIAL COMMANDS FOR TEACHING                        │
├─────────────────────────────────────────────────────────┤
│  Before Class:                                          │
│    npm test              - Verify everything works      │
│    npm run demo:reset    - Clean slate                  │
│    npm run demo:populate - Add examples                 │
│                                                          │
│  During Class:                                          │
│    npm run dev           - Start server (terminal 1)    │
│    npm run inspector     - Open UI (terminal 2)         │
│    npm run demo:segment1 - Run segment demos            │
│                                                          │
│  When Stuck:                                            │
│    Ctrl+C                - Stop server                  │
│    npm run demo:reset    - Fresh start                  │
│    npm install           - Fix dependencies             │
│                                                          │
│  For Students:                                          │
│    npm run demo:all      - All segments automatic       │
│    npm run demo:segment1 -- --auto                      │
│    npm run demo:segment2 -- --auto                      │
│    npm run demo:segment3 -- --auto                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎓 Student Handout

Give students this command sequence:

```bash
# Setup (first time only)
cd C:\github\coretext-mcp
npm install

# Run all demos automatically
npm run demo:all

# Or run each segment one at a time
npm run demo:segment1 -- --auto
npm run demo:segment2 -- --auto
npm run demo:segment3 -- --auto

# Experiment on your own
npm run demo:reset       # Start fresh
npm run demo:populate    # Add examples
npm run inspector        # Visual exploration
```

---

## 📝 Instructor Checklist

### Day Before Class

- [ ] `npm install` completed successfully
- [ ] `npm test` shows 14/14 passing
- [ ] Deepseek API key in `.env` (optional)
- [ ] Run each demo script to familiarize
- [ ] Print quick reference card

### 1 Hour Before Class

- [ ] `npm run demo:reset` for clean start
- [ ] `npm run demo:populate` for examples
- [ ] Test Inspector opens: `npm run inspector`
- [ ] Verify health endpoint: `curl http://localhost:3000/health`

### During Each Segment

- [ ] Terminal 1: `npm run dev` (server)
- [ ] Terminal 2: `npm run inspector` (UI)
- [ ] Terminal 3: `npm run demo:segmentN` (demos)
- [ ] Browser: Inspector at localhost:5173

### After Class

- [ ] Share student handout
- [ ] Share GitHub repo link
- [ ] Recommend: Students run `npm run demo:all` at home

---

## 🎤 Suggested Script

**Opening** (Segment 1):

> "Today we're solving a huge problem: AI amnesia. Every time you start a new chat, the AI forgets everything. Watch this..."
>
> [Demo ChatGPT forgetting]
>
> "Now, let me show you how MCP fixes this permanently. I'm going to run a script that creates memories, and then we'll restart the server to prove they survive."
>
> [Run demo:segment1]

**Key Phrases to Use**:

- "Press Enter when you're ready for the next demo"
- "Notice what just happened..."
- "This is the 'aha!' moment"
- "Let me show you the code that makes this work"
- "Try this on your own machine right now"

---

## 📚 Additional Resources

- **TEACHING_GUIDE.md**: Complete 4-segment lesson plan with exercises
- **CLAUDE.md**: Architecture and technical details
- **README.md**: User-facing documentation
- **src/index.js**: Complete server code (single file for teaching clarity)

---

**Good luck with your O'Reilly session, Tim! 🚀**

*Remember: The demos are designed to be resilient. If something breaks, just reset and continue. Your students will learn more from seeing you troubleshoot than from a perfect demo!*
