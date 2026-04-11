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

# Переменные окружения
ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

# Создаём папки
RUN mkdir -p uploads outputs

# Запуск сервера
CMD ["npm", "start"]

