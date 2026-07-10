import { MemBProviderSettings } from "./memb-provider";
import MemBAITextGenerator, { ProviderSettings } from "./provider-response-provider";
import { LanguageModelV3 } from '@ai-sdk/provider';

class MemBClassSelector {
    modelId: string;
    provider_wrapper: string;
    config: MemBProviderSettings;
    provider_config?: ProviderSettings;
    static supportedProviders = ["openai", "anthropic", "cohere", "groq", "google", "gemini"];

    constructor(modelId: string, config: MemBProviderSettings, provider_config?: ProviderSettings) {
        this.modelId = modelId;
        this.provider_wrapper = config.provider || "openai";
        this.provider_config = provider_config;
        if(config) this.config = config;
        else this.config = {
            provider: this.provider_wrapper,
        };

        // Check if provider_wrapper is supported
        if (!MemBClassSelector.supportedProviders.includes(this.provider_wrapper)) {
            throw new Error(`Model not supported: ${this.provider_wrapper}`);
        }
    }

    createProvider(): LanguageModelV3 {
        return new MemBAITextGenerator(this.modelId, this.config , this.provider_config || {});
    }
}

export { MemBClassSelector };
