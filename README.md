# Mega Market Backend
### Made by [@shamaevnn](https://t.me/shamaevnn)
Solving practical part of task.


Implemented methods:
* `GET` nodes with children. It's made with **ONLY ONE** SQL request. Tests are passed ✅
* `DELETE` item with all corresponding items, tests ✅
* `POST` import item, update if exists, tests ✅
* `GET` item sale **statistics**, tests ✅


## First run
1. Clone repo
```bash
git clone git@github.com:shamaevnn/ybs-summer-2022.git
cd ybs-summer-2022
```
2. Create virtual environment and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.dev.txt
```
3. Install `pre-commit` hooks
```
pre-commit install-hooks
pre-commit install
```
4. Create `.env` file, don't forget to set proper variables
```
cp .env_example .env
```

## Running locally
1. Run all necessary services
```bash
make services
```
2. Apply migrations
```
make migrate
```
3.Run backend on FastAPI
```
make dev
```
4.Check http://0.0.0.0/docs, everything should be OK!


## tests
```
python3 tests/test_default.py
```

## linter
```
make lint
```
