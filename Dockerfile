FROM python:3-slim-bullseye

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

RUN apt update && apt upgrade -y \
    && apt install bash gcc make python3-dev -y

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Cleanups
RUN apt --purge remove git gcc make python3-dev -y \
    && apt clean autoclean \
    && apt autoremove -y \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ \
              /tmp/* \
              /var/tmp/* \
              /usr/share/man \
              /usr/share/doc \
              /usr/share/doc-base

COPY mainbot mainbot/

CMD ["python3", "mainbot"]
