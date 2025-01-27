FROM node:22.11.0 AS base

RUN apt-get update && apt-get install -y \
    yarn

WORKDIR /frontend

COPY ./package.json .

COPY ./node_modules ./node_modules

COPY ./vite.config.ts .

RUN yarn install

COPY ./dist ./dist

COPY ./.env .

EXPOSE 4173

CMD ["yarn", "preview"]