FROM python:slim

RUN apt update && apt install -y git

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "repo-coppier.py", "sync"]
