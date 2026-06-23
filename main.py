# main.py
# FastAPI server — ties everything together

import os
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import json

from chunker import chunk_document
from humanizer import humanize_all
from assembler import assemble_document
from db import init_db

app = FastAPI()

init_db()  # creates the 'jobs' table if it doesn't exist yet (runs once on startup)

# Folders for uploaded and output files
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serve static files (our index.html UI)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_ui():
    """Serve the main UI page."""
    return FileResponse("static/index.html")


@app.post("/humanize")
async def humanize_endpoint(file: UploadFile = File(...)):
    """
    Main endpoint:
    1. Save uploaded file
    2. Chunk it
    3. Humanize each chunk (streaming progress)
    4. Assemble output file
    5. Stream progress events back to browser
    """

    # Save uploaded file with a unique name to avoid clashes
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    upload_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(upload_path, "wb") as f:
        f.write(await file.read())

    def event_stream():
        try:
            # Step 1: Chunk the document
            yield f"data: {json.dumps({'status': 'chunking', 'message': 'Reading document...'})}\n\n"
            chunks = chunk_document(upload_path)
            total = len(chunks)
            yield f"data: {json.dumps({'status': 'chunked', 'total': total, 'message': f'Found {total} chunks'})}\n\n"

            # Step 2: Humanize each chunk with progress updates
            humanized_chunks = []
            for i, chunk in enumerate(chunks):
                from humanizer import humanize_chunk
                result = humanize_chunk(chunk)
                humanized_chunks.append(result)

                # Send progress to browser after each chunk
                yield f"data: {json.dumps({'status': 'progress', 'current': i+1, 'total': total, 'message': f'Humanizing chunk {i+1} of {total}...'})}\n\n"

            # Step 3: Assemble the output file
            yield f"data: {json.dumps({'status': 'assembling', 'message': 'Assembling document...'})}\n\n"
            output_path = assemble_document(humanized_chunks, upload_path, OUTPUT_DIR, original_filename=file.filename)
            output_filename = os.path.basename(output_path)

            # Step 4: Done — send download filename to browser
            yield f"data: {json.dumps({'status': 'done', 'filename': output_filename, 'message': 'Done!'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/download/{filename}")
def download_file(filename: str):
    """Serve the humanized file for download."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, filename=filename)