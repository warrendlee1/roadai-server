# Road AI Server

Map anomaly data labeling for AV.

## Setup key.json

1. Navigate to https://console.firebase.google.com/u/0/project/roadai-995db/settings/serviceaccounts/adminsdk
2. Click on 'Service Accounts'
3. Click 'Generate new private key'
4. Select 'Python'
5. Drag/Drop private key into project
6. Rename file to 'key.json'

## Setup Development Environment

1. Create virtual environment

```
python3 -m venv env
```

2. Activate virtual environment

```
. env/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

**NOTE:** if you install new dependencies, then make sure to update requirements.txt

```
pip freeze > requirements.txt
```

## Running the API

```
python app.py
```
