FROM node:20-bullseye

RUN apt-get update && \
    apt-get install -y \
        python3 python3-pip lilypond \
        ghostscript \
        fontconfig \
        libfreetype6 \
        libfontconfig1 \
        libx11-6 \
        libxext6 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

RUN npm run build

RUN mkdir -p dist/python && cp -r python/* dist/python/

RUN mkdir -p uploads outputs

ENV PORT=3000
ENV LILYPOND_PATH=/usr/bin/lilypond

CMD ["npm", "start"]



