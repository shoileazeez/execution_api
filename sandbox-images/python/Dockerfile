FROM python:3.10-slim

WORKDIR /sandbox

RUN apt-get update && apt-get install -y gcc

RUN useradd -m sandbox-user
USER sandbox-user

CMD ["python3"]
