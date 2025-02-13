# Kreigspile
This project is web app for playing [Kreigspile](https://en.wikipedia.org/wiki/Kriegspiel_(chess)) in multyplayer.

## Prerequisites
Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Create your passwords
Copy *.env.example* to *.env* and write new passwords inside

### Build and Start the Containers
Use Docker Compose to build and start the containers:
```bash
docker-compose up --build -d
```
To stop and remove the containers, use:
```bash
docker-compose down
```

After launch mongo and etc. you can restart only app container for debug:
```bash
docker restart ks-app
```

### Access the App
Once the containers are running, you can access the application via:

Web UI: Open your browser and go to http://localhost. This should display the Login form. For access

Mongo UI: you can check MongoDB with Mongo-express on http://localhost:8081