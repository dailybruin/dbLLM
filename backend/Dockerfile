FROM python:3.10

WORKDIR /backend

COPY ./modules ./modules

COPY ./app.py .

COPY ./.env .

RUN pip install --no-cache-dir -q -U \
    google-generativeai \
    google-auth \
    langchain \
    python-dotenv \
    pinecone-client \
    protobuf==5.26.1 \
    beautifulsoup4 \
    flask \
    Flask-Cors

EXPOSE 5001

RUN pip install "pinecone-client[grpc]"

CMD ["python3", "app.py"]