docker stop $(docker container ps -qa)
docker rm -f $(docker container ps -qa)
docker rmi -f $(docker images -qa)
rm -rf pgadmin pgdata tools process archives workdir db logs registry-data api_service
