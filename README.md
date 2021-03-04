# Discord-bot-py

## Requirements:
* Python3
* Discord Auth-token

## Installation:

1. Run quickstart.py
  - **Windows** python quickstart.py
  - **Linux** sudo python3 quickstart.py
2. Follow the instructions for whichever setup you are using

### Kubernetes:

#### 1. Update files in config folder with correct info for your setup. Required changes are:
  - bot_secret.json
    - data.discordToken
    - data.ownerIds
    - data.postgresql.password
    - data.postgresql.host (With default settings "svc-robotodb.roboto.svc")
    - data.hereApiToken (For weather function)
    - data.apiUserAgentIdentification (For weather function)
  - db_secrets.json
    - data.POSTGRES_PASSWORD (This need to be the same as in bot_secret.json)
#### 2. Update files in config folder with correct info for your setup. Likely changes are:
  - 2_kube-storage.yaml
    - spec.nfs.path
    - spec.nfs.server
#### 3. create namespace:
  - kubectl apply -f ./kubernetes/0-namespace.yaml
#### 4. Create config and secrets:
  - kubectl apply -f ./config/
#### 5. Apply roboto configuration:
  - kubectl apply -f ./kubernetes/

### Local:
Requires separate postgres database

1. update files in config folder with correct info for your setup:
  - bot_secret.json
    - discordToken
    - ownerIds
    - postgresql.password
    - postgresql.host
