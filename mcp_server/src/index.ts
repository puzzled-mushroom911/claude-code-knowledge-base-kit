#!/usr/bin/env node

/**
 * Knowledge Base Kit — MCP Server
 *
 * A Model Context Protocol server that wraps Python-based tools for:
 *   - RAG knowledge base queries (single, multi-db, create, list)
 *   - YouTube transcript fetching, ingestion, analysis, and strategy
 *
 * Communicates via stdio transport so Claude Code (or any MCP client)
 * can call these tools directly.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { getConfig } from "./utils/config.js";
import { registerRagTools } from "./tools/rag.js";
import { registerYoutubeTools } from "./tools/youtube.js";

// ── Server bootstrap ───────────────────────────────────────────────────────

const SERVER_NAME = "knowledge-base-mcp";
const SERVER_VERSION = "1.0.0";

async function main(): Promise<void> {
  // Load configuration early so tool registrations can reference it
  const config = getConfig();

  // Create the MCP server
  const server = new McpServer(
    {
      name: SERVER_NAME,
      version: SERVER_VERSION,
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // ── Register tool groups ─────────────────────────────────────────────

  registerRagTools(server);
  registerYoutubeTools(server);

  // ── Connect via stdio transport ──────────────────────────────────────

  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Log startup to stderr (stdout is reserved for MCP protocol messages)
  console.error(
    `[${SERVER_NAME}] v${SERVER_VERSION} started — tools: ${config.tools_dir}`
  );
}

// ── Entry point ──────────────────────────────────────────────────────────

main().catch((err) => {
  console.error(`[${SERVER_NAME}] Fatal error:`, err);
  process.exit(1);
});
