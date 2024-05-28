# Build docker image 

To spin up everything, run 'docker-compose' in the root of this project:

```shell
docker-compose up
```

## Create admin

To create an admin one could use the following command:

```shell
docker exec -it music-mood-recommender-app flask create-admin <username>
```
