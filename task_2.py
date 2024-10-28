from functools import wraps
from collections import UserDict
from datetime import datetime, timedelta
    
def input_error(func):
    """
    Декоратор для обробки помилок введення користувача. 
    Обробляє KeyError, ValueError, IndexError. 
    """
    @wraps (func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Error: Contact not found."
        except ValueError as e:
            return f"Error: {str(e)}"
        except IndexError:
            return "Error: Not enough arguments provided." 
    return inner


def parse_input(user_input):
    """ 
    Розбиває вхідний рядок на команду і аргументи.
    """
    cmd, *args = user_input.split()
    return  cmd.strip().lower(), args
   

""" базовий клас Field для обробки загальних фукцій полів"""
class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self): # перетворюємо значення поля на рядкове представлення 
        return str(self.value)

""" клас Name успадковвує Field, представляє ім'я контакту """
class Name(Field):
    pass

""" клас Phone успадковвує Field, представляє номер телефону контакту"""
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10: 
            raise ValueError ("Invalid phone number. Must contain exactly 10 digits")
        super().__init__(value) #викликає конструктор Field для збереження значенння

""" клас Birthday успадковує Field і представляє день народження"""        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
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

    def set_birthday(self, date_str):
        self.birthday = Birthday(date_str)
        
    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.today().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days
        
    def __str__(self): # рядкове предсталення телефону і дня народження
        phones = ", ".join(phone.value for phone in self.phones)
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Name: {self.name.value}, Phones: [{phones}], Birthday: {birthday_str}"
    

""" клас для адресної книги """
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
                birthday_this_year = record.birthday.value.replace(year=today.year)

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


@input_error
def add_contact(args, book: AddressBook):
    """ 
    Додає новий контакт до словника.
    """

    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if len(args) < 2:
        raise ValueError 
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    """
    Змінює телефон існуючого контакту.
    """
    name, old_phone, new_phone = args
    record = book.find(name)
    if len(args) < 2:
        raise ValueError 
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Contact {name} updated with new phone number {new_phone}."
    else:
        raise KeyError
    
@input_error
def show_phone(args, book):
    """ 
    Відображає телефон контакту.
    """
    name = args[0]
    record = book.find(name)
    if len(args) < 1:
        raise IndexError
    if record:
        return f"Phone number for {name}: {[phone.value for phone in record.phones]}"
    else:
        raise KeyError
 
@input_error    
def show_all(book):   
    """ 
    відображає всі контакти.
    """
    if book.data:
        return "\n".join([str(record) for record in book.data.values()])    
    return "No contacts found." 
    
@input_error
def add_birthday(args, book):
    """ 
    додає день народження до контакту
    """
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.set_birthday(birthday)
        return f"Birthday added for {name}."
    return "Contact not found"
        
@input_error
def show_birthday(args, book):
    """ 
    відображає всі дні народження.
    """
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name} birthday is on {record.birthday.value.strftime("%d.%m.%Y")}"
    return f"Birthday not set or contact not found"

@input_error
def birthdays( book):
    """ показує дні народження протягом наступного тижня"""
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"{entry['name']}: {entry['congratulation_date']}" for entry in upcoming_birthdays])
    return "No upcoming birthdays."


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
           print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))
            
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()




