# --- ЭТАП 1: Python 3.11 + music21 + LilyPond ---
FROM python:3.11-slim AS pythonlayer

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

# Устанавливаем LilyPond 2.24.3
RUN wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.3/downloads/lilypond-2.24.3-linux-x86_64.tar.gz && \
    tar -xzf lilypond-2.24.3-linux-x86_64.tar.gz && \
    mv lilypond-2.24.3 /usr/local/lilypond && \
    ln -s /usr/local/lilypond/bin/lilypond /usr/bin/lilypond && \
    rm lilypond-2.24.3-linux-x86_64.tar.gz

# Python зависимости
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# --- ЭТАП 2: Node 20 + перенос Python 3.11 ---
FROM node:20-bullseye

# Копируем Python 3.11 полностью
COPY --from=pythonlayer /usr/local /usr/local
COPY --from=pythonlayer /usr/bin/lilypond /usr/bin/lilypond

# Устанавливаем python3 → указываем на Python 3.11
RUN ln -sf /usr/local/bin/python3 /usr/bin/python3
RUN ln -sf /usr/local/bin/pip3 /usr/bin/pip3

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

RUN mkdir -p dist/python && cp -r python/* dist/python/

RUN mkdir -p uploads outputs

ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

CMD ["npm", "start"]







