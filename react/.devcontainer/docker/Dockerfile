FROM node:18
WORKDIR /frontend/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
EXPOSE 3000
CMD ["npm", "start"]

