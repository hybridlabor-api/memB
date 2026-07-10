import { MemoryClient } from "./memb";
import type * as MemoryTypes from "./memb.types";

// Re-export all types from memb.types
export type {
  AddMemoryOptions,
  SearchMemoryOptions,
  GetAllMemoryOptions,
  DeleteAllMemoryOptions,
  ProjectOptions,
  Memory,
  MemoryHistory,
  MemoryUpdateBody,
  ProjectResponse,
  PromptUpdatePayload,
  Webhook,
  WebhookCreatePayload,
  WebhookUpdatePayload,
  Messages,
  Message,
  AllUsers,
  User,
  FeedbackPayload,
  CreateMemoryExportPayload,
  GetMemoryExportPayload,
} from "./memb.types";

// Re-export enums as values (not type-only)
export { Feedback, WebhookEvent } from "./memb.types";

// Export the main client
export { MemoryClient };
export default MemoryClient;

// Export structured exceptions
export {
  MemoryError,
  AuthenticationError,
  RateLimitError,
  ValidationError,
  MemoryNotFoundError,
  NetworkError,
  ConfigurationError,
  MemoryQuotaExceededError,
  createExceptionFromResponse,
} from "../common/exceptions";

export type { MemoryErrorOptions } from "../common/exceptions";
