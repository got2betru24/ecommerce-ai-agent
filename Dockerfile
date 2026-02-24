################# FRONTEND STAGES ##################

###################################################
# Stage: frontend-base
###################################################
FROM node:22-alpine AS frontend-base
WORKDIR /app/frontend

# COPY frontend/package.json frontend/package-lock.json ./
# RUN npm install
# COPY frontend/.eslintrc.cjs frontend/index.html frontend/vite.config.js ./
# COPY frontend/public ./public
# COPY frontend/src ./src

###################################################
# Stage: frontend-dev
###################################################
FROM frontend-base AS frontend-dev
EXPOSE 5173
CMD ["sh", "-c", "npm install && npm run dev -- --host"]


################# BACKEND STAGES ##################

###################################################
# Stage: backend-base
###################################################
FROM python:3.13-slim AS backend-base
WORKDIR /app/backend

###################################################
# Stage: backend-dev
###################################################
FROM backend-base AS backend-dev
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# main:app because main.py lives directly in backend/app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]