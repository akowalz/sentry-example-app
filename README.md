# Sentry Example App

Bootstrap:
```bash
brew install pipenv
pipenv install
```

Build the database:

```bash
pipenv run dbdo
```

Run the app:

```bash
pipenv run server
```

Run in debug mode (with hot reloading):

```bash
FLASK_ENV=development pipenv run server
```
