#!/bin/bash

# Prepare the user credentials for MongoDB
q_MONGO_USER=$(jq --arg v "$MONGO_BACKEND_USERNAME" -n '$v')
q_MONGO_PASSWORD=$(jq --arg v "$MONGO_BACKEND_PASSWORD" -n '$v')

# Run MongoDB commands
mongosh -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" admin <<EOF
    
    db = db.getSiblingDB('ks_db');
    db.createUser({
        user: $q_MONGO_USER,
        pwd: $q_MONGO_PASSWORD,
        roles: [ "readWrite"],
    });
    db.createCollection('users');
    db.createCollection('games');
    db.createCollection('auth_logs');
    db.createCollection('errors_logs');
EOF