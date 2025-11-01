import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { createLogger } from './utils/logger.js';
import { AzurePricingService } from './services/azure-pricing.service.js';
import { MCPController } from './controllers/mcp.controller.js';
import { PricingSearchSchema } from './schemas/pricing.schema.js';
import { zodToJsonSchema } from 'zod-to-json-schema';

// Load environment variables
dotenv.config();

const PORT = process.env.PORT || 3000;
const logger = createLogger();

// Initialize services
const azurePricingService = new AzurePricingService(logger);
const mcpController = new MCPController(azurePricingService, logger);

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req: Request, _res: Response, next) => {
  logger.info('Incoming request', {
    method: req.method,
    path: req.path,
    ip: req.ip,
  });
  next();
});

// Health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'azure-pricing-mcp',
    version: '2.0.0',
  });
});

// MCP protocol endpoint
app.post('/mcp', async (req: Request, res: Response) => {
  try {
    const { jsonrpc, method, params, id } = req.body;

    logger.debug('MCP request received', { method, id });

    // Validate JSON-RPC format
    if (jsonrpc !== '2.0') {
      res.status(400).json({
        jsonrpc: '2.0',
        error: {
          code: -32600,
          message: 'Invalid Request',
        },
        id: id || null,
      });
      return;
    }

    // Handle different MCP methods
    if (method === 'tools/list') {
      logger.debug('Handling tools/list request');
      
      const result = {
        tools: [
          {
            name: 'azure_price_search',
            description: 'Search Azure retail pricing information with flexible filtering options',
            inputSchema: zodToJsonSchema(PricingSearchSchema, 'PricingSearchSchema'),
          },
        ],
      };

      res.json({
        jsonrpc: '2.0',
        result,
        id,
      });
      return;
    } else if (method === 'tools/call') {
      const { name, arguments: args } = params || {};

      logger.info('Handling tools/call request', { toolName: name });

      if (name === 'azure_price_search') {
        const result = await mcpController.handlePriceSearch(args);
        res.json({
          jsonrpc: '2.0',
          result,
          id,
        });
        return;
      }

      res.status(500).json({
        jsonrpc: '2.0',
        error: {
          code: -32602,
          message: `Unknown tool: ${name}`,
        },
        id,
      });
      return;
    } else {
      res.status(400).json({
        jsonrpc: '2.0',
        error: {
          code: -32601,
          message: 'Method not found',
        },
        id,
      });
      return;
    }
  } catch (error) {
    logger.error('Error handling MCP request', { error });

    res.status(500).json({
      jsonrpc: '2.0',
      error: {
        code: -32603,
        message: 'Internal error',
        data: error instanceof Error ? error.message : 'Unknown error',
      },
      id: req.body.id || null,
    });
  }
});

// Error handling middleware
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  logger.error('Unhandled error', { error: err });
  res.status(500).json({
    error: 'Internal server error',
    message: err.message,
  });
});

// Start server
const server = app.listen(PORT, () => {
  logger.info(`Azure Pricing MCP Server started`, {
    port: PORT,
    env: process.env.NODE_ENV || 'development',
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    logger.info('HTTP server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT signal received: closing HTTP server');
  server.close(() => {
    logger.info('HTTP server closed');
    process.exit(0);
  });
});

export { app, server };
