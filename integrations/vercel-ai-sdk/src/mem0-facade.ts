import { withoutTrailingSlash } from '@ai-sdk/provider-utils'

import { MemBGenericLanguageModel } from './memb-generic-language-model'
import { MemBChatModelId, MemBChatSettings } from './memb-types'
import { MemBProviderSettings } from './memb-provider'

export class MemB {
  readonly baseURL: string
  readonly headers?: any

  constructor(options: MemBProviderSettings = {
    provider: 'openai',
  }) {
    this.baseURL =
      withoutTrailingSlash(options.baseURL) ?? 'https://api.openai.com'

    this.headers = options.headers
  }

  private get baseConfig() {
    return {
      baseURL: this.baseURL,
      headers: this.headers,
    }
  }

  chat(modelId: MemBChatModelId, settings: MemBChatSettings = {}) {
    return new MemBGenericLanguageModel(modelId, settings, {
      provider: 'openai',
      modelType: 'chat',
      ...this.baseConfig,
    })
  }

  completion(modelId: MemBChatModelId, settings: MemBChatSettings = {}) {
    return new MemBGenericLanguageModel(modelId, settings, {
      provider: 'openai',
      modelType: 'completion',
      ...this.baseConfig,
    })
  }
}