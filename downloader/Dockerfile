FROM python:3.13-slim
WORKDIR /app
COPY download_model.py /app/
RUN pip install huggingface_hub transformers
CMD ["python","/app/download_model.py"]
