import json
from fastapi import FastAPI
from loguru import logger
from modules.db import DB
from modules.checks import Checks
from sqlalchemy import create_engine
from models import Base
from settings import settings_db


app = FastAPI()

engine = create_engine(f"postgresql+psycopg2://{settings_db['username']}:{settings_db['password']}@{settings_db['host']}:{settings_db['port']}/{settings_db['database']}")

Base.metadata.create_all(engine)



@app.post("/create/walk")
async def create_walk(name: str, 
                      phone: str, 
                      dog_name:str,
                      flat_number: int, 
                      start_date: str,
                      dog_description: str = None):
    """
        Создание заказа
        Parameters
        ----------
        name: str
            Имя хозяина собаки
            Пример: Иван
        phone: str
            Номер телефона хозяина собаки
            Пример: 89558883344
        dog_name: str
            Кличка собаки
            Пример: Барбос
        flat_number: int
            Номер квартиры
            Пример: 1
        start_date: str
            Дата начала прогулки
            Пример: 2024-01-30 14:00
        dog_description: str
            Описание собаки, её особенности
            Пример: Особо активный, во время прогулки нужно с ним бегать
        Returns
        -------
        json
            Если объект уже существует, то
                {'message': 'Объект уже существует',
                    'object_id': int}
            Если объект не существовал, то
                {'message': 'Объект сохранен',
                    'object_id': int}
            Если цена для времени не была создана, то
                {'error': 'Вы не создали цену для времени'}
    """
    
    check = Checks()
    check_date = check.check_time_walk(check_time=start_date)
    check_phone = check.check_phone(check_phone=phone)

    if 'error' in check_date:
        return json.dumps(check_date,ensure_ascii=False)
    else:
        start_date = check_date['check_time']
    
    if 'error' in check_phone:
        return json.dumps(check_phone,ensure_ascii=False)
    else:
        phone = check_phone['check_phone']
    
    db = DB(engine=engine)
    result = db.insert(table_name='walk', values= {'name': name,
                                          'phone': phone,
                                          'dog_name': dog_name,
                                          'dog_description': dog_description,
                                          'flat_number': flat_number,
                                          'start_date': start_date})
    return json.dumps(result,ensure_ascii=False)

@app.post("/get/walks")
async def get_walks(current_date: str = None, status: str = None):
    """
        Функция для получения всех заказов по указанной дате и статусу (оба параметра опциональны)
        Parameters
        ----------
        current_date: str
            Дата, по которой будет осуществлён поиск заказов
            Пример: '2024-01-30'
        status: str
            Статус заказа
            Может быть None (если никакое значение не получено). 
            Либо 'ACSS' (принято), либо 'RJCT' (отклонено), либо 'CRTD' (создано)
            Пример: 'CRTD'
        Returns
        -------
        json
            { 'walks':
                [
                    {
                        'walk_id': 1,
                        'start_date': '2024-01-30 14:00',
                        'end_date': '2024-01-30 14:30',
                        'created_at': '2024-01-29 13:47',
                        'status': 'ACSS',
                        'dog_name': 'Барбос',
                        'dog_description':'Особо активный, во время прогулки нужно с ним бегать',
                        'user_name': 'Иван',
                        'phone': '89664454560',
                        'price': 500.00,
                        'who_walking': 'Петр'
                    }, 
                    ...
                ]
            }
    """
    check = Checks()
    if current_date:
        check_date = check.check_current_date(current_date=current_date)
        if 'error' in check_date:
            return json.dumps(check_date,ensure_ascii=False)
        else:
            current_date = check_date['current_date']

    if status:
        if len(status) > 4:
            return json.dumps({'error': 'Неправильный статус'},ensure_ascii=False)
        
    db = DB(engine=engine)
    items = db.get_all_walks(current_date=current_date,status=status)
    return json.dumps({'walks': items},ensure_ascii=False)


@app.put("/update/walk/status")
async def update_status(walk_id: int, status: str, who_walking: str = None):
    """
        Функция обновления статуса у заказа
        Parameters
        ----------
        walk_id: int
            id заказа
            Пример: 1
        status: str
            Статус заказа 
            Либо 'ACSS' (принято), либо 'RJCT' (отклонено), либо 'CRTD' (создано)
            Если статус 'ACSS', обязательно надо вписать имя гуляющего с собакой в who_walking
            Пример: CRTD
        who_walking: str
            Имя гуляющего
        Returns
        -------
        json
            {'error': str}
            или
            {'message': str}
    """
    db = DB(engine=engine)
    if status:
        if len(status) > 4:
            return json.dumps({'error': 'Неправильный статус'},ensure_ascii=False)
        if status == 'ACSS' and (not who_walking or who_walking == ''):
            return json.dumps({'error': 'Укажите имя гуляющего'},ensure_ascii=False)
    return json.dumps(db.update(table_name='walk',values={'walk_id': walk_id,'status': status,'who_walking': who_walking}),ensure_ascii=False)

@app.post("/create/price")
async def create_price(price:float):
    """
        Функция создания цен на всё время
        Parameters
        ----------
        price: float
            Цена прогулки
            Пример: 700
        Returns
        -------
        json
            {'message': str}
    """
    db = DB(engine=engine)
    return json.dumps(db.create_price(price=price), ensure_ascii=False)


@app.put("/update/price")
async def update_price(hour_minute: str, price: float):
    """
        Функция изменения цены на определенное время
        Parameters
        ----------
        hour_minute: str
            Время
            Пример: 7:00
        price: float
            Цена прогулки
            Пример: 700
        Returns
        -------
        json
            {'message': str}
    """
    db = DB(engine=engine)
    return json.dumps(db.create_price(hour_minute=hour_minute,price=price), ensure_ascii=False)