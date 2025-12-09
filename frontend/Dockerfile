FROM node:22.21-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
RUN npm install -g serve
EXPOSE 8080
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]