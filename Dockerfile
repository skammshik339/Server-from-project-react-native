FROM node:20-bullseye

# Устанавливаем Python, pip и LilyPond
RUN apt-get update && \
    apt-get install -y python3 python3-pip lilypond && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем Node-зависимости
COPY package*.json ./
RUN npm install

# Устанавливаем Python-зависимости
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Копируем весь проект
COPY . .

# Сборка TypeScript
RUN npm run build

# Копируем Python-скрипты в dist, чтобы Node мог их запускать
RUN mkdir -p dist/python && cp -r python/* dist/python/

# Создаём папки
RUN mkdir -p uploads outputs

# Переменные окружения
ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

# Запуск сервера
CMD ["npm", "start"]


