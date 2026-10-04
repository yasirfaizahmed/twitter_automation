# Agent image: the android-automation package, adb, and (optionally) the ADBKeyboard APK.
# The model is served separately (deploy/docker-compose.model.yml). Build and run it with
# deploy/docker-compose.agent.yml, or directly:
#   docker build -t android-automation .
#   docker run --rm -it --privileged -v /dev/bus/usb:/dev/bus/usb android-automation check
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

# Optional dependency groups to install, e.g. "local" for the in-process transformers backend.
ARG EXTRAS=""
# Bundle ADBKeyboard so non-ASCII text (Arabic, Urdu, emoji) can be typed. 0 to skip.
ARG ADBKEYBOARD=1
ARG ADBKEYBOARD_URL=https://raw.githubusercontent.com/senzhk/ADBKeyBoard/d7b27288bc8c1c8348a79ea6896bd7352c30a9fc/ADBKeyboard.apk
ARG ADBKEYBOARD_SHA256=e698adea5633135a067b038f9a0cf41baa4de09888713a81593fb2b9682cdc59

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends adb ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN if [ "$ADBKEYBOARD" = "1" ]; then \
        mkdir -p /opt/adbkeyboard \
        && python -c "import sys, urllib.request; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])" \
            "$ADBKEYBOARD_URL" /opt/adbkeyboard/ADBKeyboard.apk \
        && echo "$ADBKEYBOARD_SHA256  /opt/adbkeyboard/ADBKeyboard.apk" | sha256sum -c - ; \
    fi

WORKDIR /app

# Dependencies first, so code edits do not reinstall them.
COPY pyproject.toml README.md ./
RUN mkdir android_automation && touch android_automation/__init__.py \
    && pip install ".${EXTRAS:+[$EXTRAS]}" \
    && pip uninstall -y android-automation

COPY android_automation ./android_automation
RUN pip install --no-deps .

COPY configs ./configs
COPY examples ./examples
COPY deploy/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh && mkdir -p /app/runs

ENTRYPOINT ["entrypoint.sh"]
CMD ["--help"]
