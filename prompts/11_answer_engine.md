# Answer Engine

## Objective
Orchestrate prompt construction and call the LLM provider to generate a structured, legally sound answer strictly grounded in the retrieved context.

----------------------------------------------------

## Representative Prompt

```text
Objective: Build the Prompt Builder and Answer Generation module.

Requirements:
- Develop a strict system prompt instructing the LLM to act as a legal analyst.
- Inject the retrieved chunks dynamically into the prompt.
- Force the LLM to output a structured JSON format containing the `answer` and an array of `citations`.
- Implement a provider abstraction supporting Mock LLMs, OpenAI, and Anthropic.
- Validate the generated JSON schema using Pydantic.
```

----------------------------------------------------

## Outcome
- Created the core `answer_engine/` featuring the `PromptBuilder` and `LLMProvider` abstractions.
- Established a robust fallback schema ensuring unpredictable LLM text strings wouldn't crash the UI.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Enforcing JSON output drastically reduces parsing errors. Abstracting the LLM provider allows the enterprise to switch from OpenAI to internal open-source models without altering retrieval logic.
- **Review Steps:** Analyzed the system prompt to ensure strong anti-hallucination guardrails were explicitly commanded ("Do NOT use outside knowledge").
- **Validation Approach:** Ran generations against a Mock Provider to test the Pydantic schema validator against deliberate edge cases.
