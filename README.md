# User-api

1> Deploy MySQL RDS in AWS 
2>check for connectivity from local using your favourite database client.
3>write a .env file with credentials in it as below format:
  HOST=hostname or ip address
  USER_NAME=username
  PASSWORD=database password
  DBNAME=dbname
4>Use the sql.txt for creating the user table.
5>To build a docker image in the local 
Run sudo docker build -t reponame/tagname .
6>Check for docker image and run container out of it by pointing local port with container port
and now endpoint can be accessed from localhost through local port mapped.
  
