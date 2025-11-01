import winston from 'winston';

/**
 * Creates a Winston logger instance with structured JSON logging
 */
export function createLogger(level: string = process.env.LOG_LEVEL || 'info'): winston.Logger {
  const logger = winston.createLogger({
    level,
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.json()
    ),
    defaultMeta: { service: 'azure-pricing-mcp' },
    transports: [
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.timestamp(),
          winston.format.printf(({ timestamp, level, message, ...meta }) => {
            const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
            return `${timestamp} [${level}]: ${message} ${metaStr}`;
          })
        )
      })
    ]
  });

  return logger;
}
