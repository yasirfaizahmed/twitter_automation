# Agent image: Python + adb. The model is served separately (see deploy/docker-compose.yml).
#   docker build -t android-automation .
#   docker run --rm -it --network host android-automation check
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends adb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY android_automation ./android_automation
RUN python -m pip install --no-cache-dir .
COPY configs ./configs
COPY examples ./examples

ENTRYPOINT ["android-automation"]
CMD ["--help"]
