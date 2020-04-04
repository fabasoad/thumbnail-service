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
            "name": "Thumbnail Service",
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
| Healthcheck                 | /api/v1/system/pulse           | GET    | None          | None                              | 200          | {"alive": true}                                                                                                                              |
| Get info of all thumbnails  | /api/v1/thumbnail              | GET    | None          | None                              | 200          | [{"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": true, "size": {"original": 343956, "thumbnail": 3609}}] |
| Get info of thumbnail by ID | /api/v1/thumbnail/:id          | GET    | None          | None                              | 200          | {"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": true, "size": {"original": 343956, "thumbnail": 3609}}   |
| Upload image                | /api/v1/thumbnail              | POST   | image=\<Image\> | Content-Type: multipart/form-data | 201          | {"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": false, "size": {"original": 343956}}                     |
| Delete thumbnail            | /api/v1/thumbnail/:id          | DELETE | None          | None                              | 200          | {"id": "09e35a84-eecd-4386-b8cf-299bbe478b14", "filename": "IMG_8667.png", "ready": true, "size": {"original": 343956, "thumbnail": 3609}}   |
| Download thumbnail          | /api/v1/thumbnail/:id/download | GET    | None          | None                              | 200          | \<Image\>                                                                                                                                      |
## Architecture
### Description
Basically we have 2 layers - REST API layer (`rest` folder) and Services layer (`service` folder). Each request is handled by related function in `*_resources.py` file. This layer retrieves needed information from request (like `id` for example) and passes it to `thumbnail_service.py` (if it's not healthcheck). Service layer works with Redis instance using `redis_factory.py` file and with `thumbnail_processor.py` file that are responsible for image resizing.
### Technologies
`aiohttp` is used for REST API layer. It's modern framework that allows easily create REST application. Also, it is used as a client for REST tests. Redis is used to store the information about images. It has a good mechanism for records expiration (`EXPIRE`), so we can set records lifetime if we do not need to store the thumbnails forever (then separate job can just check existing keys in Redis and remove all the files from storage that are not present in Redis). `PIL` python library is used for image resizing. It's powerful library to work with images and we can use it for future improvements as well (for example, if we will need to save image proportions or put watermark on top of thumbnails for `free` accounts, etc.).
### Workflow
Let's take a look at full lifecycle. Client sends a request to upload the image, `thumbnail_resources.py` (later, just `TR`) gets this request and passes stream reader to `thumbnail_service.py` (later, just `TS`). `TS` validates the coming data and if all fine it does the following: saves original image to the storage (using `id` as a file name), saves information about this image to Redis, passes image to `thumbnail_processor.py` (later, just `TP`) to resize it in a separate thread and immediately returns the result about the image with state `ready=False` (means that thumbnail is not ready yet). `TR` returns this information in response in JSON format. Client retrieves the response that has information about original image name, original image size, id and status (not ready yet). In any time client can check the status of this image by calling GET `/api/v1/thumbnail/:id` request where `id` is id that came from previous call. Let's assume that in a background `TP` is finished its work (means that thumbnail file is created with `id` + `.thumbnail` suffix and Redis is updated with the new information - `ready=True` and thumbnail image size). So `TR` retrieves GET request and passes `id` from it to `TS` to get the current state. `TS` retrieves actual information from Redis (that is already updated by `TP`) and returns it to `TR`. `TR` returns this information in response in JSON format. Client sees that status `ready=True` and sees the thumbnail size, so he decides to download this thumbnail by calling `/api/v1/thumbnail/:id/download` URL. `TR` retrieves this request and passes `id` to `TS` to download thumbnail. `TS` finds the information about the image in Redis and returns full path to the image and original name. `TR` returns this file as `FileResponse` but instead of `id` + `.thumbnail` name it passess original name and `thumbnail` suffix in the middle (e.g. original file name is `IMG_8932.png` then thumbnail will be `IMG_8932.thumbnail.jpg`) (note: resizing operation saves thumbnail in `JPEG` format). After client retrieves the thumbnail he decides to delete it from server. Client calls DELETE `/api/v1/thumbnail/:id` URL. `TR` retrieves the request and passes `id` to "delete" function in `TS`. `TS` deletes original file, thumbnail and information from Redis. Then returns information about deleted record (the same as GET returns). `TR` returns this information in response in JSON format.
## Improvements
### Functionality
1. We store thumbnail for a long time but we can also:
    1. Remove it right after client gets the thumbnail.
    2. Remove it after some time, e.g. after 1 hour. We need to create a separate job for it.
2. Cover `ThumbnailProcessor` by Unit tests.
3. Cover all cases for `ThumbnailService` by Unit tests (e.g. `save_file`, `get_file`, `get_thumbnail`).
4. Cover all cases by REST tests (e.g. `download_file`).
5. Add load testing (to be sure that application handles high load). We can use existing solutions for this purposes, for example [Artillery](https://artillery.io/) service.
6. `.env` file should be added to `.gitignore` but I left it there just for the convenience to run the application.
7. `REDIS_PASSWORD` should be added to `.env` as it's sensitive information.
8. We are storing original files. It takes some time as well:
    1. If it's not necessary this functional can be removed.
    2. If we need original file, we can move it's saving to background job, so client will not be waiting for this operation.
9. Do not create thumbnails for images that are smaller than 100x100 size.
10. For now all users have access to all thumbnails. We can add authentication, so that users cannot see/delete thumbnails of each other.
### Infrastructure
1. To scale it horizontally all what we need to do is to run another instance(s) of this application. All application instances will work with the same Redis instance and with the same image storage (shared folder in our case). For example, if we will work in Kubernetes cluster we can define a rule to scale this application up or down based on requests load.
2. For image storage we can use external storage, like AWS S3 that can store a big amount of data.
3. High load of requests would be a bit painful for now as we do original image saving in the same thread but based on option `8.2` from previous section we can improve it.
4. We can add REST tests and Unit tests running to CI job, so we can be sure that nothing is broken after each code change.
> Made by Yevhen Fabizhevskyi