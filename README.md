# [Mega Market Backend](https://ybs.shamaevn.com/docs)
### Made by [@shamaevnn](https://t.me/shamaevnn)
Solving practical part of task. Avaiable at https://ybs.shamaevn.com/docs#


Implemented methods:
* `GET` nodes with children. It's made with **ONLY ONE** SQL request. Tests are passed ✅
* `DELETE` item with all corresponding items, tests ✅
* `POST` import item, update if exists, tests ✅
* `GET` item sale **statistics**, tests ✅

All of them are available [here](https://github.com/shamaevnn/ybs-summer-2022/tree/master/app/api), in `routes.py` particularly.

<img width="592" alt="Screenshot 2022-06-26 at 23 14 57" src="https://user-images.githubusercontent.com/50623190/175832316-10f8f223-c35a-4369-83bf-d8a2d0a2a060.png">

## Used Technologies
* Python with `FastAPI` for backend
* Database: `PostgreSQL`. Just have a look at this [AMAZING QUERY](https://github.com/shamaevnn/ybs-summer-2022/blob/master/app/models/items/queries.py#L14) 👀 via
postgres to get item and all it's children recursively.
* Data validation: `Pydantic`
* Linters: `mypy`, `flake8`, `black`
* `GitHub Actions` for deployment

## Database
This solution uses only 2 tables: [items](https://github.com/shamaevnn/ybs-summer-2022/blob/master/app/models/items/table_schema.py) for 3 main endpoints
and [items_statistic](https://github.com/shamaevnn/ybs-summer-2022/blob/master/app/models/items_statistic/table_schema.py) for statistic endpoint


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
4.Check http://0.0.0.0:80/docs, everything should be OK!


## Tests
```
make run_tests
```

## Linter
```
make lint
```


## Deployment info
Deploy to production via `GitHub Actions` consists of 3 steps:
1. Check all linters via pre-commit, it runs on any branch/pull request.

<img width="925" alt="Screenshot 2022-06-27 at 20 44 38" src="https://user-images.githubusercontent.com/50623190/176004430-a3371a91-a8f4-4ee9-9e83-cfa65e6ac4f0.png">

If it's success, then:
2. Login to github registry, build and push docker image.
3. Go to server via ssh and VPN, pull built docker image, stop old ones, start new one.

<img width="984" alt="Screenshot 2022-06-27 at 20 48 49" src="https://user-images.githubusercontent.com/50623190/176004515-56833876-7c21-4352-a6be-c68775867df6.png">

---

To deploy, you have to set several secret variables:
1. `VPN variables`.You can get it from your `.ovpn` file. Check [here](https://github.com/marketplace/actions/connect-vpn#how-to-prepare-file-ovpn) for more info.
```
CA_CRT  # encode to base64 content of <ca>
USER_CRT  # ... of <cert>
USER_KEY  # ... of <key>
VPN_FILE  #  check instruction above
```
2. `DATABASE_URL`, where your info about items will be stored, example:
```
postgresql://postgres:b9a59b43439d3ebac8a410c9@86.208.71.101:15336/ybs
```
3. `SERVER_IP` -- address of your server with backend.
4. `TOKEN_GITHUB` -- token with access to write/read/delete packages, check [this instruction](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
5. `SSH_PRIVATE_KEY` -- private key, which has access to server.
