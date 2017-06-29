FROM alpine:3.6

LABEL maintainer "jeff.n.may@gmail.com"

WORKDIR /usr/src/app

COPY stage .

RUN apk add --no-cache \
        build-base \
        mariadb-dev \
        python3 \
        py-pip \
        python3-dev \
        uwsgi-python3

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV FLASK_APP "flask_app.py"

ENTRYPOINT ["uwsgi", \
            "--plugins-dir", "/usr/lib/uwsgi/", \
            "--need-plugin", "python3", \
            "--socket", "0.0.0.0:8080", \
            "--protocol=http", \
            "--manage-script-name", "--mount", "/=flask_app:app"]

