FROM node:16-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

# No COPY user_code.js here! It's created at runtime.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1
CMD ["node"] # Just start the node interpreter