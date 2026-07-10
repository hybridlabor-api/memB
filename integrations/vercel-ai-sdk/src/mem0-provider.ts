import { ProviderV3 } from '@ai-sdk/provider';
import { LanguageModelV3 } from '@ai-sdk/provider';
import { withoutTrailingSlash } from "@ai-sdk/provider-utils";
import { MemBChatModelId, MemBChatSettings, MemBConfig } from "./memb-types";
import { MemBGenericLanguageModel } from "./memb-generic-language-model";
import { LLMProviderSettings } from "./memb-types";

export interface MemBProvider extends ProviderV3 {
  (modelId: MemBChatModelId, settings?: MemBChatSettings): LanguageModelV3;

  chat(modelId: MemBChatModelId, settings?: MemBChatSettings): LanguageModelV3;
  completion(modelId: MemBChatModelId, settings?: MemBChatSettings): LanguageModelV3;

  languageModel(
    modelId: MemBChatModelId,
    settings?: MemBChatSettings
  ): LanguageModelV3;
}

export interface MemBProviderSettings {
  baseURL?: string;
  /**
   * Custom fetch implementation. You can use it as a middleware to intercept
   * requests or to provide a custom fetch implementation for e.g. testing
   */
  fetch?: typeof fetch;
  /**
   * @internal
   */
  generateId?: () => string;
  /**
   * Custom headers to include in the requests.
   */
  headers?: Record<string, string | undefined>;
  name?: string;
  membApiKey?: string;
  apiKey?: string;
  provider?: string;
  modelType?: "completion" | "chat";
  membConfig?: MemBConfig;

  /**
   * The configuration for the provider.
   */
  config?: LLMProviderSettings ;
}

export function createMemB(
  options: MemBProviderSettings = {
    provider: "openai",
  }
): MemBProvider {
  const baseURL =
    withoutTrailingSlash(options.baseURL) ?? "https://api.openai.com";
  const getHeaders = () => ({
    ...options.headers,
  });

  const createGenericModel = (
    modelId: MemBChatModelId,
    settings: MemBChatSettings = {}
  ) =>
    new MemBGenericLanguageModel(
      modelId,
      settings,
      {
        baseURL,
        fetch: options.fetch,
        headers: getHeaders(),
        provider: options.provider || "openai",
        name: options.name,
        membApiKey: options.membApiKey,
        apiKey: options.apiKey,
        membConfig: options.membConfig,
      },
      options.config
    );

  const createCompletionModel = (
    modelId: MemBChatModelId,
    settings: MemBChatSettings = {}
  ) =>
    new MemBGenericLanguageModel(
      modelId,
      settings,
      {
        baseURL,
        fetch: options.fetch,
        headers: getHeaders(),
        provider: options.provider || "openai",
        name: options.name,
        membApiKey: options.membApiKey,
        apiKey: options.apiKey,
        membConfig: options.membConfig,
        modelType: "completion",
      },
      options.config
    );

  const createChatModel = (
    modelId: MemBChatModelId,
    settings: MemBChatSettings = {}
  ) =>
    new MemBGenericLanguageModel(
      modelId,
      settings,
      {
        baseURL,
        fetch: options.fetch,
        headers: getHeaders(),
        provider: options.provider || "openai",
        name: options.name,
        membApiKey: options.membApiKey,
        apiKey: options.apiKey,
        membConfig: options.membConfig,
        modelType: "chat",
      },
      options.config
    );

  const provider = function (
    modelId: MemBChatModelId,
    settings: MemBChatSettings = {}
  ) {
    if (new.target) {
      throw new Error(
        "The MemB model function cannot be called with the new keyword."
      );
    }

    return createGenericModel(modelId, settings);
  };

  provider.specificationVersion = 'v3';
  provider.languageModel = createGenericModel;
  provider.completion = createCompletionModel;
  provider.chat = createChatModel;

  return provider as unknown as MemBProvider;
}

export const memb = createMemB();
