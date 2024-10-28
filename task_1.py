from collections import UserDict
from datetime import datetime, timedelta

""" базовий клас Field для обробки загальних фукцій полів"""
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        """ 
        Перетворюємо значення поля на рядкове представлення 
        """
        return str(self.value)

  
""" клас Name успадковвує Field, представляє ім'я контакту """
class Name(Field):
    pass

""" клас Phone успадковвує Field, представляє номер телефону контакту"""
class Phone(Field):
    
    """ініціалізуємо телефон з переввіркою на 10-значний номер"""
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError ("Invalid phone number. Must contain exactly 10 digits")
        super().__init__(value) #викликає конструктор Field для збереження значенння

""" клас Birthday успадковує Field і представляє день народження"""        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
            # перевірка коректності даних та перетворення рядка на об'єкт datetime
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

"""клас Record для обробки інформаціі про окремий контакт"""
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        
    def remove_phone(self, phone_value):
        self.phones = [phone for phone in self.phones if phone.value != phone_value]
        
    def edit_phone(self, old_phone_value, new_phone_value):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone_value:
                self.phones [i] = Phone(new_phone_value)
                return
        raise ValueError("Phone number not found")    
        
    def find_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                return phone
        return None

    def __str__(self): # рядкове предсталення телефону 
        return f"Contact name: {self.name.value}, phones: {', '.join(p.value for p in self.phones)}"
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

""" клас AddressBook успадковує UserDict, є колекцією записів """
class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")
        
    def get_upcoming_birthdays (self, days=7):
        today = datetime.today().date() # отримуємо поточну дату
        upcoming_birthdays = [] # список для збереження найближчих днів народження
    
        for record in self.data.values():
            if record.birthday:
                # отримуємо день народження на поточний рік
                birthday_this_year = record.birthday.value.replace(year=today.year).date()

                # якщо день народження вже пройшов цього року, обираємо наступний рік
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                
                # перевіряємо чи день народження припадає на наступний тиждень
                days_left = (birthday_this_year - today).days
                if 0 <= days_left <= days:
                    # якщо день народження припадає на суботу чи неділю, переносимо привітання на понеділок    
                    if birthday_this_year.weekday() in (5,6):
                        birthday_this_year += timedelta (days=(7-birthday_this_year.weekday()))
                
                    # додаємо запис до списку з ім'ям та датою привітання        
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime("%d-%m-%Y")
                    }) 
            
        return upcoming_birthdays 
                
# перевірка

address_book = AddressBook()

record1 = Record("Alice")
record1.add_birthday("25.10.1990")  # Наприклад, день народження 25 жовтня
address_book.add_record(record1)

record2 = Record("Bob")
record2.add_birthday("30.10.1985")  # День народження 30 жовтня
address_book.add_record(record2)

record3 = Record("Charlie")
record3.add_birthday("01.11.1992")  # День народження 1 листопада
address_book.add_record(record3)

record4 = Record("Diana")
record4.add_birthday("27.10.1995")  # День народження 27 жовтня
address_book.add_record(record4)

upcoming_birthdays = address_book.get_upcoming_birthdays(days=7)

print("Upcoming birthdays in the next 7 days:")
for entry in upcoming_birthdays:
    print(f"Name: {entry['name']}, Congratulation Date: {entry['congratulation_date']}")