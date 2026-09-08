name=services/bandari-engine/Dockerfile
# Bandari Engine Dockerfile (Node)
FROM node:18-alpine
WORKDIR /app
COPY bandari-engine-2026/current/package.json ./
RUN npm ci --silent
COPY bandari-engine-2026/current/ ./
EXPOSE 3000
CMD ["node", "index.js"]