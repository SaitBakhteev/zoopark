from tortoise.models import Model
from tortoise import fields


# поля с префиксом tg заполняются автоматически от телеграмм
class User(Model):
    id = fields.IntField(primary_key=True)
    tg_id = fields.BigIntField()
    tg_username = fields.CharField(max_length=100)
    tg_name = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    admin_permissions = fields.BooleanField(default=False)
    totemic_animal = fields.CharField(max_length=20, null=True)


'''Названия категорий вопросов. Например, " Животные Индии", 
"Жвачные парнокопытные", "Животные тундры",
 "Земноводные" и т.п. '''
class Category(Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=20)
    animals = fields.JSONField() # список животных

    def __str__(self):
        return self.title


''' Вопросы с вариантами ответов. Правильный ответ 
в виде внешнего ключа в поле "correct_answer" '''
class Question(Model):
    id = fields.IntField(primary_key=True)
    text = fields.TextField()
    answers = fields.JSONField()

    # название категории вопроса
    category = fields.ForeignKeyField("models.Category", related_name='question')

    # Путь на файл для загрузки изображения животного, когда про него звучит вопрос
    image_path = fields.CharField(max_length=50)

    # название животного из словаря ANIMALS, про которого звучит вопрос
    animal = fields.CharField(max_length=20)

    def __str__(self):
        return self.text[:10]


# Результаты опроса-викторины
class Survey(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name='survey')
    survey_date = fields.DatetimeField(auto_now_add=True)

    # Результат опроса в виде текста. Пример:
    # "Набрано 45 баллов из 68. Тотемное животное-Бенгальский тигр"
    result = fields.CharField(max_length=50)
