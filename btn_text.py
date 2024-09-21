"""
btn_text.py

Этот модуль содержит текстовые метки для кнопок, используемых в боте ВКонтакте,
а также их цветовые обозначения. Кнопки используются для взаимодействия с
пользователями и упрощают процесс выбора действий.

Константы:
----------
- BTN_FIND_PAIR: Текст кнопки для поиска пары.
- BTN_HELP: Текст кнопки для получения помощи.
- BTN_LIKE: Текст кнопки "Нравится".
- BTN_DISLIKE: Текст кнопки "Не нравится".
- BTN_NEXT: Текст кнопки "Следующий".

Списки кнопок:
---------------
- buttons_star: Список кнопок, которые отображаются на начальном экране
  бота. Включает кнопки "Найти пару" и "Помощь".

- buttons_choice: Список кнопок, которые отображаются при выборе действия.
  Включает кнопки "Нравится", "Не нравится" и "Следующий".

Использование:
--------------
Импортируйте этот модуль в основной код бота, чтобы получить доступ к
текстовым меткам и кнопкам. Например:

```python
from btn_text import buttons_star, buttons_choice

"""
from vk_api.keyboard import VkKeyboardColor

# Названия кнопок

BTN_REGISTRATION = 'Начать регистрацию📋'
BTN_FIND_PAIR = "Найти пару💓"
BTN_HELP = "Помощь🆘"
BTN_LIKE = "Нравится👍"
BTN_DISLIKE = "Не нравится👎"
BTN_NEXT = "Следующий👉"
BTN_SEX_MAN = 'Кавалера🙎‍♂️'
BTN_SEX_WOMAN = 'Женщина🙎‍♀️️'

# генерация кнопок в клавиатуре
buttons_regist = [(BTN_REGISTRATION, VkKeyboardColor.POSITIVE),
                (BTN_HELP, VkKeyboardColor.NEGATIVE)
                ]
buttons_start = [(BTN_FIND_PAIR, VkKeyboardColor.POSITIVE),
                (BTN_HELP, VkKeyboardColor.NEGATIVE)
                ]

buttons_choice = [(BTN_LIKE, VkKeyboardColor.POSITIVE),
                  (BTN_DISLIKE, VkKeyboardColor.NEGATIVE),
                  (BTN_NEXT, VkKeyboardColor.POSITIVE)
                  ]
buttons_choice_sex = [(BTN_SEX_MAN, VkKeyboardColor.PRIMARY),
                      (BTN_SEX_WOMAN, VkKeyboardColor.POSITIVE)
                      ]
# Сообщение пользователем.

welcome_message = '\nДобро пожаловать в наш бот для поиска своей второй половинки 💕! \n\n' \
                  'Мы поможем тебе найти интересных людей и завести новые знакомства.\n\n' \
                  'Нажми "Найти пару 💓", чтобы начать поиск! Если что-то непонятно — ' \
                  'всегда можно нажать на "Помощь 🆘".\n\n' \
                  'Удачи в поиске, надеемся, что здесь ты найдёшь именно того, кого ищешь! 💫'