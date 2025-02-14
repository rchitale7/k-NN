FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
ENV PYTHONPATH=/code/app

ENV REQUEST_STORE_MAX_SIZE=1000
ENV REQUEST_STORE_TTL_SECONDS=900
ENV REQUEST_STORE_TYPE='memory'

ENV PENDING_QUEUE_MAX_SIZE=1000
ENV PENDING_QUEUE_MAX_RETRIES=3
ENV PENDING_QUEUE_RETRY_DELAY_SECONDS=120

ENV GPU_MEMORY_LIMIT=15.5
ENV CPU_MEMORY_LIMIT=20.5

ENV MAX_WORKERS=5

ENV SERVICE_NAME='remote-vector-index-builder'

CMD ["fastapi", "run", "app/main.py", "--port", "80"]