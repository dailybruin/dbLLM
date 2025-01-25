FROM node:22.11.0 AS base

WORKDIR /app/frontend

COPY ./frontend/package.json ./package.json

RUN npm i

COPY ./frontend/dist ./dist

COPY ./frontend/.env ./.env

FROM python:3.10

RUN apt-get update && apt-get install -y \
    npm

WORKDIR /app

COPY --from=base /app/frontend /app/frontend

COPY ./backend/modules /app/backend/modules

COPY ./backend/app.py /app/backend/app.py

COPY ./backend/.env /app/backend/.env

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

WORKDIR /app

EXPOSE 5001 4173

CMD ["sh", "-c", "cd /app/backend && pip install 'pinecone-client[grpc]' && python3 app.py & cd /app/frontend && npm run dev"]
#CMD ["sh", "-c", "cd /app/backend && python3 app.py & cd /app/frontend && npm run dev"]