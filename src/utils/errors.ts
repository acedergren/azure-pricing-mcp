/**
 * Custom error classes for Azure Pricing Service
 */

export class AzureAPIError extends Error {
  constructor(message: string, public readonly originalError?: unknown) {
    super(message);
    this.name = 'AzureAPIError';
    Object.setPrototypeOf(this, AzureAPIError.prototype);
  }
}

export class RateLimitError extends Error {
  constructor(message: string, public readonly retryAfter?: number) {
    super(message);
    this.name = 'RateLimitError';
    Object.setPrototypeOf(this, RateLimitError.prototype);
  }
}

export class ValidationError extends Error {
  constructor(message: string, public readonly validationErrors?: unknown) {
    super(message);
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}
