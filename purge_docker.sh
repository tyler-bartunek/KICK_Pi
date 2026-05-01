IMAGE_NAME="kickbot"
CONTAINER_NAME="Footlocker"
WORKSPACE="/home/tyler/Documents/ShoeBot_Pi/sros_ws"

# Check if container already exists and remove it if so
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Removing existing container..."
    docker stop $CONTAINER_NAME 2>/dev/null
    docker rm $CONTAINER_NAME
fi

# Check if image exists, destroy if it does
    if [ -z "$(docker images -q $IMAGE_NAME)" ]; then
        echo "Image $IMAGE_NAME not found."
    else
        echo "Image $IMAGE_NAME found, destroying..."
        docker rmi $IMAGE_NAME
    fi