# Thumbnail Service
## How to run
### REST application using Docker
#### Prerequisites
1. Docker >= 19.03.5
2. Docker-Compose >= 1.24.1
#### Steps
1. Run `docker-compose` command:
```bash
cd ./docker
docker-compose -f "docker-compose.yml" up -d --build
```
2. For quick check, open `http://127.0.0.1:8080/api/v1/thumbnail` in browser. There should be an empty array in JSON format (in case you run it at first time).
> It might take a several minutes to up and run the application.
### Tests
#### REST Tests
1. Run server with clean state
2. Run the command below.
    1. From host (Linux):
    ```bash
    pip install -r requirements.txt
    pytest src/rest_tests
    ```
    2. From docker container:
    ```bash
    docker exec -it <CONTAINER ID> /bin/bash
    pytest src/rest_tests
    ```
#### Unit Tests
1. Run the command below.
    1. From host (Linux):
    ```bash
    pip install -r requirements.txt
    export REDIS_HOST=127.0.0.1
    export REDIS_PORT=6379
    export REDIS_PASSWORD=<password from docker/env/redis.env file>
    pytest ./src/service/tests
    ```
    2. From docker container:
    ```bash
    docker exec -it <CONTAINER ID> /bin/bash
    pytest src/service/tests
    ```
### REST application in Debug mode
#### VS Code
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
### REST application manually
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
> It might take a several minutes to up and run the application.
## REST API Documentation
| Description                 | URL                            | Method | Form Data     | Headers                           | Success Code | Example Response                                                                                                                             |
|-----------------------------|--------------------------------|--------|---------------|-----------------------------------|--------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Get info of all thumbnails  | /api/v1/thumbnail              | GET    | None          | None                              | 200          | [{"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": true, "size": {"original": 343956, "thumbnail": 3609}}] |
| Get info of thumbnail by ID | /api/v1/thumbnail/:id          | GET    | None          | None                              | 200          | {"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": true, "size": {"original": 343956, "thumbnail": 3609}}   |
| Upload image                | /api/v1/thumbnail              | POST   | image=\<Image\> | Content-Type: multipart/form-data | 201          | {"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": false, "size": {"original": 343956}}                     |
| Delete thumbnail            | /api/v1/thumbnail/:id          | DELETE | None          | None                              | 200          | {"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": true, "size": {"original": 343956, "thumbnail": 3609}}   |
| Download thumbnail          | /api/v1/thumbnail/:id/download | GET    | None          | None                              | 200          | \<Image\>                                                                                                                                      |
## Improvements
