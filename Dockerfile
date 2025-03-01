FROM python:3.12-slim

ENV PYTHONUNBUFFERED True
ENV PYTHONPATH "${PYTHONPATH}:/"

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install dependencies
RUN python -m pip install --no-cache-dir --upgrade --root-user-action=ignore pip \
    && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Start the application
CMD exec hypercorn --bind :${PORT:-8000} --workers 2 --worker-class uvloop app.main:app