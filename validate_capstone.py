from disaster_agent import classify_disaster_question
from gemini_engine import gemini_available, SYSTEM_PROMPT

intent = classify_disaster_question('Assam mein baadh aayi hai?')
print('intent=', intent)
print('prompt_check=', 'Never infer or invent deaths' in SYSTEM_PROMPT)
assert intent.domain == 'flood'
assert 'Never infer' in SYSTEM_PROMPT and 'or invent deaths' in SYSTEM_PROMPT
print('capstone_backend_validation_ok', gemini_available())
