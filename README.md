# GTN_monitoring service
- required MongoDB on localhost:27017
- required Redis on localhost:6379

# For run
```
chmod a+x start.sh && ./start.sh
```
# Request description:

- `~/api/country/all` 'get' запрос возвращает список всех стран
- `~/api/country/<name>` 'get' запрос возвращает информацию по стране
 доступные сервера, поисковики итд.