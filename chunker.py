# chunker.py
# Reads a document and splits it into smart chunks

from docx import Document  # reads .docx files


def chunk_txt(filepath):
    """Split a plain text file into paragraphs."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    # Split on blank lines — each block = one chunk
    blocks = raw.split("\n\n")

    chunks = []
    for block in blocks:
        block = block.strip()
        if block:  # skip empty blocks
            chunks.append({
                "type": "paragraph",
                "text": block
            })

    return chunks


def chunk_docx(filepath):
    """Split a .docx file into paragraphs, tagging headings separately."""
    doc = Document(filepath)
    chunks = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue  # skip blank lines

        # Detect if this paragraph is a heading
        if para.style.name.startswith("Heading"):
            chunks.append({
                "type": "heading",
                "style": para.style.name,  # e.g. "Heading 1", "Heading 2"
                "text": text
            })
        else:
            chunks.append({
                "type": "paragraph",
                "text": text
            })

    return chunks


def chunk_document(filepath):
    """Main function — detects file type and chunks accordingly."""
    if filepath.endswith(".txt"):
        return chunk_txt(filepath)
    elif filepath.endswith(".docx"):
        return chunk_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")


# ── Quick test (only runs when you run this file directly) ──
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python chunker.py yourfile.txt")
    else:
        chunks = chunk_document(sys.argv[1])
        print(f"Found {len(chunks)} chunks:\n")
        for i, chunk in enumerate(chunks):
            print(f"[{i+1}] ({chunk['type']}) {chunk['text'][:60]}...")