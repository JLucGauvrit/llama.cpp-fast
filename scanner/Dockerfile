FROM python:3.13-slim
WORKDIR /app
COPY scan_specs.py /app/
RUN pip install psutil GPUtil
CMD ["python","scan_specs.py"]
