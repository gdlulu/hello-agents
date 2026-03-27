FROM python:3.10-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    curl \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.torch.txt ./

RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements.torch.txt && \
    pip check

CMD ["sleep", "infinity"]