cd frontend
npm run build
cd ..
docker compose build
docker push registry.digitalocean.com/dailybruin/dbllm-frontend:latest
docker push registry.digitalocean.com/dailybruin/dbllm-backend:latest

echo "Registry updated"