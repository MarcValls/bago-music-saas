FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

ENV PYTHONUNBUFFERED=1
ENV PORT=7430

EXPOSE 7430

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7430"]
