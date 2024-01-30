import re
from sqlalchemy import and_, insert, text, update
from models import *
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from loguru import logger

class DB:
    def __init__(self,engine) -> None:
         self.engine = engine

    @logger.catch
    def insert(self, table_name: str, values: dict) -> dict:
        """
        Функция для добавления данных в базу данных
        Parameters
        ----------
        table_name: str
            Название таблицы
            Пример: 'walk'
        values: dict
            Словарь из значений, необходимый для создания строки в таблице
            Пример: {'start_date': '2024-01-30 14:00', 
                        'phone': '89664454560', 
                        'name': 'Иван', 
                        'flat_number': 1,
                        'dog_name': 'Барбос',
                        'dog_description': 'Особо активный, во время прогулки нужно с ним бегать'}
        Returns
        -------
        dict
            Если объект уже существует, то
                {'message': 'Объект уже существует',
                    'object_id': int}
            Если объект не существовал, то
                {'message': 'Объект сохранен',
                    'object_id': int}
        """
        if table_name != 'walk':
            object_id = self.check_exist_object(table_name=table_name,values=values)
        else: 
            object_id = None
        if object_id is not None:
            return {
                'message': 'Объект уже существует',
                'object_id': object_id}
        with self.engine.connect() as connection:
            session = Session(bind=self.engine)
            match table_name:
                case 'users':
                    object_id = session.scalars(
                        insert(Users).returning(Users.user_id),
                        [
                            {
                                'name': values['name'],
                                'phone': values['phone'],
                                'flat_number': values['flat_number']
                            }
                        ]
                    ).all()
                case 'dog':
                    object_id = session.scalars(
                        insert(Dog).returning(Dog.dog_id),
                        [
                            {
                                'dog_name': values['dog_name'],
                                'dog_description': values['dog_description'],
                                'user_id': values['user_id']
                            }
                        ]
                    ).all()
                case 'time_price':
                    object_id = session.scalars(
                        insert(Time_price).returning(Time_price.time_id),
                        [
                            {
                                'hour_minute': values['hour_minute'],
                                'price': values['price']
                            }
                        ]
                    ).all()
                case 'walk':
                    busy_time = session.query(Walk.start_date).filter(and_(Walk.start_date==values['start_date'],Walk.status!='RJCT')).all()
                    if len(busy_time) >= 2:
                        return {'error': 'Время уже занято'}

                    user_id = self.insert(table_name='users', values={'name': values['name'], 'phone': values['phone'],'flat_number': values['flat_number']})['object_id']
                    dog_id = self.insert(table_name='dog', values={'dog_name': values['dog_name'],'dog_description': values['dog_description'],'user_id': user_id})['object_id']

                    price = self.check_exist_object(table_name='time_price', values={'hour_minute': values['start_date'][11:]})

                    if not price:
                        return {'error': 'Вы не создали цену для времени'}

                    object_id = self.check_exist_object(table_name='walk',values={'start_date': values['start_date'],'dog_id': dog_id})
                    if object_id is not None:
                        return {
                            'message': 'Объект уже существует',
                            'object_id': object_id}
                    
                    object_id = session.scalars(
                        insert(Walk).returning(Walk.walk_id),
                        [
                            {
                                'start_date': values['start_date'],
                                'hour_minute': values['start_date'][11:],
                                'dog_id': dog_id,
                                'status': 'CRTD',
                                'price': price,
                                'end_date': datetime.strptime(values['start_date'],"%Y-%m-%d %H:%M") + timedelta(minutes=30)
                            }
                        ]
                    ).all()

            session.commit()
            session.close()
        return {'message': 'Объект сохранен',
                'object_id': object_id[0]}

    @logger.catch
    def update(self, table_name: str, values: dict) -> dict:
        """
        Функция для обновления данных в базе данных
        Parameters
        ----------
        table_name: str
            Название таблицы
            Пример: 'walk'
        values: dict
            Словарь из значений, необходимый для изменения строки в таблице
            Пример: {'walk_id': 1
                     'status': 'ACSS'}
            status может быть либо 'ACSS' (принято), либо 'RJCT' (отклонено), либо 'CRTD' (создано)
        Returns
        -------
        dict
            {'message': 'Значение успешно изменено'}
        """
        with self.engine.connect() as connection:
            session = Session(bind=self.engine)
            match table_name:
                case 'walk':
                    session.scalars(
                        update(Walk)
                        .where(Walk.walk_id == values['walk_id'])
                        .values(status=values['status'], who_walking=values['who_walking']).returning(Walk.walk_id)
                    )
                case 'time_price':
                    session.scalars(
                        update(Time_price)
                        .where(Time_price.hour_minute == values['hour_minute'])
                        .values(price=values['price']).returning(Time_price.time_id)
                    )
            session.commit()
            session.close()
        return {'message': 'Значение успешно изменено'}

    
    @logger.catch
    def check_exist_object(self, table_name: str, values: dict) -> int:
        """
        Функция для проверки существования объекта
        Parameters
        ----------
        table_name: str
            Название таблицы
            Пример: 'walk'
        values: dict
            Словарь из значений, необходимые для проверки наличия строк в таблице
            Пример: {'dog_id': 1
                     'start_date': '2024-01-30 14:00'}
        Returns
        -------
        int
            id объекта
        """
        with self.engine.connect() as connection:
            session = Session(bind=self.engine)
            match table_name:
                case 'users':
                    object_id = session.query(Users.user_id).filter(and_(Users.phone==values['phone'],Users.flat_number==values['flat_number'])).all()
                case 'dog':
                    object_id = session.query(Dog.dog_id).filter(Dog.dog_name==values['dog_name']).all()
                case 'walk':
                    object_id = session.query(Walk.walk_id).filter(and_(Walk.dog_id==values['dog_id'],Walk.start_date==values['start_date'])).all()
                case 'time_price':
                    object_id = session.query(Time_price.price).filter(Time_price.hour_minute==values['hour_minute']).all()
                case _:
                    object_id = []
            session.commit()
            session.close()
            if len(object_id) == 0:
                return None
            else:
                return object_id[0][0]
            
    @logger.catch            
    def get_all_walks(self, current_date: str = None, status: str = None) -> list:
        """
        Функция для получения всех заказов по указанной дате и статусу (статус опционален)
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
        list
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
        """
        with self.engine.connect() as connection:
            items = []
            query = f''' SELECT  
                                walk.walk_id,
                                walk.start_date,
                                walk.end_date,
                                walk.created_at,
                                walk.status,
                                walk.price,
                                dog.dog_name,
                                dog.dog_description, 
                                users.phone, 
                                users.name as user_name,
                                walk.who_walking
                        FROM dog
                            INNER JOIN walk
                                ON dog.dog_id = walk.dog_id
                            INNER JOIN users
                                ON dog.user_id = users.user_id
                        WHERE (1=1)
                    '''
            if current_date is not None:
                query += f'''AND walk.start_date >= '{current_date} 00:00'
                            AND walk.start_date <='{current_date} 23:59' '''
            if status is not None:
                query += f" AND walk.status = '{status}' "


            walks = connection.execute(text(query))

            for walk in walks:
                    item = {
                        'walk_id': walk[0],
                        'start_date': datetime.strftime(walk[1],"%Y-%m-%d %H:%M"),
                        'end_date': datetime.strftime(walk[2],"%Y-%m-%d %H:%M"),
                        'created_at': datetime.strftime(walk[3],"%Y-%m-%d %H:%M"),
                        'status': walk[4],
                        'price': walk[5],
                        'dog_name': walk[6],
                        'dog_description':walk[7],
                        'phone': walk[8],
                        'user_name':walk[9],
                        'who_walking': walk[10]}
                    items.append(item)
            return items
        
    @logger.catch
    def create_price(self,hour_minute: str|None = None,price: float|None = None) -> dict:
        """
        Функция, устанавливающая цену на время
        Parameters
        ----------
        hour_minute: str
            Время прогулки в формате ЧЧ:ММ
            Пример: '14:30' (если нужно установить цены на всё время, тогда значение оставить пустым)
        price: float
            Цена прогулки
            Пример: 400.00
        Returns
        -------
        dict
            {'error': str}
            или
            {'message': str}
        """
        if not hour_minute:
            prices = None

            with self.engine.connect() as connection:
                query = f'''SELECT * FROM time_price'''
                prices = connection.execute(text(query))
            count_price = 0
            for pr in prices:
                count_price+=1
                break
            for i in range(7,24):
                if i < 10:
                    hour = f"0{i}"
                else:
                    hour = f"{i}"
                if not price:
                    price = 500
                if count_price == 0:
                    self.insert(table_name='time_price', values={'hour_minute': hour+':00','price': price})
                    if i != 23:
                        self.insert(table_name='time_price', values={'hour_minute': hour+':30','price': price})
                else:
                    self.update(table_name='time_price', values={'hour_minute': hour+':00','price': price})
                    if i != 23:
                        self.update(table_name='time_price', values={'hour_minute': hour+':30','price': price})
            return {'message': 'Цены добавлены'}
        else:
            if not price:
                return {'error': 'Не указана цена'}
            else:
                self.update(table_name='time_price', values={'hour_minute': hour_minute,'price': price})
            return {'message': 'Цена изменена'}

