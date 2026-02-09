FROM python:3.11-slim

WORKDIR /app

COPY homebot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
# Добавляем --chdir homebot
CMD ["gunicorn", "--chdir", "homebot", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

# CMD ["python", "app.py"]