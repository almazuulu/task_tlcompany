FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

# Устанавливаем supervisor для запуска нескольких програм 
RUN apt-get update && apt-get install -y supervisor

# Копируем конфигурацию supervisor в контейнер
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Команда для запуска supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
