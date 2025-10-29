# Stoic MCP Demo Runbook

A hands-on guide to showcase all features of the Stoic MCP server.

---

## 1. Enablement

### Claude Desktop Setup

1. **Add to Configuration**

   Edit `%APPDATA%\Claude\claude_desktop_config.json`:

   ```json
   {
     "mcpServers": {
       "stoic-mcp": {
         "command": "node",
         "args": [
           "C:\\github\\stoic-mcp\\local\\dist\\index.js"
         ]
       }
     }
   }
   ```

   **Important:** Update the path to match your installation location.

2. **Set Environment Variable** (if not already set)

   ```bash
   # Windows (System Properties > Environment Variables)
   DEEPSEEK_API_KEY=your_key_here
   ```

   The environment variable is automatically inherited by Claude Desktop.

3. **Restart Claude Desktop**

   Close and reopen Claude Desktop to load the MCP server.

4. **Verify Connection**

   Look for the MCP icon (🔌) in Claude Desktop indicating connected servers.

### VS Code Setup (Optional)

If you want to use this with VS Code's MCP support:

1. Install the MCP extension for VS Code
2. Add similar configuration to VS Code settings
3. Restart VS Code

---

## 2. Read Operations

### Get a Random Quote

**Sample Prompt:**
```
I need some Stoic wisdom to start my day.
```

**Expected Output:**
A random quote from the collection with author, source, and theme.

---

### Search by Author

**Sample Prompt:**
```
Show me all quotes by Marcus Aurelius.
```

**Alternative Prompts:**
- "Find quotes from Seneca"
- "What does Epictetus say?"

---

### Search by Theme

**Sample Prompt:**
```
I'm dealing with anxiety. Find me quotes about anxiety.
```

**Other Themes to Try:**
- control
- mindset
- courage
- resilience
- discipline
- gratitude
- adversity

---

### Search by Keyword

**Sample Prompt:**
```
Search for quotes mentioning 'mind' or 'thoughts'.
```

**Alternative:**
```
Find quotes about dealing with difficult people.
```

---

### View Favorites

**Sample Prompt:**
```
Show me my favorite quotes.
```

---

## 3. Write Operations

### Add a New Quote

**Sample Prompt:**
```
Add this quote to my collection:
"The best time to plant a tree was 20 years ago. The second best time is now."
Author: Marcus Aurelius
Source: Meditations, Book 4
Theme: action
```

**Verification:**
After adding, search for it to confirm it was saved.

---

### Toggle Favorite

**Sample Prompt:**
```
Mark quote #13 as a favorite.
```

**To Unfavorite:**
```
Remove quote #13 from favorites.
```

---

### Add Personal Notes

**Sample Prompt:**
```
Add this note to quote #5: "Reminds me to take calculated risks in my career. Fear of failure has held me back from deploying that major refactor."
```

**View Your Notes:**
```
Show me quote #5 with my notes.
```

---

### Delete a Quote

**Sample Prompt:**
```
Delete quote #7 from my collection.
```

---

## 4. AI-Powered Features

### Get Practical Explanation

**Sample Prompt:**
```
Explain quote #1 in the context of handling a difficult production incident.
```

**Alternative Context:**
```
How does quote #3 apply to dealing with imposter syndrome as a junior developer?
```

**More Examples:**
- "Explain quote #4 for code review situations"
- "How can I apply quote #10 to managing technical debt?"
- "Relate quote #8 to work-life balance challenges"

---

### Generate Custom Quote

**Sample Prompt:**
```
Generate a Stoic-style quote about debugging.
```

**Other Themes to Try:**
- code review
- imposter syndrome
- deadline pressure
- technical debt
- team collaboration
- learning new technologies
- production outages
- refactoring legacy code

**Follow-up:**
If you like the generated quote, you can add it to your collection using the `add_quote` command.

---

## 5. Demo Workflow: Complete Session

Here's a complete workflow that demonstrates multiple features:

### Step 1: Start Your Day
```
Give me a random Stoic quote to inspire my morning.
```

### Step 2: Find Relevance
```
That's interesting! Can you explain how quote #X applies to handling deployment anxiety?
```

### Step 3: Save Your Favorite
```
I love that quote. Mark it as a favorite.
```

### Step 4: Add Personal Reflection
```
Add this note to that quote: "This helped me during the Q4 release. Remember to focus on what I can control - my preparation and testing."
```

### Step 5: Search for More
```
Find me more quotes about control and preparation.
```

### Step 6: Create Something New
```
Generate a Stoic quote about embracing code review feedback.
```

### Step 7: Add It to Collection
```
Add that generated quote to my collection with:
- Author: Modern Stoic
- Source: AI Generated
- Theme: growth
```

### Step 8: Review Your Journey
```
Show me all my favorite quotes.
```

---

## 6. Advanced Use Cases

### Daily Standup Prep
```
Give me a quote about courage and resilience for our standup today. We're discussing the production incident from yesterday.
```

### Team Meeting Ice Breaker
```
Find a quote about collaboration or teamwork that I can share with my team.
```

### Code Review Mindset
```
I'm about to review some code that needs significant changes. Give me a quote about delivering difficult feedback with integrity.
```

### Dealing with Technical Debt
```
Search for quotes about discipline and long-term thinking. We need to convince stakeholders to pay down technical debt.
```

### Learning New Technology
```
Generate a Stoic quote about embracing discomfort and learning new things.
```

### Post-Mortem Reflection
```
Find quotes about learning from mistakes and moving forward constructively.
```

---

## 7. Tips & Tricks

### Natural Language Works
You don't need to use technical commands. Claude understands natural language:
- "Show me..." instead of "search_quotes"
- "Mark this as favorite" instead of "toggle_favorite"
- "Explain this quote" instead of "get_quote_explanation"

### Quote IDs
Pay attention to quote IDs (shown as `[#]` in search results). You'll need them for:
- Marking favorites
- Adding notes
- Getting explanations
- Deleting quotes

### Combine Operations
You can chain operations in one prompt:
```
Find quotes about mindset, then explain the first one in terms of learning TypeScript.
```

### Export Your Favorites
```
Show me all my favorite quotes formatted as a markdown list that I can copy into my journal.
```

---

## 8. Troubleshooting

### Server Not Showing in Claude Desktop
- Check that Claude Desktop was restarted
- Verify the config file path is correct
- Ensure `dist/` folder exists (run `npm run build`)

### AI Features Not Working
- Verify `DEEPSEEK_API_KEY` environment variable is set
- Check that the API key is valid at platform.deepseek.com
- Restart Claude Desktop after setting environment variables

### Quotes Not Persisting
- Check that `quotes.json` exists in the `local/` folder
- Verify file permissions allow read/write
- Look for error messages in Claude Desktop's MCP logs

---

## 9. Sample Session Output

Here's what a typical session might look like:

```
You: Give me a random Stoic quote.

Claude: Here's a Stoic quote for you:

"You have power over your mind - not outside events. Realize this, and you will find strength."
— Marcus Aurelius, Meditations
Theme: control
ID: 1

You: Explain that in terms of handling production incidents.

Claude: This quote is particularly relevant for production incidents...

[DeepSeek provides context-aware explanation about focusing on response rather than the incident itself]

You: Perfect! Mark that as a favorite and add a note: "Used this during the November outage."

Claude: Quote marked as favorite ⭐

Notes updated for:
"You have power over your mind - not outside events. Realize this, and you will find strength."
— Marcus Aurelius

Your notes: Used this during the November outage.
```

---

## 10. Next Steps

### Customize Your Collection
- Add quotes that resonate with your specific challenges
- Build themes relevant to your work (e.g., "remote-work", "leadership")
- Use personal notes to track when quotes helped you

### Share with Your Team
- Export favorite quotes for team documentation
- Use generated quotes in team channels
- Create themed collections for different scenarios

### Scale to Azure
When ready for production deployment, migrate to the Azure implementation with Cosmos DB for:
- Multi-user support
- Cloud scalability
- Advanced querying
- Backup and disaster recovery

---

**Happy philosophizing! May Stoic wisdom guide your code and your life.** 🏛️
