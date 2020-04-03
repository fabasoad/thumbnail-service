# Thumbnail Service
## How to run
### Prerequisites
1. Docker >= 19.03.5
2. Docker-Compose >= 1.24.1
### Steps
1. Create `./docker/.env` file with the following content:
```bash
VERSION=1.0.0
PORT=8080
THUMBNAIL_PATH=/usr/local/temp
```
2. Run `docker-compose` command:
```bash
cd ./docker
docker-compose -f "docker-compose.yml" up -d --build
```
3. Open `http://127.0.0.1:8080/` in browser.
## How to debug
### VS Code
1. Create `.vscode/launch.json` file with the following content:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: File Storage",
            "type": "python",
            "request": "launch",
            "module": "src.rest"
        }
    ]
}
```
2. Go to the Debug tab and run your configuration.
## Run REST application manually
> In case something went wrong with Docker running
1. Install Python 3 and Pip.
2. Install and run Redis with password.
3. Run the following command (Linux):
```bash
export THUMBNAIL_PATH=<Path to images folder>
export THUMBNAIL_BACKEND_HOST=127.0.0.1
export THUMBNAIL_BACKEND_PORT=8080
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
export REDIS_PASSWORD=<PASSWORD>
pip install -r requirements.txt
python -m src.rest
```
4. For quick check, open `http://127.0.0.1:8080/api/v1/thumbnail` in browser. There should be an empty array in JSON format (in case you run it at first time).
## Run Tests
### REST Tests
1. Run server with clean state
2. Run the command below.
```bash
# export commands are optional
export REST_SCHEMA='http' # default is 'http'
export REST_HOST='localhost' # default is '127.0.0.1'
export REST_PORT=8080 # default is 8080
pip install -r requirements.txt
pytest ./src/rest_tests
```
### Unit Tests
1. Run the commands below.
```bash
pip install -r requirements.txt
pytest ./src/service/tests
```