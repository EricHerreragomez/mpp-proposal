# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is

This is a **configuration-only** repository. There is no application source code, no
package manager, no build system, and no automated tests. The entire "product" is a
Cursor → ServiceNow ITSM MCP server connection defined in `.cursor/mcp.json` and
documented in `README.md`.

- No dependencies to install (no `package.json`, `requirements.txt`, `go.mod`, etc.).
- Nothing to lint/build/test. The only meaningful check is that `.cursor/mcp.json`
  is valid JSON:
  `python3 -c "import json; json.load(open('.cursor/mcp.json'))"`

### Running the "application" (the MCP connection)

The MCP server is `MPP-MCP-SNOW`, pointing at
`https://mckinsey.service-now.com/sncapps/mcp-server/mcp/servicenow_itsm_mcp_server`.
It is loaded by the Cursor client from `.cursor/mcp.json`; it is not a local service you
start with a shell command.

**This connection cannot be exercised from a Cursor Cloud Agent.** Reasons (all confirmed
during setup):

1. **Network egress is blocked.** `mckinsey.service-now.com` resolves
   (`148.139.175.18`) but the TLS connection is reset, and the host is not on the Cloud
   Agent egress allowlist. It is an internal McKinsey host that requires VPN.
2. **OAuth is interactive + Desktop-only.** Connecting requires the OAuth 2.0 sign-in
   flow against McKinsey ServiceNow and the `SERVICENOW_MCP_CLIENT_ID` /
   `SERVICENOW_MCP_CLIENT_SECRET` env vars (see `README.md`).

As `README.md` states, use this MCP server from **Cursor Desktop** on the McKinsey
network/VPN, not from Cloud Agents. Cloud Agents can only validate the config file
statically.
