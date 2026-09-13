FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock && useradd --create-home app
COPY . .
RUN mkdir -p /app/data && chown app:app /app/data
USER app
ENV PAUSEWELL_HOST=0.0.0.0
EXPOSE 8765
CMD ["python", "scripts/serve.py"]
