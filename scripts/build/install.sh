# install package requirements
python3.8 -m pip install -r "$(git rev-parse --show-toplevel)/requirements.txt" && \
# install test and build dependencies
python3.8 -m pip install -r "$(git rev-parse --show-toplevel)/requirements-dev.txt" && \
# install apt dependencies
sudo apt-get install -y ffmpeg
