#!/bin/bash
# Nexus Vlog Agent - Cloud Run Deployment Script

PROJECT_ID="woven-mapper-489504-u7"
SERVICE_NAME="nexus-agent"
REGION="us-central1"

echo "==========================================="
echo " Deploying Nexus Agent to Google Cloud Run"
echo " Project: $PROJECT_ID"
echo " Service: $SERVICE_NAME"
echo "==========================================="

# Note: Before running, ensure you have ran `gcloud auth login` and `gcloud config set project $PROJECT_ID`

echo "[1/2] Submitting build to Google Container Registry..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

echo "[2/2] Deploying image to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,GCP_LOCATION=$REGION

echo "==========================================="
echo " Deployment Complete!"
echo "==========================================="
