FROM python:3.10-slim-bullseye

ENV BUILD_PREFIX=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR ${BUILD_PREFIX}

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt 

COPY . ${BUILD_PREFIX}/

EXPOSE 8090

CMD ["python", "open-api.py"]