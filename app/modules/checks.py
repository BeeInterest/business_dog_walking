from datetime import datetime
import re
from loguru import logger


class Checks:

    @logger.catch 
    def check_time_walk(self, check_time: str) -> dict:
        """
        Функция, проверяющая время начала прогулки
        Parameters
        ----------
        check_time: str
            Дата начала прогулки
            Пример: '2024-01-30 14:30'
        Returns
        -------
        dict
            {'error': str}
            или
            {'check_time': str}
        """

        if re.fullmatch(r"\d{2}.\d{2}.\d{4} \d{2}:\d{2}",check_time):
            check_time_format = f"{check_time[6:10]}-{check_time[3:5]}-{check_time[0:2]}{check_time[10:]}"
    
        try:
            check_time_format = datetime.strptime(check_time,"%Y-%m-%d %H:%M")
        except:
            return 'Неправильный формат времени'
        
        error = ''
        if check_time_format < datetime.now():
            error += 'Дата должна быть в будущем. '
        if datetime.strptime(check_time[11:], '%H:%M') < datetime.strptime("07:00", '%H:%M') or datetime.strptime(check_time[11:], '%H:%M') > datetime.strptime("23:00", '%H:%M'):
            error += 'Время выгула должно быть не раньше 7 утра и не позже 11 вечера. '
        if check_time[14:] != '00' and check_time[14:] != '30':
            error += 'Время выгула должно начинаться либо в начале часа, либо в половину. '
        
        if error != '':
            return {'error': error}
        else:
            return {'check_time': check_time}
    
    @logger.catch 
    def check_current_date(self,current_date: str) -> dict:
        """
        Функция, проверяющая указанную дату для выдачи всех заказов
        Parameters
        ----------
        current_date: str
            Дата, по которой будет осуществлён поиск заказов
            Пример: '2024-01-30'
        Returns
        -------
        dict
            {'error': str}
            или
            {'current_date': str}
        """

        if re.fullmatch(r"\d{2}.\d{2}.\d{4}",current_date):
            current_date = f"{current_date[6:]}-{current_date[3:5]}-{current_date[0:2]}"
        try:
            datetime.strptime(current_date,"%Y-%m-%d")
        except:
            return {'error': 'Неправильный формат времени'}
        return {'current_date':current_date}
    
    @logger.catch 
    def check_phone(self, check_phone: str) -> dict:
        """
        Функция, проверяющая телефон
        Parameters
        ----------
        check_phone: str
            Номер телефона
            Пример: '89772234567'
        Returns
        -------
        dict
            {'error': str}
            или
            {'check_phone': str}
        """
        if len(check_phone) > 12 or len(check_phone) < 11:
            return {'error': 'Неправильная длина номера телефона'}
        if check_phone[:2] != "+7" and check_phone[0] != '8':
            return {'error':'Неправильный формат номера телефона'}
        if len(check_phone) == 12:
            check_phone = '8'+check_phone[2:]
        return {'check_phone': check_phone}
        