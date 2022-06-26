# [Mega Market Backend](https://ybs.shamaevn.com/docs)
### Made by [@shamaevnn](https://t.me/shamaevnn)
Solving practical part of task. Avaiable at https://ybs.shamaevn.com/docs#


Implemented methods:
* `GET` nodes with children. It's made with **ONLY ONE** SQL request. Tests are passed ✅
* `DELETE` item with all corresponding items, tests ✅
* `POST` import item, update if exists, tests ✅
* `GET` item sale **statistics**, tests ✅

<img width="592" alt="Screenshot 2022-06-26 at 23 14 57" src="https://user-images.githubusercontent.com/50623190/175832316-10f8f223-c35a-4369-83bf-d8a2d0a2a060.png">

## Used Technologies
* Python with `FastAPI` for backend
* Database: `PostgreSQL`. Just have a look at this [AMAZING QUERY](https://github.com/shamaevnn/ybs-summer-2022/blob/master/app/models/items/queries.py#L14) 👀 via
postgres to get item and all it's children recursively.
* Data validation: `Pydantic`
* Linters: `mypy`, `flake8`, `black`
* `GitHub Actions` for deployment


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


## Deployment info
This app is deployed via [dokku](https://dokku.com/) -- free open-source version of Heroku.
Unfortunately, I haven't managed to deploy it to Yandex servers. Probably, because of VPN.

* Push or pull request to any branch triggers `checks.yml` github action with linters
* Push to `master` begins deployment process
