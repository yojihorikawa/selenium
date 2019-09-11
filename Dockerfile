FROM node:10.13.0-alpine

# node.js の環境変数を定義する
# 本番環境では production
ENV NODE_ENV=development

# 雛形を生成するのに必要なパッケージのインストール
RUN apk add --update alpine-sdk



#pythonインストール
RUN apk add --update \
    build-base

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi

RUN apk add --update python3-dev build-base jpeg-dev zlib-dev freetype-dev libjpeg-turbo-dev libpng-dev

#chromeインストール
RUN apk add --update \
            udev \
            ttf-freefont \
            chromium \
            openssl \
            chromium-chromedriver \
            gfortran \
            gcc \
            g++

# 日本語フォント追加（wordcloud文字化け対応）
RUN apk update \
  && apk add --no-cache curl fontconfig \
  && curl -O https://noto-website.storage.googleapis.com/pkgs/NotoSansCJKjp-hinted.zip \
  && mkdir -p /usr/share/fonts/NotoSansCJKjp \
  && unzip NotoSansCJKjp-hinted.zip -d /usr/share/fonts/NotoSansCJKjp/ \
  && rm NotoSansCJKjp-hinted.zip \
  && fc-cache -fv

RUN pip install Pillow

ENV LIBRARY_PATH=/lib:/usr/lib


RUN git config --global url."https://".insteadOf git://

# ディレクトリを作成
WORKDIR /src

# ポート3000番を開放する
EXPOSE 3009
