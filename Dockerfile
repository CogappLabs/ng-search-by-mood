FROM python:3.10-slim

WORKDIR /app

# CPU-only torch build - the default PyPI wheel bundles CUDA support, which
# is much larger and unnecessary since Cloud Run has no GPU
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.14.1 torchvision==0.29.2 \
      --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# bake the CLIP model weights into the image at build time, so a cold start
# never needs to reach out to the network to fetch them
RUN python -c "import open_clip; open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')"

# application code - common.py deliberately excluded: it's only used by the
# local precompute scripts (which need the National Gallery hack API's
# credentials), not by the deployed search API itself
COPY clip_rank.py vad_rank.py description_rank.py vad_lexicon.py rrf_search.py app.py ./
COPY docs/ docs/

# only the data the API actually reads at request time - not the ~2500
# downloaded painting images (the frontend loads those straight from the
# National Gallery's own IIIF CDN instead) and not the lexicon's zip/PDFs
COPY data/paintings_raw.jsonl data/paintings_raw.jsonl
COPY data/colour_vad.parquet data/colour_vad.parquet
COPY data/description_vad.parquet data/description_vad.parquet
COPY data/clip_embeddings.npy data/clip_embeddings.npy
COPY data/clip_uids.json data/clip_uids.json
COPY data/lexicons/nrc-vad-v2.1/NRC-VAD-Lexicon-v2.1/NRC-VAD-Lexicon-v2.1.txt \
     data/lexicons/nrc-vad-v2.1/NRC-VAD-Lexicon-v2.1/NRC-VAD-Lexicon-v2.1.txt

ENV PORT=8080
EXPOSE 8080

# one worker process (so the ~350MB model is only loaded into memory once,
# not duplicated per worker), with a few threads for concurrency across
# simultaneous requests
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 60 app:app"]
