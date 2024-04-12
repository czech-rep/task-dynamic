Start comtainers
```sh
docker compose up -d
```

Apply migrations
```sh
docker compose exec backend ./manage.py migrate
```

Run tests
```sh
docker compose exec backend ./manage.py test
```
