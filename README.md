# Image Annotation — веб-приложение

Веб-приложение для управления проектами, загрузки изображений и интерактивной разметки

## Технологии

### Frontend
- **Vue.js 3** — фреймворк для создания пользовательского интерфейса
- **Vue Router** — маршрутизация
- **Pinia** — управление состоянием
- **Vite** — сборщик и dev-сервер
- **Nginx** — веб-сервер для production сборки

### Backend
- **FastAPI** — современный веб-фреймворк для Python
- **SQLAlchemy** — ORM для работы с базой данных
- **PostgreSQL** — реляционная база данных
- **Uvicorn** — ASGI-сервер

### Инфраструктура
- **Docker** — контейнеризация приложения
- **Docker Compose** — оркестрация сервисов

## Структура проекта

```
.
├── backend/              # Backend приложение (FastAPI)
│   ├── app/
│   │   ├── api/routes/   # API эндпоинты
│   │   ├── core/         # Конфигурация и база данных
│   │   ├── models/       # SQLAlchemy модели
│   │   ├── schemas/      # Pydantic схемы
│   │   ├── services/     # Бизнес-логика
│   │   └── static/       # Статические файлы (изображения)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Frontend приложение (Vue.js)
│   ├── src/
│   │   ├── api/          # API клиенты
│   │   ├── components/   # Vue компоненты
│   │   ├── router/       # Маршруты
│   │   ├── store/        # Pinia stores
│   │   └── views/        # Страницы
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml    # Конфигурация Docker Compose
└── README.md
```

## Функциональность

### Управление проектами и изображениями

- ✅ Отображение списка проектов
- ✅ Создание нового проекта по названию
- ✅ Просмотр списка загруженных изображений внутри проекта
- ✅ Загрузка одного или нескольких изображений (через кнопку или drag-and-drop)
- ✅ Предварительный просмотр изображений в виде миниатюр
- ✅ Удаление проекта и отдельных изображений

### Интерактивная аннотация изображений

- ✅ Отображение выбранного изображения
- ✅ Рисование bounding box'ов на изображении (с зажатой мышью)
- ✅ Назначение класса bounding box'у после создания
- ✅ Хранение каждого bounding box'а как отдельного объекта с координатами, классом и уникальным идентификатором
- ✅ Отображение всплывающей подсказки при наведении на bounding box (класс, координаты, размеры)
- ✅ Редактирование и удаление созданных bounding box'ов
- ✅ Масштабирование изображения с корректной работой аннотаций при зуме
- ✅ Имитация вызова ML-эндпоинта (POST /predict) с возвратом фейковых bounding box'ов

## API Эндпоинты

### Проекты
- `POST /projects` — создать проект
- `GET /projects` — получить список всех проектов
- `DELETE /projects/{id}` — удалить проект и все связанные изображения

### Изображения
- `POST /projects/{id}/images` — загрузить одно или несколько изображений в проект
- `GET /projects/{id}/images` — получить метаданные и ссылки на изображения проекта
- `GET /images/{image_id}` — получить информацию об изображении
- `DELETE /images/{image_id}` — удалить конкретное изображение

### Аннотации
- `POST /images/{image_id}/annotations` — создать аннотацию (bounding box)
- `GET /images/{image_id}/annotations` — получить все аннотации изображения
- `PUT /images/{image_id}/annotations/{annotation_id}` — обновить аннотацию
- `DELETE /images/{image_id}/annotations/{annotation_id}` — удалить аннотацию

### ML Предсказания
- `POST /predict/{image_id}` — получить предсказания ML-модели в формате COCO-like аннотаций

## Запуск проекта

### Требования
- Docker
- Docker Compose

### Запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd practic
```

2. Запустите все сервисы одной командой:
```bash
docker-compose up --build
```

3. Приложение будет доступно по адресам:
   - Frontend: http://localhost:5174
   - Backend API: http://localhost:8001
   - API документация (Swagger): http://localhost:8001/docs

### Остановка

```bash
docker-compose down
```


## Хранение данных

### База данных
Проект использует PostgreSQL для хранения метаданных проектов, изображений и аннотаций.

### Изображения
В текущей реализации изображения хранятся локально в директории `backend/app/static/images/`


### Переход на внешнее хранилище (S3)

Для перехода на S3-совместимое хранилище (например, MinIO, AWS S3) необходимо:

1. **Установить библиотеку для работы с S3:**
   ```bash
   pip install boto3
   ```

2. **Модифицировать `backend/app/services/storage.py`:**
   - Добавить конфигурацию для S3 (endpoint, access key, secret key, bucket name)
   - Заменить функцию `save_image()` на загрузку в S3 через boto3
   - Обновить логику получения URL изображений (использовать presigned URLs или публичные URL)

3. **Обновить конфигурацию:**
   - Добавить переменные окружения для S3 в `docker-compose.yml`
   - Обновить `backend/app/core/config.py` для чтения S3 настроек

4. **Опционально: добавить MinIO в docker-compose.yml:**
   ```yaml
   minio:
     image: minio/minio
     ports:
       - "9000:9000"
       - "9001:9001"
     environment:
       MINIO_ROOT_USER: minioadmin
       MINIO_ROOT_PASSWORD: minioadmin
     command: server /data --console-address ":9001"
     volumes:
       - minio_data:/data
   ```

Архитектура сервиса `storage.py` позволяет легко заменить локальное хранение на S3 без изменения остального кода.



