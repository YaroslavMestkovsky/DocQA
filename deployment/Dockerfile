# Контейнер с виртуальным окружением проекта.
FROM python:3.11.0
ARG USER_GID

# установка необходимых зависимостей
RUN apt update && apt upgrade -y && apt-get update

# настройка доступа к контейнеру по SSH
RUN apt-get install -y openssh-server sudo
RUN mkdir /var/run/sshd

# установка тессеракта, необходимых языковых пакетов (русский + английский) и дополнительных пакетов для обработки PDF.
RUN apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev \
        tesseract-ocr-rus \
        tesseract-ocr-eng \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -rm -d /home/python-root -s /bin/bash -g root -G sudo -u ${USER_GID} python-root && \
    echo 'python-root:python-root' | chpasswd

COPY pyproject.toml /opt/pyproject.toml
RUN pip install --upgrade pip==25.2 && pip install wheel

# установка основных зависимостей
RUN pip install -e /opt

# Отладка
#CMD ["tail", "-f", "/dev/null"]
