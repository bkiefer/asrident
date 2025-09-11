git pull --recurse-submodules
git submodule update --init --recursive --remote
docker build -f Dockerfile -t asrident .
