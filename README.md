**Collabrix - платформа с системой рекомендаций**, предназначенная для формирования проектных команд и взаимодействия студентов

## Технологический стек

*   **Backend**: FastAPI, SQLAlchemy, PyTorch, Transformers
*   **Frontend**: Streamlit
*   **RecSys**: Cosine Similarity, rubert-tiny2 embeddings

---

## Запуск проекта

### 1. Подготовка окружения
Клонируйте репозиторий и установите зависимости:

```bash
git clone https://github.com/razzikz/Collabrix.git
```

**Backend** (терминал №1)
```bash
cd Collabrix/backend
pip install -r requirements.txt
```

**Frontend** (терминал №2)
```bash
cd Collabrix/frontend
pip install -r requirements.txt
```

### 2. Запуск
Запустите API и веб интерфейс

**Запуск Backend** (терминал №1)
```bash
uvicorn main:app
```
*Запустится по адресу http://127.0.0.1:8000*

**Запуск Frontend** (терминал №2)
```bash
streamlit run app.py
```
*Запустится по адресу http://localhost:8501*
