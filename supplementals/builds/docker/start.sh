echo "Start script: $1"

if [ "$(uname)" == "Darwin" ]; then
    echo "Detected OS: macos"
    export DISPLAY=docker.for.mac.host.internal:0
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    echo "Detected OS: linux"        
    export DISPLAY=:0
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    echo "Detected OS: macos"        
    echo "Not implemented"
    exit 1      
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    echo "Detected OS: macos"        
    echo "Not implemented"        
    exit 1    
else
    echo "Detected OS: --"        
    echo "Not implemented"        
    exit 1    
fi

docker compose -f supplementals/builds/docker/docker-compose.yml build --build-arg=START_SCRIPT=$1

docker compose -f supplementals/builds/docker/docker-compose.yml up
