FROM node:20-bullseye

# --- Устанавливаем Python, LilyPond и ВСЕ нужные шрифты ---
RUN apt-get update && \
    apt-get install -y \
        python3 python3-pip \
        lilypond \
        lilypond-data \
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

# --- Создаём рабочую директорию ---
WORKDIR /app

# --- Устанавливаем Node зависимости ---
COPY package*.json ./
RUN npm install

# --- Устанавливаем Python зависимости ---
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# --- Копируем весь проект ---
COPY . .

# --- Сборка TypeScript ---
RUN npm run build

# --- Копируем Python-скрипты в dist ---
RUN mkdir -p dist/python && cp -r python/* dist/python/

# --- Папки для файлов ---
RUN mkdir -p uploads outputs

# --- Переменные окружения ---
ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

# --- Запуск сервера ---
CMD ["npm", "start"]




