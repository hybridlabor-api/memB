import { MemBProviderSettings } from "./memb-provider";
import { OpenAIProviderSettings } from "@ai-sdk/openai";
import { AnthropicProviderSettings } from "@ai-sdk/anthropic";
import { CohereProviderSettings } from "@ai-sdk/cohere";
import { GroqProviderSettings } from "@ai-sdk/groq";
import { GoogleGenerativeAIProviderSettings } from "@ai-sdk/google";
export type MemBChatModelId =
  | (string & NonNullable<unknown>);

export interface MemBConfigSettings {
  user_id?: string;
  app_id?: string;
  agent_id?: string;
  run_id?: string;
  metadata?: Record<string, any>;
  filters?: Record<string, any>;
  infer?: boolean;
  page?: number;
  page_size?: number;
  membApiKey?: string;
  top_k?: number;
  threshold?: number;
  rerank?: boolean;
  host?: string;
}

export interface MemBChatConfig extends MemBConfigSettings, MemBProviderSettings {}

export type LLMProviderSettings = OpenAIProviderSettings | AnthropicProviderSettings | CohereProviderSettings | GroqProviderSettings | GoogleGenerativeAIProviderSettings;

export interface MemBConfig extends MemBConfigSettings {}
export interface MemBChatSettings extends MemBConfigSettings {}
