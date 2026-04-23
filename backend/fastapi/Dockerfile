FROM python:3.12-slim

WORKDIR /app

ARG REQS_FILE=requirements.txt
COPY ${REQS_FILE} ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts

# Ensure the app directory is treatable as a package
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
