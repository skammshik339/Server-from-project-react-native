FROM node:20-bookworm

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
    && rm -rf /var/lib/apt/lists/*

# --- Install LilyPond 2.24.4 ---
RUN wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.4/downloads/lilypond-2.24.4-linux-x86_64.tar.gz \
    && tar -xzf lilypond-2.24.4-linux-x86_64.tar.gz \
    && mv lilypond-2.24.4 /opt/lilypond \
    && ln -s /opt/lilypond/bin/lilypond /usr/bin/lilypond

# --- Python deps ---
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

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
















