from gemini_engine import gemini_package_available, gemini_available, gemini_status, ask_gemini
assert gemini_package_available() is True
assert gemini_available('') is False
assert 'key not configured' in gemini_status('')
assert ask_gemini('test', {}) is None
print('gemini_runtime_validation_ok')
