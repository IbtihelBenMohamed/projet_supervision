FROM python:3.11

WORKDIR /app

COPY simulator.py .

RUN pip install prometheus_client faker

EXPOSE 8000

CMD ["python", "simulator.py"]