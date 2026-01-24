# Setting Up n8n as MCP Server

This guide explains how to configure n8n workflows to act as MCP (Model Context Protocol) servers that can be called by your AI agent.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   AI Agent      │         │   n8n Instance   │
│  (Python Code)  │ ◄─────► │  (MCP Server)    │
└─────────────────┘         └──────────────────┘
        │                            │
        │                            ├─ Discovery Webhook
        │                            ├─ Tool 1 Webhook
        │                            ├─ Tool 2 Webhook
        └────────────────────────────┴─ Tool 3 Webhook
```

## Step 1: Create MCP Discovery Workflow in n8n

This workflow returns a list of all available tools.

### Workflow Structure:
1. **Webhook Node** (Trigger)
   - Method: GET
   - Path: `mcp-discovery`
   - Response: Immediately

2. **Code Node** - Return tool definitions:
```javascript
const tools = [
  {
    name: 'search_database',
    description: 'Search the database for records',
    endpoint: 'http://localhost:5678/webhook/search-database',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query string'
        },
        limit: {
          type: 'number',
          description: 'Maximum number of results',
          default: 10
        }
      },
      required: ['query']
    }
  },
  {
    name: 'send_notification',
    description: 'Send a notification via Slack/Email/etc',
    endpoint: 'http://localhost:5678/webhook/send-notification',
    input_schema: {
      type: 'object',
      properties: {
        message: {
          type: 'string',
          description: 'Notification message'
        },
        channel: {
          type: 'string',
          description: 'Channel to send to (slack/email/sms)',
          enum: ['slack', 'email', 'sms']
        }
      },
      required: ['message', 'channel']
    }
  }
  // Add more tools here
];

return [{ json: { tools } }];
```

3. **Respond to Webhook Node**
   - Response Data Source: All Entries
   - Response Code: 200

### Testing:
```bash
curl http://localhost:5678/webhook/mcp-discovery
```

## Step 2: Create Individual Tool Workflows

Each tool is a separate workflow with a webhook trigger.

### Example: Search Database Tool

1. **Webhook Node** (Trigger)
   - Method: POST
   - Path: `search-database`
   - Response: Using Respond to Webhook Node

2. **Code Node** - Validate Input:
```javascript
const input = $input.first().json;

// Validate required fields
if (!input.query) {
  throw new Error('Missing required parameter: query');
}

const query = input.query;
const limit = Math.min(input.limit || 10, 100); // Cap at 100

return [{
  json: {
    query: query,
    limit: limit
  }
}];
```

3. **Database/HTTP/etc Node** - Execute the actual work:
   - Configure your database connection
   - Use the query from previous node
   - Fetch results

4. **Code Node** - Format Response:
```javascript
const results = $input.all();

return [{
  json: {
    success: true,
    data: results,
    metadata: {
      timestamp: new Date().toISOString(),
      tool_name: 'search_database',
      count: results.length
    }
  }
}];
```

5. **Respond to Webhook Node**
   - Response Data Source: All Entries
   - Response Code: 200

### Testing:
```bash
curl -X POST http://localhost:5678/webhook/search-database \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 5}'
```

## Step 3: Example Tool Templates

### Weather Tool
```javascript
// Discovery entry
{
  name: 'get_weather',
  description: 'Get current weather for a location',
  endpoint: 'http://localhost:5678/webhook/get-weather',
  input_schema: {
    type: 'object',
    properties: {
      location: { type: 'string', description: 'City name or ZIP code' }
    },
    required: ['location']
  }
}

// Workflow: Webhook → HTTP Request (to weather API) → Format Response → Respond
```

### File Upload Tool
```javascript
// Discovery entry
{
  name: 'upload_file',
  description: 'Upload a file to cloud storage',
  endpoint: 'http://localhost:5678/webhook/upload-file',
  input_schema: {
    type: 'object',
    properties: {
      filename: { type: 'string', description: 'Name of the file' },
      content: { type: 'string', description: 'Base64 encoded file content' },
      folder: { type: 'string', description: 'Destination folder' }
    },
    required: ['filename', 'content']
  }
}

// Workflow: Webhook → Decode Base64 → Google Drive/S3/etc → Respond
```

### Data Processing Tool
```javascript
// Discovery entry
{
  name: 'process_data',
  description: 'Process and transform data using custom logic',
  endpoint: 'http://localhost:5678/webhook/process-data',
  input_schema: {
    type: 'object',
    properties: {
      data: { type: 'array', description: 'Array of data to process' },
      operation: { 
        type: 'string', 
        description: 'Operation to perform',
        enum: ['filter', 'transform', 'aggregate']
      }
    },
    required: ['data', 'operation']
  }
}
```

## Step 4: Security Considerations

### Add API Key Authentication

1. In n8n, add a **Code Node** after webhook:
```javascript
const input = $input.first().json;
const headers = $input.first().headers;

const expectedApiKey = 'your-secret-api-key';
const providedApiKey = headers['x-n8n-api-key'];

if (providedApiKey !== expectedApiKey) {
  throw new Error('Unauthorized: Invalid API key');
}

return [{ json: input }];
```

2. Update your `.env`:
```bash
N8N_API_KEY=your-secret-api-key
```

## Step 5: Running Your Python Code

1. Install dependencies:
```bash
uv pip install aiohttp
# or: pip install aiohttp
```

2. Update your `.env` file:
```bash
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key-here
```

3. Run the integrated version:
```bash
python main_with_n8n.py
```

## Step 6: Testing End-to-End

1. Start n8n (if not running):
```bash
npx n8n
# or if installed globally: n8n start
```

2. Import/Create the discovery workflow
3. Import/Create your tool workflows
4. Activate all workflows
5. Run your Python code:
```bash
python main_with_n8n.py
```

## Advanced: Dynamic Tool Registration

For larger setups, you can create a workflow that:
1. Scans all active workflows with a specific tag (e.g., "mcp-tool")
2. Automatically generates the discovery response
3. Updates when workflows are added/removed

```javascript
// Code node in discovery workflow
const workflows = $input.all(); // From n8n API node

const tools = workflows
  .filter(w => w.tags?.includes('mcp-tool'))
  .map(w => ({
    name: w.name.toLowerCase().replace(/\s+/g, '_'),
    description: w.notes || w.name,
    endpoint: `http://localhost:5678/webhook/${w.webhookPath}`,
    input_schema: JSON.parse(w.settings?.inputSchema || '{}')
  }));

return [{ json: { tools } }];
```

## Troubleshooting

### Tools not discovered
- Ensure n8n is running: `http://localhost:5678`
- Check the discovery webhook is active
- Verify the webhook path matches your configuration

### Tool calls failing
- Check tool webhook is active
- Verify input schema matches what you're sending
- Check n8n execution logs for errors

### Authentication errors
- Verify API key in `.env` matches n8n configuration
- Check headers are being sent correctly

## Next Steps

- Add error handling and retry logic
- Implement rate limiting
- Add logging and monitoring
- Create more complex tools with multiple steps
- Set up n8n in production (Docker/cloud)
