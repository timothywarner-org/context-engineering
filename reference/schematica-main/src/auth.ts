/**
 * Authentication middleware for Schematica MCP Server
 */

import { Request, Response, NextFunction } from 'express';

const API_KEY = process.env.MCP_API_KEY;

export interface AuthenticatedRequest extends Request {
  authenticated: boolean;
}

/**
 * Bearer token authentication middleware
 */
export function authMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Health check endpoint is public
  if (req.path === '/health' || req.path === '/') {
    return next();
  }

  if (!API_KEY) {
    console.warn('MCP_API_KEY environment variable not set - rejecting all requests');
    res.status(500).json({
      error: 'Server configuration error',
      message: 'API key not configured'
    });
    return;
  }

  const authHeader = req.headers.authorization;

  if (!authHeader) {
    res.status(401).json({
      error: 'Unauthorized',
      message: 'Missing Authorization header'
    });
    return;
  }

  // Expect "Bearer <token>" format
  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer') {
    res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid Authorization header format. Expected: Bearer <token>'
    });
    return;
  }

  const token = parts[1];

  if (token !== API_KEY) {
    res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid API key'
    });
    return;
  }

  // Token is valid
  (req as AuthenticatedRequest).authenticated = true;
  next();
}
