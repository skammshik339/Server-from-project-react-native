# --- ЭТАП 1: Python 3.11 + music21 (без LilyPond) ---
FROM python:3.11-slim-bookworm AS pythonlayer

RUN apt-get update && \
    apt-get install -y \
        wget \
        ghostscript \
        fontconfig \
        fonts-dejavu \
        fonts-dejavu-core \
        fonts-dejavu-extra \
        libfreetype6 \
        libfontconfig1 \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libxft2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# --- ЭТАП 2: Node 20 + Debian 12 + LilyPond ---
FROM node:20-bookworm

RUN apt-get update && \
    apt-get install -y \
        ghostscript \
        fontconfig \
        fonts-dejavu \
        fonts-dejavu-core \
        fonts-dejavu-extra \
        libfreetype6 \
        libfontconfig1 \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libxft2 \
        lilypond \
        guile-2.2-libs \
    && rm -rf /var/lib/apt/lists/*

# Копируем Python 3.11 с пакетами
COPY --from=pythonlayer /usr/local /usr/local

# Привязываем python3/pip3 к Python 3.11
RUN ln -sf /usr/local/bin/python3 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3 /usr/bin/pip3

WORKDIR /app

# Node зависимости
COPY package*.json ./
RUN npm install

# Код проекта
COPY . .

# Сборка
RUN npm run build

# Копируем Python-скрипты
RUN mkdir -p dist/python && cp -r python/* dist/python/

# Папки для файлов
RUN mkdir -p uploads outputs

ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

CMD ["npm", "start"]













