# Sweet by Metabolic Company of CalHacks

**Manage diabetes from your textbox**

## Features:

- **🔗 Dexcom Integration** - Real-time glucose monitoring with trend analysis and historical data
- **🍎 AI Food Analysis** - Smart nutrition breakdown with personalized tips using Gemini AI
- **💉 Insulin Calculator** - Precise dosing based on carbs and glucose with safety checks (keep in mind this is a fun hack, dont take it too seriosly: at least for now.)
- **📊 Pattern Learning** - Track meals and glucose responses for personalized recommendations
- **🚨 Smart Alerts** - Background monitoring with AI-generated suggestions for high/low glucose
- **🤖 MCP Server** - Works seamlessly with Poke AI assistant through conversational text

## 👻 Start:

### Prerequisites

- Dexcom Account (username and password)
- Gemini API Key
- Python 3.8+
- Ngrok account (for exposing local server)

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ilovesugar
   ```

2. **Set up Python environment**

   ```bash
   cd mcp
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the `mcp/` directory:

   ```env
   DEXCOM_USERNAME=your_dexcom_userame
   DEXCOM_PASSWORD=your_dexcom_password
   DEXCOM_REGION=your_region  # Options: us, ous, jp (us=United States, ous=Outside US, jp=Japan)
   GEMINI_API_KEY=your_gemini_api_key
   # Server Configuration
   PORT=8000
   ENVIRONMENT=development
   ```

4. **Start the MCP server**

   ```bash
   cd mcp/src
   python server.py
   ```

5. **Expose server via Ngrok**
   In a new terminal:
   ```bash
   ngrok http 8000
   ```
   Copy the HTTPS URL (e.g., `https://randommonkey.ngrok-free.app`)

### Connecting to Poke

1. **Configure Poke MCP Integration**

   In your [Poke](https://poke.com) dashboard, add the Sweet MCP server:

   - Go to your Poke MCP integration settings
   - Add your ngrok URL (e.g., `https://abc123.ngrok-free.app/mcp`) as the server endpoint
   - This allows Poke to communicate with your running Sweet server

2. **Start using Sweet!**

   Simply text Poke on your phone with messages like:

   - "What is my current glucose level?"
   - "I'm having this meal, could you please analyze the macros based on the description/image?"
   - "How much insulin should i be taking for this meal?"
   - "Analyze my glucose levels starting this morning, what meal has affected me the most?"

   Sweet can do much more, your imagination is the limit.

## Available tools

### Main Functions:

- **`get_current_glucose()`** - Get real-time glucose reading from Dexcom CGM
- **`analyze_food(food_description)`** - AI-powered nutrition analysis with personalized tips
- **`calculate_insulin_dose(carb_grams, ...)`** - Calculate insulin dose based on carbs and glucose
- **`track_meal_context(food, carbs, insulin, glucose)`** - Log meals for pattern learning
- **`start_glucose_alerts(thresholds)`** - Begin background glucose monitoring with AI alerts
- **`get_diabetes_management_summary()`** - Get comprehensive diabetes management overview

---

Wohoo have a sweet life 💌
