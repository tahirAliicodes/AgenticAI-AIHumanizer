# humanizer.py
# Sends each chunk to llama3.1 and gets back humanized text

import ollama


SYSTEM_PROMPT = """You are an expert editor who makes AI-generated text sound 
naturally human. Your rules:
- Keep the EXACT same meaning — never add or remove information
- Use varied sentence lengths — mix short punchy sentences with longer ones
- Avoid robotic phrases like "Furthermore", "Moreover", "It is important to note"
- Sound like a smart human wrote this, not a machine
- Keep headings exactly as they are — do not rewrite headings
- Return ONLY the rewritten text, nothing else. No explanations."""


def humanize_chunk(chunk):
    """Takes one chunk dict, returns it with humanized text added."""

    # Don't humanize headings — keep them exactly as-is
    if chunk["type"] == "heading":
        return chunk

    # Send paragraph to llama3.1
    response = ollama.chat(
        model="llama3.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": chunk["text"]}
        ]
    )

    # Pull the text out of the response
    humanized_text = response["message"]["content"].strip()

    # Return a new chunk with humanized text
    return {
        **chunk,               # keep all original fields (type, style, etc.)
        "humanized": humanized_text
    }


def humanize_all(chunks, progress_callback=None):
    """Humanizes every chunk. Calls progress_callback after each one."""
    results = []

    for i, chunk in enumerate(chunks):
        humanized = humanize_chunk(chunk)
        results.append(humanized)

        # If someone gave us a progress function, call it
        if progress_callback:
            progress_callback(i + 1, len(chunks))

    return results


# ── Quick test ──
if __name__ == "__main__":
    test_chunk = {
        "type": "paragraph",
        "text": "It is important to note that artificial intelligence has furthermore demonstrated remarkable capabilities in various domains of human endeavor."
    }

    print("Original:")
    print(test_chunk["text"])
    print("\nHumanizing... (this takes a few seconds)")

    result = humanize_chunk(test_chunk)

    print("\nHumanized:")
    print(result["humanized"])