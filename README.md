# Техническое задание

Необходимо написать `helmfile` и выложить в git, который выполняет следующее:
* Поднимает в k8s простую PostgreSQL базу любой версии и создает в ней одну таблицу (использовать Helm-чарт);
* Написать простой сервис (можно просто средствами nginx, можно на удобном Вам языке), который пишет в базу postgres IP клиента, который обращается через `ingress-nginx` к этому же сервису (должен получится dockerfile);    
* Написать Helm-чарт, который установит этот сервис в k8s.

### Трактовка

* Kubernetes кластер развернут локально в minikube;
* В кластере находятся `ingress-nginx`, k8s ресурсы для приложения: `Deployment`, `Service`, `Secret`, - а также релиз PostgreSQL;
* Запрос приходит на `ingress-nginx` и прокидывается на k8s `Service`;
* У k8s `Service` в селекорах стоят лейблы соответсвтущие Поду с приложением;
* Под при инициализации считывает учетные данные для PostgreSQL из k8s `Sercret`;
* Получая запросы от k8s `Service`, приложение считывает IP-адрес из HTTP-заголовка, открывает коннект к БД и создает строку в базе `postgres`.

### Архитектура решения

![arhc-k8s-cluster](/asset/image.png)


# Решение

### Сервис записи IP адресов в БД

Сервис написан на `Python` и развернут в `docker-container`.
При обращении GET-запросом по эндпоинту `/write-url` в БД PostgreSQL в таблицу `ip_test` создается запись, содержащая 2 атрибута: IP клиента и время обращения.

Rout и метод, используемые сервисом: 
```Python
@app.route("/write_ip", methods=["GET"])
```

В случае успешного внесения записи в БД
выводиться содержимое файла `index.html`, в случае ошибки (например при отсутвии коннекта к БД, неправильных кредах подключения, отсутствии таблицы) содержимое `error.html`

````php
        return render_template('index.html')
    except Exception as e:
        print(e)
        return render_template('error.html')  
````

### База данных PostgreSQL

Для деплоя Базы Данных использовался Helm-чарт [postgresql](https://github.com/bitnami/charts/tree/main/bitnami/postgresql/#installing-the-chart) от Bitnami, который добавлен в перечень релизов `helmfile`.

Секреты подключения были кастомизированы и хранятся в файле `/helmfile/deploy/minikube/secrets.yaml`. 
Для расшифровки файла необходимо сделать следующее: 
1) Распаковать архив с приватными ключами `gnupg.tar` в домашнюю директорию пользователя, в папку `.gnupg`;
2) Зайти в терминале в папку `python-demo-service/helmfile`;
3) Запустить команду:
```bash
helm secrets dec deploy/minikube/secrets.yaml
```

В БД создается таблица `ip_test`.
Скрипт используемый для создания таблицы:
````SQL
CREATE TABLE IF NOT exists postgres.public."ip_test" (ip text, time time);
````

Таким образом, мы можем версионировать миграции. 

### Структура репозитория

```yaml

├── helm-chart ## Helm-чарт для деплоя микросервиса в k8s
├── helmfile
│   └── deploy
│       ├── bases
│       │   └── defaults.yaml ## Преднастройки вида: автосоздание Неймспеса, автовыбор kube-context
│       ├── helmfile.yaml ## Корневой файл, в нем описаны релизы, чарты, окружения
│       ├── minikube
│       │   ├── environment.yaml ## Стендозависимые переменные окружения (версия образа, кол-во реплик, скрипт создания таблицы)
│       │   └── secrets.yaml ## Зашифрованный файл с секретами для подключения к БД
│       └── values
│           ├── environment.yaml ## Общие параметры, независимо от окружения
│           ├── ipapp.yaml.gotmpl ## Values сервиса 
│           └── postgre-db.yaml.gotmpl ## Values БД
└── svc ## Исходный код приложения и `Dockerfile` для сборки
```

# Деплой и тестирование проекта

1) Верификация изменений путем запуска превью:
```Go
helmfile -e minikube -f deploy/helmfile.yaml diff
```
2) Деплой проекта: 
```
helmfile -e minikube -f deploy/helmfile.yaml apply
```
3) Переадресация портов командой:
```
kubectl port-forward --namespace ipapp svc/postgre-db-postgresql 5432:5432
```
4) Обращение к сервису через `ingress-nginx`
```
curl http://ipapp.ru/write_ip ## Я прописывал ipapp.ru 127.0.0.1 в hosts
```
5) Проверка наличия в таблице записей

![BD check](/asset/image2.png)