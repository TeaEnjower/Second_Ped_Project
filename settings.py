from envparse import Env

env = Env()
env.read_envfile()

# Читаем отдельные переменные
POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_PORT = env.int("POSTGRES_PORT")  # Используем int для порта
DB_HOST = env.str("DB_HOST")

# Собираем строку подключения
REAL_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"