-- Таблица пользователей (Users)
CREATE table if not exists users (
    id SERIAL PRIMARY KEY,
    vk_id BIGINT UNIQUE NOT NULL,  -- VK ID пользователя
    name VARCHAR(255) NOT NULL,    -- Имя и фамилия пользователя
    city VARCHAR(255),             -- Город пользователя
    age INT,                       -- Возраст пользователя
    gender CHAR(1),                -- Пол пользователя ('M' или 'F')
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица избранных пользователей (Favorites)
CREATE TABLE if not exists favorites (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- ID пользователя в нашей системе
    favorite_vk_id BIGINT NOT NULL,  -- VK ID избранного пользователя
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица фотографий (Photos)
CREATE table if not exists photos (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- ID пользователя в нашей системе
    photo_url TEXT NOT NULL,                             -- URL фотографии
    likes_count INT NOT NULL,                            -- Количество лайков на фотографии
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);