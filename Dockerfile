FROM node:20-bullseye

RUN apt-get update && \
    apt-get install -y \
        python3 python3-pip \
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

RUN wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.3/downloads/lilypond-2.24.3-linux-x86_64.tar.gz && \
    tar -xzf lilypond-2.24.3-linux-x86_64.tar.gz && \
    mv lilypond-2.24.3 /usr/local/lilypond && \
    ln -s /usr/local/lilypond/bin/lilypond /usr/bin/lilypond && \
    rm lilypond-2.24.3-linux-x86_64.tar.gz

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





