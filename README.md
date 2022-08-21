# sage

This app is is like Mint, but better. It collects all of an individual's personal financial data. Data is collected from:

1. Bank alert emails sent to a personal gmaila account. 
2. TBD

The data is stored in Postgres and viewed through Grafana.

## Usage
1. Create a [Google Cloud project](https://developers.google.com/workspace/guides/create-project).
2. Create the .env file using .env-example as a template.
3. Create credentials.json and populate it with the credentials [from Google Cloud](https://developers.google.com/workspace/guides/create-credentials). example-credentials.json shows the expected format for credentials.
4. Start docker:
```bash
$ docker compose up
```

# Useful Commands
Remove all volumes
```
docker volume rm $(docker volume ls -q)
```