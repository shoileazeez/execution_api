FROM golang:1.20-slim

WORKDIR /sandbox

RUN useradd -m sandbox-user
USER sandbox-user

CMD ["go", "run"]
