# --- ЭТАП 1: Python 3.11 + music21 + LilyPond ---
FROM python:3.11-slim AS pythonlayer

# Устанавливаем системные зависимости
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

# Устанавливаем Python зависимости
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# --- ЭТАП 2: Node 20 + твой сервер ---
FROM node:20-bullseye

# Копируем Python из первого слоя
COPY --from=pythonlayer /usr/local /usr/local
COPY --from=pythonlayer /usr/bin/lilypond /usr/bin/lilypond

# Рабочая директория
WORKDIR /app

# Node зависимости
COPY package*.json ./
RUN npm install

# Копируем проект
COPY . .

# Сборка TypeScript
RUN npm run build

# Копируем Python скрипты в dist
RUN mkdir -p dist/python && cp -r python/* dist/python/

# Папки
RUN mkdir -p uploads outputs

# Переменные окружения
ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

CMD ["npm", "start"]






