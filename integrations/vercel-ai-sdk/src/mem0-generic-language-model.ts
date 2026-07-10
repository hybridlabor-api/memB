/* eslint-disable camelcase */
import {
  LanguageModelV3,
  LanguageModelV3CallOptions,
  LanguageModelV3GenerateResult,
  LanguageModelV3Message,
  LanguageModelV3Source,
  LanguageModelV3StreamResult,
} from '@ai-sdk/provider';

import { MemBChatConfig, MemBChatModelId, MemBChatSettings, MemBConfigSettings } from "./memb-types";
import { MemBClassSelector } from "./memb-provider-selector";
import { MemBProviderSettings } from "./memb-provider";
import { addMemories, getMemories } from "./memb-utils";

const generateRandomId = () => {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export class MemBGenericLanguageModel implements LanguageModelV3 {
  readonly specificationVersion = "v3";
  readonly supportedUrls: Record<string, RegExp[]> = {
    '*': [/.*/]
  };

  constructor(
    public readonly modelId: MemBChatModelId,
    public readonly settings: MemBChatSettings,
    public readonly config: MemBChatConfig,
    public readonly provider_config?: MemBProviderSettings
  ) {
    this.provider = config.provider ?? "openai";
  }

  provider: string;

  private async processMemories(messagesPrompts: LanguageModelV3Message[], membConfig: MemBConfigSettings) {
    try {
      // Add new memories — await to ensure writes complete before returning
      try {
        await addMemories(messagesPrompts, membConfig);
      } catch (e) {
        console.error("Error while adding memories");
      }

      // Get memories (always returns an array since graph support is removed)
      const memories: any[] = await getMemories(messagesPrompts, membConfig) ?? [];

      const mySystemPrompt = "These are the memories I have stored. Give more weightage to the question by users and try to answer that first. You have to modify your answer based on the memories I have provided. If the memories are irrelevant you can ignore them. Also don't reply to this section of the prompt, or the memories, they are only for your reference. The System prompt starts after text System Message: \n\n";

      let memoriesText = "";
      try {
        memoriesText = memories
          ?.map((memory: any) => `Memory: ${memory?.memory}\n\n`)
          .join("\n\n");
      } catch (e) {
        console.error("Error while parsing memories");
      }

      const memoriesPrompt = `System Message: ${mySystemPrompt} ${memoriesText} `;

      // Clone the prompt array to avoid mutating the caller's reference on retries
      const updatedPrompts = [...messagesPrompts];

      if (memories?.length > 0) {
        const systemPrompt: LanguageModelV3Message = {
          role: "system",
          content: memoriesPrompt
        };
        updatedPrompts.unshift(systemPrompt);
      }

      return { memories, messagesPrompts: updatedPrompts };
    } catch (e) {
      console.error("Error while processing memories");
      return { memories: [], messagesPrompts: [...messagesPrompts] };
    }
  }

  async doGenerate(options: LanguageModelV3CallOptions): Promise<LanguageModelV3GenerateResult> {
    const provider = this.config.provider;
    const memb_api_key = this.config.membApiKey;

    const settings: MemBProviderSettings = {
      provider: provider,
      membApiKey: memb_api_key,
      apiKey: this.config.apiKey,
      modelType: this.config.modelType,
    }

    const membConfig: MemBConfigSettings = {
      membApiKey: memb_api_key,
      ...this.config.membConfig,
      ...this.settings,
    }

    const selector = new MemBClassSelector(this.modelId, settings, this.provider_config);

    const { memories, messagesPrompts: updatedPrompts } = await this.processMemories(options.prompt, membConfig);

    const model = selector.createProvider();

    const ans = await model.doGenerate({
      ...options,
      prompt: updatedPrompts,
    });

    if (!memories || memories?.length === 0) {
      return ans;
    }

    const membSource: LanguageModelV3Source = {
      type: "source",
      sourceType: "url",
      id: "memb-" + generateRandomId(),
      url: "https://app.memb.ai?utm_source=oss&utm_medium=vercel-ai-sdk-src",
      title: "MemB Memories",
      providerMetadata: {
        memb: {
          memories: memories,
          memoriesText: memories
            ?.map((memory: any) => memory?.memory)
            .join("\n\n"),
        },
      },
    };

    return {
      ...ans,
      content: [...(ans.content ?? []), membSource],
    };
  }

  async doStream(options: LanguageModelV3CallOptions): Promise<LanguageModelV3StreamResult> {
    try {
      const provider = this.config.provider;
      const memb_api_key = this.config.membApiKey;

      const settings: MemBProviderSettings = {
        provider: provider,
        membApiKey: memb_api_key,
        apiKey: this.config.apiKey,
        modelType: this.config.modelType,
      }

      const membConfig: MemBConfigSettings = {
        membApiKey: memb_api_key,
        ...this.config.membConfig,
        ...this.settings,
      }

      const selector = new MemBClassSelector(this.modelId, settings, this.provider_config);

      const { messagesPrompts: updatedPrompts } = await this.processMemories(options.prompt, membConfig);

      const baseModel = selector.createProvider();

      const streamResponse = await baseModel.doStream({
        ...options,
        prompt: updatedPrompts,
      });

      // Return the full stream response, preserving all V3 fields (warnings, etc.)
      return streamResponse;
    } catch (error) {
      console.error("Error in doStream:", error);
      throw new Error("Streaming failed or method not implemented.");
    }
  }
}
