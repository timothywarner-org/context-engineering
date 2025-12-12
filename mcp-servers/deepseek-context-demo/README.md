# DeepSeek Context Demo

This Node.js project demonstrates **context window utilization** for DeepSeek models with a colorful, animated terminal demo.

## 🧩 Features

- Token counting with `gpt-tokenizer`
- Dynamic CLI progress bar showing percentage of context window used
- Real API call to DeepSeek at the end
- Fully commented source for teaching/demo purposes

---

## ⚙️ Installation

1. **Clone or unzip this project**

   ```bash
   cd deepseek-context-demo
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Add your DeepSeek API key**

   Create a `.env` file (already included) and add your key:

   ```bash
   DEEPSEEK_API_KEY=your_api_key_here
   ```

4. **Run the demo**

   ```bash
   npm start
   ```

---

## 🎓 How It Works

1. The script builds a growing chat history and uses the tokenizer to count tokens.
2. It divides tokens used by the model’s max context (128K by default).
3. A CLI progress bar visualizes how much of the window is consumed.
4. When the loop finishes, it makes a real API call to demonstrate usage reporting.

---

## 🧠 Teaching Tips

- Use this to show **token budgeting** in real time.
- Pause mid-run to explain why long chats lose memory when context limits are hit.
- Experiment by changing `MAX_CONTEXT_TOKENS` or the number of iterations in the loop.

---

## 📦 Dependencies

- axios
- chalk
- cli-progress
- dotenv
- gpt-tokenizer

---

## 🧰 Project Structure

```
deepseek-context-demo/
├── package.json
├── .env
├── contextDemo.js
└── README.md
```

---

Happy teaching! 🎉
