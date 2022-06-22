FROM python:3.9

RUN pip install fastapi uvicorn spacy

COPY ./api /api/api

ENV PYTHONPATH=/api

WORKDIR /api

EXPOSE 8000:8000


ENTRYPOINT ["uvicorn"]

CMD ["model_api:app, "--host", "0.0.0.0", "--port", "8000"]
