FROM python:3.8-slim

RUN pip3 install virtualenv pipenv

RUN useradd -ms /bin/bash stonks
USER stonks
WORKDIR /home/stonks

ENV VIRTUAL_ENV=/home/stonks/venv
RUN virtualenv -p python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY Pipfile* ./
RUN pipenv lock --keep-outdated --requirements > requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ARG FASTAPI_DEBUG=False
ENV FASTAPI_DEBUG="${FASTAPI_DEBUG}"

ARG FASTAPI_HOST=0.0.0.0
ENV FASTAPI_HOST="${FASTAPI_HOST}"

ARG CORS_DOMAIN=http://localhost
ENV CORS_DOMAIN="${CORS_DOMAIN}"

ADD . /home/streamio2/

ENTRYPOINT ["python", "run.py"]
