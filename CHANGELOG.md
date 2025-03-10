# Changelog

## [0.1.1](https://github.com/googleapis/genai-toolbox-langchain-python/compare/v0.1.0...v0.1.1) (2025-03-10)


### Bug Fixes

* Add items to parameter schema ([#62](https://github.com/googleapis/genai-toolbox-langchain-python/issues/62)) ([d77eb7c](https://github.com/googleapis/genai-toolbox-langchain-python/commit/d77eb7c4ccf604ea8449a784d6ba4d8b4ad1ac96))
* **deps:** Update dependency black to v25 ([#47](https://github.com/googleapis/genai-toolbox-langchain-python/issues/47)) ([451c0b1](https://github.com/googleapis/genai-toolbox-langchain-python/commit/451c0b18287fa003b3e10e531b45a82b16ea0c5b))
* **deps:** Update dependency google-cloud-storage to v3 ([#48](https://github.com/googleapis/genai-toolbox-langchain-python/issues/48)) ([ecdecb7](https://github.com/googleapis/genai-toolbox-langchain-python/commit/ecdecb7921354cd1fc98e04d5133c262b958d0c4))
* **deps:** Update dependency isort to v6 ([#49](https://github.com/googleapis/genai-toolbox-langchain-python/issues/49)) ([313f6d3](https://github.com/googleapis/genai-toolbox-langchain-python/commit/313f6d3e3df0728530f106005d5e5bd49f3be519))
* **deps:** Update dependency pillow to v11 ([#50](https://github.com/googleapis/genai-toolbox-langchain-python/issues/50)) ([955fd41](https://github.com/googleapis/genai-toolbox-langchain-python/commit/955fd41e32d0d33280640ba5bf974e284e427f95))
* **deps:** Update python-nonmajor ([#30](https://github.com/googleapis/genai-toolbox-langchain-python/issues/30)) ([93240a2](https://github.com/googleapis/genai-toolbox-langchain-python/commit/93240a2de5e5ef7f98ecf9b7de81b31b2104d5e4))
* **langchain-sdk:** Fix issue occurring when using a tool with list type. ([#33](https://github.com/googleapis/genai-toolbox-langchain-python/issues/33)) ([9c4f0d1](https://github.com/googleapis/genai-toolbox-langchain-python/commit/9c4f0d102e9d399437e67152e906a76d9d632757))

## 0.1.0 (2025-02-05)


### ⚠ BREAKING CHANGES

* Improve PyPI package name
* Migrate existing state and APIs to a tools level class
* deprecate 'add_auth_headers' in favor of 'add_auth_tokens' 

### Features

* Add support for sync operations ([9885469](https://github.com/googleapis/genai-toolbox-langchain-python/commit/9885469703d88afc7c7aed10c85e97c099d7e532))
*Add features for binding parameters to ToolboxTool class. ([4fcfc35](https://github.com/googleapis/genai-toolbox-langchain-python/commit/4fcfc3549038c52c495d452f36037817a30eed2e))
*Add Toolbox SDK for LangChain ([d4a24e6](https://github.com/googleapis/genai-toolbox-langchain-python/commit/d4a24e66139cb985d7457d9162766ce564c36656))
* Correctly parse Manifest API response as JSON ([86bcf1c](https://github.com/googleapis/genai-toolbox-langchain-python/commit/86bcf1c4db65aa5214f4db280d55cfc23edac361))
* Migrate existing state and APIs to a tools level class. ([6fe2e39](https://github.com/googleapis/genai-toolbox-langchain-python/commit/6fe2e39eb16eeeeaedea0a31fc2125b105d633b4))
* Support authentication in LangChain Toolbox SDK. ([b28bdb5](https://github.com/googleapis/genai-toolbox-langchain-python/commit/b28bdb5b12cdfe3fe6768345c00a65a65d91b81b))
* Implement OAuth support for LlamaIndex. ([dc47da9](https://github.com/googleapis/genai-toolbox-langchain-python/commit/dc47da9282af876939f60d6b24e5a9cf3bf75dfd))
* Make ClientSession optional when initializing ToolboxClient ([956591d](https://github.com/googleapis/genai-toolbox-langchain-python/commit/956591d1da69495df3f602fd9e5fd967bd7ea5ca))


### Bug Fixes

* Deprecate 'add_auth_headers' in favor of 'add_auth_tokens' ([c5c699c](https://github.com/googleapis/genai-toolbox-langchain-python/commit/c5c699cc29bcc0708a31bff90e8cec489982fe2a))
