# 1. Login to Docker Hub (if not already logged in)
docker login

# 2. Build the image with the Docker Hub tag
docker build -t akhaladze/iot-homebot:latest .

# 3. Push the image to Docker Hub
docker push akhaladze/iot-homebot:latest


# 4. compose variant
docker compose build && docker compose push &&  docker compose up

# 5. Delete old pod
kubectl delete pod -l app=iot-homebot -n homebot
