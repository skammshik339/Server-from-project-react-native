# --- ЭТАП 1: Python 3.11 + music21 + LilyPond 2.22.2 ---
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

# Устанавливаем LilyPond 2.22.2 (стабильная версия)
RUN wget https://lilypond.org/download/binaries/linux-64/lilypond-2.22.2-linux-x86_64.tar.gz && \
    tar -xzf lilypond-2.22.2-linux-x86_64.tar.gz && \
    mv lilypond-2.22.2 /usr/local/lilypond && \
    ln -s /usr/local/lilypond/bin/lilypond /usr/bin/lilypond && \
    rm lilypond-2.22.2-linux-x86_64.tar.gz

# Python-зависимости
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# --- ЭТАП 2: Node 20 + Debian 12 (bookworm) ---
FROM node:20-bookworm

# Копируем Python 3.11 и LilyPond из первого слоя
COPY --from=pythonlayer /usr/local /usr/local
COPY --from=pythonlayer /usr/bin/lilypond /usr/bin/lilypond

# Делаем /usr/bin/python3 и /usr/bin/pip3 ссылками на Python 3.11
RUN ln -sf /usr/local/bin/python3 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3 /usr/bin/pip3

WORKDIR /app

# Node-зависимости
COPY package*.json ./
RUN npm install

# Код проекта
COPY . .

# Сборка
RUN npm run build

# Копируем Python-скрипты в dist
RUN mkdir -p dist/python && cp -r python/* dist/python/

# Папки для файлов
RUN mkdir -p uploads outputs

ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

CMD ["npm", "start"]










