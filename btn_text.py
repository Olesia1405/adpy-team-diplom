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
BTN_SEX_MAN = 'Кавалера🙎‍♂️'
BTN_SEX_WOMAN = 'Женщину🙎‍♀️️'
BTN_MAIN_MENU = 'Главное меню🏠'
BTN_CHOSEN = "⭐Избранные⭐"
BTN_NEXT = 'Следующий🔜'
BTN_BACK = 'Предыдущий🔙'
BTN_REMOVE_FAVORITES = 'Убрать из избранных💔'

# генерация кнопок в клавиатуре
buttons_regist = [(BTN_REGISTRATION, VkKeyboardColor.POSITIVE),
                  (BTN_HELP, VkKeyboardColor.NEGATIVE)
                  ]

buttons_start = [(BTN_FIND_PAIR, VkKeyboardColor.PRIMARY),
                 (BTN_CHOSEN, VkKeyboardColor.POSITIVE),
                 (BTN_HELP, VkKeyboardColor.NEGATIVE)
                 ]

buttons_choice = [(BTN_LIKE, VkKeyboardColor.POSITIVE),
                  (BTN_DISLIKE, VkKeyboardColor.NEGATIVE),
                  (BTN_MAIN_MENU, VkKeyboardColor.PRIMARY)
                  ]

buttons_choice_sex = [(BTN_SEX_MAN, VkKeyboardColor.PRIMARY),
                      (BTN_SEX_WOMAN, VkKeyboardColor.POSITIVE),
                      (BTN_MAIN_MENU, VkKeyboardColor.PRIMARY)
                      ]
buttons_favorites = [(BTN_BACK, VkKeyboardColor.PRIMARY),
                     (BTN_NEXT, VkKeyboardColor.PRIMARY),
                     (BTN_REMOVE_FAVORITES, VkKeyboardColor.NEGATIVE),
                     (BTN_MAIN_MENU, VkKeyboardColor.POSITIVE)
                     ]
buttons_favorites_next = [(BTN_NEXT, VkKeyboardColor.PRIMARY),
                          (BTN_REMOVE_FAVORITES, VkKeyboardColor.NEGATIVE),
                          (BTN_MAIN_MENU, VkKeyboardColor.POSITIVE)
                          ]

buttons_favorites_back = [(BTN_BACK, VkKeyboardColor.PRIMARY),
                          (BTN_REMOVE_FAVORITES, VkKeyboardColor.NEGATIVE),
                          (BTN_MAIN_MENU, VkKeyboardColor.POSITIVE)
                          ]
# Сообщение пользователем.

WELCOME_MESSAGE = '\nДобро пожаловать в наш бот для поиска своей второй половинки 💕! \n\n' \
                  'Мы поможем тебе найти интересных людей и завести новые знакомства.\n\n' \
                  'Нажми "Найти пару 💓", чтобы начать поиск! Если что-то непонятно — ' \
                  'всегда можно нажать на "Помощь 🆘".\n\n' \
                  'Удачи в поиске, надеемся, что здесь ты найдёшь именно того, кого ищешь! 💫'

HELP_MESSAGE = """
                Этот бот поможет вам найти пару! 👫
                
                Команды бота:
                - "Начать" — зарегистрируйтесь и начните поиск.
                - "Найти пару" — выберите параметры для поиска кандидатов.
                - "Помощь" — получите информацию о командах бота.
                
                Используйте кнопки на клавиатуре для быстрого доступа к функциям.
                
                Если возникли вопросы, обратитесь в поддержку. Удачи в поиске!
                """
