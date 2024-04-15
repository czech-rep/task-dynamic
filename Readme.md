Create .env file
```sh
cp .env.template .env
```

Start comtainers
```sh
docker compose up -d
```

Visit:

http://localhost:8000/api/table/


Run tests
```sh
docker compose exec backend coverage run ./manage.py test
```

Check coverage
```sh
docker compose exec backend coverage report
```

----

/api/table/ accepts payload in form:
```
{
  "fields": [
    {
      "name": "name",
      "default": "anomim",
      "type": 1
    },
    {
      "name": "age",
      "type": "2"    }
  ]
}
```

then PUT accepts the same payload but will to edit in-place this table. Possible:
- add field - it fill be not required or will have a default value
- remove field - if its missing in PUTed payload
- change field type
- change of field name is impossible

looks like all fields will not be required, bc otherwise modification of table would require a default
// or: if default if provided, field will use it
FIRST lets create all as not required
