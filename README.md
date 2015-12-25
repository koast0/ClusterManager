# ClusterManager #
  

## Отчет 

Отчет доступен по [ссылке](https://bitbucket.org/ivan_guschenko/clustermanager_iguschenko/src/a4987d3abf909aec2cfa8a6f272aed27e125d5e0/%D0%BE%D1%82%D1%87%D0%B5%D1%82.md?at=master&fileviewer=file-view-default).

## Запуск ##

### Необходимо для запуска ###

```
#!bash

# tornado
pip3 install tornado

# requests
pip3 install requests


```



### Master: ###
```
#!bash
python3 master.py (-c [--config]) (файл конфига)

```
### Agent: ###
```
#!bash
python3 agent.py -n[--name] (имя ноды) 

```
### Формат конфиг файла ###

```
#!bash
(Имя ноды) (команда запуска процесса)

```

При запуске системы без указанного конфиг файла, система инициализируется из базы данных agent.db.
При запуске с конфиг файлом система инициализирутся из него и по необходимости создает базу данных.