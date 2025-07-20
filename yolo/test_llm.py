from llm_handler import generate_collision_explanation, speak_text, get_voice_command

explanation = generate_collision_explanation(50, 35, 10, 0.76)
print("[LLM] 🔎", explanation)
speak_text(explanation)

print("[VOICE] Now ask something:")
cmd = get_voice_command()
speak_text(f"You said: {cmd}")
