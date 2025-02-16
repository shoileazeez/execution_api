FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements.txt FIRST
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies (if needed for your Python packages)
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-dev \
    libpq-dev \
    build-essential \
    libffi-dev \
    zlib1g-dev \
    curl \
    gnupg \
    default-jdk \              
    ruby-full \                
    g++ \  
    nodejs \
    npm \
    golang \
    php-cli \
    php-mbstring \
    php-xml \
    php-curl \
    php-zip \
    rustc \
    cargo \
    kotlin \
    r-base \
    perl \
    lua5.3 \   
    erlang \
    elixir \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install JSON dependencies
# JavaScript & TypeScript
RUN npm install -g ts-node typescript node-fetch typescript-json

# Java (JSON handling)
RUN curl -L https://repo1.maven.org/maven2/org/json/json/20230227/json-20230227.jar -o /usr/share/java/json.jar

# C & C++
RUN apt-get update && apt-get install -y libjson-c-dev

# Ruby
RUN gem install json

# Go
RUN go env -w GO111MODULE=on \
    && go install github.com/tidwall/gjson@latest


# PHP (Composer & JSON)
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer require nesbot/carbon

# Rust
RUN cargo install serde_json

# Kotlin (JSON parsing)
RUN mkdir -p /usr/share/kotlin-libs && curl -L https://repo1.maven.org/maven2/org/json/json/20230227/json-20230227.jar -o /usr/share/kotlin-libs/json.jar

# R
RUN R -e "install.packages('jsonlite', repos='http://cran.r-project.org')"

# Perl
RUN cpan JSON

# Lua
RUN apt-get install -y luarocks && luarocks install lua-cjson

# Erlang
RUN apt-get install -y erlang-xmerl && git clone https://github.com/talentdeficit/jsx.git && cd jsx && make && make install

# Elixir
RUN mix local.hex --force && mix local.rebar --force && mix archive.install hex phx_new --force && mix deps.get && mix deps.compile

# Install Yarn (optional, if needed for Node.js projects)
RUN npm install --global yarn

# Install Ruby Gems (if your Ruby scripts need any)
RUN gem install bundler

# Copy the rest of your Django project (AFTER installing npm dependencies)
COPY . .

# Create a non-root user and set it as the owner of the working directory
RUN adduser --disabled-password --gecos '' celeryuser \
    && chown -R celeryuser:celeryuser /app

# Switch to the celeryuser to avoid running as root
USER celeryuser

# Expose port
EXPOSE 8000

# Command to run Celery worker and Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput  & gunicorn sandbox_project.wsgi:application --bind 0.0.0.0:$PORT"]
