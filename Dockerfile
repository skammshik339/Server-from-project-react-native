FROM node:20-bookworm

# --- Force rebuild marker (обновляй число при каждом деплое) ---
ARG REBUILD=1

# --- System deps ---
RUN apt-get update && apt-get install -y \
    wget \
    ghostscript \
    fontconfig \
    libfreetype6 \
    libfontconfig1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# --- Install LilyPond 2.24.4 ---
RUN wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.4/downloads/lilypond-2.24.4-linux-x86_64.tar.gz \
    && tar -xzf lilypond-2.24.4-linux-x86_64.tar.gz \
    && mv lilypond-2.24.4 /opt/lilypond \
    && ln -s /opt/lilypond/bin/lilypond /usr/bin/lilypond

# --- Python virtual environment ---
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# --- Force rebuild pip layer ---
COPY requirements.txt /tmp/requirements.txt
RUN echo "FORCE REBUILD $REBUILD" \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# --- Node app ---
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# Python scripts
RUN mkdir -p dist/python && cp -r python/* dist/python/
RUN mkdir -p uploads outputs

ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

CMD ["npm", "start"]


















