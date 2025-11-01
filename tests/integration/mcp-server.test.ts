import request from 'supertest';
import { app, server } from '../../src/server.js';

describe('MCP Server Integration', () => {
  afterAll((done) => {
    // Close server after tests
    server.close(done);
  });

  describe('Health Check', () => {
    it('should return 200 OK with status information', async () => {
      const response = await request(app).get('/health');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('status', 'ok');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('service', 'azure-pricing-mcp');
      expect(response.body).toHaveProperty('version', '2.0.0');
    });
  });

  describe('MCP Protocol - tools/list', () => {
    it('should list available tools', async () => {
      const response = await request(app)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'tools/list',
          id: 1,
        })
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('jsonrpc', '2.0');
      expect(response.body).toHaveProperty('id', 1);
      expect(response.body.result).toHaveProperty('tools');
      expect(response.body.result.tools).toHaveLength(1);
      expect(response.body.result.tools[0]).toHaveProperty('name', 'azure_price_search');
      expect(response.body.result.tools[0]).toHaveProperty('description');
      expect(response.body.result.tools[0]).toHaveProperty('inputSchema');
    });

    it('should return error for invalid JSON-RPC version', async () => {
      const response = await request(app)
        .post('/mcp')
        .send({
          jsonrpc: '1.0',
          method: 'tools/list',
          id: 1,
        })
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toHaveProperty('code', -32600);
    });
  });

  describe('MCP Protocol - tools/call', () => {
    it('should call azure_price_search tool with valid parameters', async () => {
      const response = await request(app)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'azure_price_search',
            arguments: {
              service: 'Virtual Machines',
              region: 'eastus',
              limit: 5,
            },
          },
          id: 2,
        })
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('jsonrpc', '2.0');
      expect(response.body).toHaveProperty('id', 2);
      expect(response.body).toHaveProperty('result');
      expect(response.body.result).toHaveProperty('content');
      expect(Array.isArray(response.body.result.content)).toBe(true);
      expect(response.body.result.content.length).toBeGreaterThan(0);
      expect(response.body.result.content[0]).toHaveProperty('type', 'text');
      expect(response.body.result.content[0]).toHaveProperty('text');

      // Parse the text response to validate structure
      const parsedResult = JSON.parse(response.body.result.content[0].text);
      expect(parsedResult).toHaveProperty('summary');
      expect(parsedResult).toHaveProperty('items');
      expect(Array.isArray(parsedResult.items)).toBe(true);
    }, 30000); // Increase timeout for API call

    it('should handle azure_price_search with minimal parameters', async () => {
      const response = await request(app)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'azure_price_search',
            arguments: {
              limit: 3,
            },
          },
          id: 3,
        })
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('result');
      expect(response.body.error).toBeUndefined();
    }, 30000);

    it('should return error for unknown tool', async () => {
      const response = await request(app)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'unknown_tool',
            arguments: {},
          },
          id: 4,
        })
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(500);
      expect(response.body).toHaveProperty('error');
    });

    it('should handle validation errors gracefully', async () => {
      const response = await request(app)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'tools/call',
          params: {
            name: 'azure_price_search',
            arguments: {
              limit: 'invalid', // Should be a number
            },
          },
          id: 5,
        })
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('result');
      
      // The result should contain validation error details
      const parsedResult = JSON.parse(response.body.result.content[0].text);
      expect(parsedResult).toHaveProperty('error');
    });
  });

  describe('MCP Protocol - method not found', () => {
    it('should return error for unsupported method', async () => {
      const response = await request(app)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'unsupported/method',
          id: 6,
        })
        .set('Content-Type', 'application/json');

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toHaveProperty('code', -32601);
    });
  });
});
