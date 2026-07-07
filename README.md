# mpp-proposal

McKinsey Platform Proposal — ServiceNow ITSM MCP integration for Cursor.

## ServiceNow MCP setup

This project connects Cursor to the McKinsey ServiceNow ITSM MCP server (`servicenow_itsm_mcp_server`) over OAuth 2.0.

### Prerequisites

- Cursor IDE (latest version with remote MCP + OAuth support)
- Access to the McKinsey ServiceNow instance (`mckinsey.service-now.com`)
- OAuth credentials from the **Machine Identity Console** → **Inbound integrations** for `servicenow_itsm_mcp_server`

### 1. Get OAuth credentials

1. In ServiceNow, open **Machine Identity Console** → **Inbound integrations**.
2. Find the integration for `servicenow_itsm_mcp_server`.
3. Copy the **Client ID** and **Client Secret** from that record.
4. Ensure the Cursor OAuth redirect URL is listed in the integration's **Redirect URLs** (Cursor will prompt you during first connect).

> Do not create a separate OAuth application manually. Use the auto-generated inbound integration for this MCP server so the correct auth scopes are applied.

### 2. Set environment variables

Add these to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export SERVICENOW_MCP_CLIENT_ID="d767680fb1024b44a93ddf92e6172bfa"
export SERVICENOW_MCP_CLIENT_SECRET="your-client-secret-here"
```

Restart Cursor after setting the variables so it can resolve `${env:...}` placeholders in `.cursor/mcp.json`.

### 3. Connect in Cursor

1. Open this project in Cursor.
2. Go to **Settings → MCP** (or **Cursor Settings → Tools & MCP**).
3. Confirm `MPP-MCP-SNOW` appears from `.cursor/mcp.json`.
4. Click **Connect** and complete the OAuth sign-in flow against McKinsey ServiceNow.

### MCP server URL

```
https://mckinsey.service-now.com/sncapps/mcp-server/mcp/servicenow_itsm_mcp_server
```

### Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Server not listed | Cursor not restarted after env vars set | Restart Cursor; verify `.cursor/mcp.json` is in the workspace root |
| OAuth fails | Missing or wrong redirect URL | Add Cursor's redirect URL to the inbound integration in ServiceNow |
| Connected but no tools | Wrong OAuth scope | Use `useraccount` scope (configured in `.cursor/mcp.json`) |
| Auth succeeds, empty tools | Wrong inbound integration / client | Use credentials from the `servicenow_itsm_mcp_server` integration only |
| Cloud Agent cannot reach ServiceNow | Network egress restriction | Use Cursor Desktop on the McKinsey network/VPN; Cloud Agents cannot reach `mckinsey.service-now.com` |

### Cloud Agent note

Cursor Cloud Agents run in a restricted network environment. The McKinsey ServiceNow instance is not on the egress allowlist, so this MCP server must be used from **Cursor Desktop** (with VPN/network access to ServiceNow), not from Cloud Agents.
