# runs a containerized install/build/test
. $(git rev-parse --show-toplevel)/scripts/ensure-toplevel.sh && \

docker build . --file scripts/build/Dockerfile --tag duckbot-test:latest

docker rmi duckbot-test:latest
