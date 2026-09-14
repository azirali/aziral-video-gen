# Hugging Face Spaces image for aziral-video-gen (Docker SDK, port 7860).
#
# Differences from the root Dockerfile: no Chinese package mirrors, deps come
# from pyproject.toml (no g4f), runs as the non-root uid 1000 that Spaces
# expect, and config.toml is generated from Space secrets on start.
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git imagemagick ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    # moviepy renders subtitles through ImageMagick; allow the @file syntax it uses
    && sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml

RUN useradd -m -u 1000 user
WORKDIR /app

COPY pyproject.toml ./
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))" > /tmp/requirements.txt \
    && pip install -r /tmp/requirements.txt

COPY --chown=user:user . .
RUN chmod +x deploy/huggingface/entrypoint.sh

USER user
ENV PYTHONPATH=/app \
    HOME=/home/user \
    HF_HOME=/tmp/hf \
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 7860
CMD ["deploy/huggingface/entrypoint.sh"]
