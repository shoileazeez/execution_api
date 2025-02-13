FROM ruby:3.2-slim

WORKDIR /sandbox

RUN useradd -m sandbox-user
USER sandbox-user

CMD ["irb"]
