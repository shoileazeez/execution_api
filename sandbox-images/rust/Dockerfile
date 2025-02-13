FROM rust:1.72-slim

WORKDIR /sandbox

RUN useradd -m sandbox-user
USER sandbox-user

CMD ["cargo", "run"]
