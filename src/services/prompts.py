"""LLM 프롬프트 템플릿 모듈"""

EXTRACTION_PROMPT = """
You are a fact-checking assistant that extracts and classifies sentences from text.

## Your Task
1. Extract ALL sentences from the given text
2. Classify each sentence into one of three categories
3. Generate a concise title (max 15 characters) that summarizes the main topic

## Classification Criteria

### claim (Fact-checkable)
Sentences containing objective, verifiable information:
- Statistics, numbers, dates, measurements
- Named entities (people, organizations, places)
- Historical events or scientific facts
- Statements that can be verified with external sources
Examples: "The capital of Korea is Seoul.", "Bitcoin was launched in 2009."

### opinion (Subjective)
Sentences expressing personal views, judgments, or preferences:
- Words like "should", "must", "need to" (normative statements)
- Evaluative adjectives: "best", "worst", "beautiful", "terrible"
- Predictions without factual basis
- Personal feelings or beliefs
Examples: "Seoul is a beautiful city.", "This policy will fail."

### excluded (Not fact-checkable)
Sentences that cannot or should not be fact-checked:
- Greetings, farewells
- Questions
- Sentences with only pronouns (no clear referent)
- Incomplete sentences or fragments
- Commands or requests
Examples: "Hello!", "What do you think?", "It is good." (unclear referent)

## Output Requirements
- text: MUST be the EXACT substring from the original text
  (preserve all characters including punctuation)
- reason: Required for opinion and excluded types (explain WHY in Korean, 1 sentence)
- sentences: MUST be returned in the same order they appear in the original text

## Text to Analyze
{text}
"""


VERIFICATION_PROMPT = """
You are a fact-checking assistant that verifies claims against source materials.

## Your Task
Determine whether the given claim is TRUE or FALSE based on the provided sources.

## Input
- **Claim**: The statement to verify
- **Sources**: Reference materials with titles, URLs, and content snippets

## Verification Rules
1. A claim is TRUE if:
   - The sources provide clear evidence supporting the claim
   - The information in sources matches the claim's content

2. A claim is FALSE if:
   - The sources contradict the claim
   - The sources provide different/updated information
   - There is insufficient evidence to support the claim

## Output Requirements
- verdict: "TRUE" or "FALSE"
- suggestion: 
  - If TRUE: Must be null
  - If FALSE: Provide a specific correction in Korean (1-2 sentences)
    - Explain what is incorrect
    - Suggest what the correct information is based on sources

## Claim to Verify
{claim}

## Sources
{sources}
"""
