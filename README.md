# Minechat client

Lesson 4 in devman's async-python module
Simple TCP clent

## How to use

### With Poetry
```bash
poetry install
poetry run minechat --help
poetry run minechat register --help
poetry run minechat send --help
```

### With Docker

```bash
docker build -t minechat .  # build the image
# read the chat
# ATTENTION: file would be created by root
# trick with parameter -u=`id -u` doesn't help
docker run --rm [-d|-it] -v `pwd`/history:/var/minechat minechat
docker run --rm -it minechat register --help  
docker run --rm -it minechat send --help
```

### No poetry and docker (what a shame)

```bash
pip install aiofiles python-dotenv  # no requirements.txt anymore
export PYTHONPATH=.
python minechat_client/main.py --help
python minechat_client/main.py register --help
python minechat_client/main.py send --help
```

## Settings

Additionally to command line args the next environment variables are supported.

- MINECHAT_HOST
- MINECHAT_LISTENER_PORT
- MINECHAT_WRITER_PORT
- MINECHAT_HISTORY
- MINECHAT_AUTH_TOKEN

If command line argument is used its value would be used.
