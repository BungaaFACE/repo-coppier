FROM python:slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "repo-coppier.py"]
