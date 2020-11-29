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

1. Generate the configmap from file
  - kubectl create configmap discord-py-config -n discord-bot-py --from-file=./config/bot.json
2. Generate the secrets from file
  - kubectl create secret generic discord-py-secrets -n discord-bot-py --from-file=./config/secrets.json
3. Set up nfs share for any audiofiles and modify 2_kube-storage file with correct fileshare info
3. Deploy
  - kubectl apply -f ./Deployment_files/

### Local:

TODO
