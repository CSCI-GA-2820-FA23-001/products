# Build it in the root path of this repo

FROM python:3.11-slim

# Create working folder and install dependencies
WORKDIR /app
COPY k8s/requirements.txt .
RUN pip install -U pip wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application contents
COPY service /app/service/

# Switch to a non-root user
RUN useradd --uid 1001 flask && chown -R flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV FLASK_APP=service:app
ENV PORT 8000
EXPOSE $PORT

CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]