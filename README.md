# ilovesugar MCP Server

An MCP server built with [FastMCP](https://github.com/jlowin/fastmcp) that integrates Dexcom glucose monitoring, AI-powered suggestions (Gemini), and Twilio SMS alerts to pre-registered recipients.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/InteractionCo/mcp-server-template)

## Local Development

### Setup

Fork the repo, then run:

```bash
git clone <your-repo-url>
cd mcp-server-template
conda create -n mcp-server python=3.13
conda activate mcp-server
pip install -r requirements.txt
```

### Test

```bash
python src/server.py
# then in another terminal run:
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport (NOTE THE `/mcp`!).

## Twilio SMS Alerts

When glucose is high/low, the background monitor can send SMS alerts to pre-registered people.

Configure Twilio via environment variables (recommended to place these in your `.env` file):

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM=+15551234567

# Optional: comma-separated list of phone numbers
ALERT_RECIPIENTS=+15557654321,+15559876543

# Optional: file path to store recipients
ALERT_RECIPIENTS_FILE=./recipients.json

# Optional: force dry-run (no real SMS) for testing
TWILIO_DRY_RUN=true
```

You can manage recipients via MCP tools (usable from Poke or the MCP Inspector):

- `list_alert_recipients()` – View merged recipients (file + env)
- `add_alert_recipient(name, phone)` – Add to file-backed list
- `remove_alert_recipient(phone)` – Remove from file-backed list
- `send_test_sms(message?)` – Send a test SMS to all recipients
- `send_test_glucose_alert(level?, value?)` – Send a test glucose-style alert SMS

Background monitor tools (already present):

- `start_glucose_alerts(low_threshold?, high_threshold?, interval_minutes?)`
- `stop_glucose_alerts()`
- `glucose_alerts_status()`
- `get_latest_glucose_alert()`

## Deployment

### Option 1: One-Click Deploy

Click the "Deploy to Render" button above.

### Option 2: Manual Deployment

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Connect your forked repository
5. Render will automatically detect the `render.yaml` configuration

Your server will be available at `https://your-service-name.onrender.com/mcp` (NOTE THE `/mcp`!)

## Poke Setup

You can connect your MCP server to Poke at (poke.com/settings/connections)[poke.com/settings/connections].
To test the connection explitly, ask poke somethink like `Tell the subagent to use the "{connection name}" integration's "{tool name}" tool`.
If you run into persistent issues of poke not calling the right MCP (e.g. after you've renamed the connection) you may send `clearhistory` to poke to delete all message history and start fresh.
We're working hard on improving the integration use of Poke :)

## Dexcom and Gemini Setup

In your `.env`:

```
DEXCOM_USERNAME=your_username_or_email_or_phone
DEXCOM_PASSWORD=your_password
DEXCOM_REGION=us  # Options: us, ous, jp

GEMINI_API_KEY=your_gemini_api_key
```

## Notes

- If Twilio is not configured or not installed, the server gracefully falls back to dry-run (alerts are logged but not sent).
- Recipients specified in `ALERT_RECIPIENTS` are read-only; use the MCP tools to manage the file-backed list.
- The alert SMS message is concise and includes level, value, threshold, timestamp, and an AI-generated short suggestion when available.

## Customization

Add more tools by decorating functions with `@mcp.tool`:

```python
@mcp.tool
def calculate(x: float, y: float, operation: str) -> float:
    """Perform basic arithmetic operations."""
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    # ...
```
