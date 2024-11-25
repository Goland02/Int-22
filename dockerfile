FROM python:3.9-slim
WORKDIR /tests
COPY ./tests /tests
RUN pip install --no-cache-dir -r /tests/requirements.txt
CMD ["pytest", "test.py"]
