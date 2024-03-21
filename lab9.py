from collections import UserDict
import re
from datetime import datetime
from datetime import timedelta
import pickle

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Потрібен ПІБ!"
        except KeyError:
            return "Нема такого ПІБ!"
        except ValueError as e:
            return "Потрібен ПІБ та тел.!"#, e.args[0]
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу
		pass

class Birthday(Field):
    def __init__(self, value):
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Phone(Field):
    def __init__(self, in1: str):
        # Клас Phone:Реалізовано валідацію номера телефону (має бути перевірка на 10 цифр). - це привести до формату +380989456457
        phone = in1
        if in1 == None:
            raise ValueError("Потрібно 10 цифр")
        if len(phone)!=10:
            raise ValueError("Потрібно 10 цифр")
        # Видаліть всі символи, крім цифр та '+', з номера телефону
        pattern = r"[^1234567890]"
        replacement = ""
        phone = re.sub(pattern, replacement, phone)
        # чи номер не 10 цифр
        if len(phone)!=10:
            raise ValueError("Потрібно 10 цифр")
      
        self.value = phone

    def __str__(self):
        return self.value

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # додаемо ДР
    def add_birthday(self, sdate: str):
        self.birthday = Birthday(sdate)

    # додаемо тел
    def add_phone(self, tel: str): 
        self.phones.append(Phone(tel))
 
    def remove_phone(self, oldtel: str):
        for i, v in enumerate(self.phones):
            if v.value == Phone(oldtel).value:
               del(self.phones[i])
        
    def edit_phone(self, oldtel: str, newtel: str):
        for i, v in enumerate(self.phones):
              if v.value == Phone(oldtel).value:
                self.phones[i] = Phone(newtel)
                return "Телефон змінено"
        raise ValueError("Телефон не знайдено!")
      
    def find_phone(self, oldtel: str) -> Phone:
        for el in self.phones:
            if el.value == oldtel:
                return el
        return None
   
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, Rec: Record):
        self.data[Rec.name.value] = Rec

    def find(self, name: str) -> Record:
        return self.data.get(name)
        
    def delete(self, name: str):
        self.data.pop(name)
        return None
    
    def add_dr(self, name: str, dr: str):
        rec = self.find(name)
        if rec == None:
            rec = Record(name)
            rec.add_birthday(dr)
            self.add_record(rec)
        else:
            rec.add_birthday(dr)
        return "ДР додано"
     
    def add_contact(self, name: str, phone: str):
        rec = self.find(name)
        if rec == None:
            rec = Record(name)
            rec.add_phone(phone)
            self.add_record(rec)
        else:
            rec.add_phone(phone)
            self.add_record(rec)
        return "Контакт додано"
    
    def get_upcoming_birthdays(self):
        listall = []
        if self.data == None:
            return listall
        # поточна дата
        now = datetime.today().date()
        # Пройдіться по списку users та аналізуйте дати народження кожного
        for rec in self.data:
            if self.data[rec].birthday != None:
                date_user = self.data[rec].birthday.value
                # міняемо год на поточний
                date_user = date_user.replace(year=now.year)
                # Розрахунок кількості днів
                days_since = date_user.toordinal() - now.toordinal()
                # на тиждне?
                if days_since>=0 and days_since<=7:
                    # яка доба
                    iday = int(date_user.weekday())
                    if iday==5:
                        date_user = date_user + timedelta(days=2) # Додаємо 2 днів
                    elif iday==6:
                        date_user = date_user + timedelta(days=1) # Додаємо 2 днів
                    # нова дата ДН    
                    sdate = date_user.strftime("%d.%m.%Y")
                    s1 = f"Name: {self.data[rec].name} - DR: {sdate}"
                    listall.append(s1)
        return listall
    
def all_contact(self) -> str:
    listall = [f"{self.data[el1]}" for el1 in self.data]
    return "\n".join(listall)
    
@input_error    
def phone_contact(book: AddressBook, args):
    name = args[0]
    return book.find(name)

@input_error 
def change_contact(book: AddressBook, args):
    name, oldphone, newphone = args
    record = book.find(name)
    if record != None:
        record.edit_phone(oldphone, newphone)
        book.data[name] = record
        return "Контакт змінено"
    else:
        raise ValueError("ПІБ не знайдено!")

@input_error
def add_contact(book: AddressBook, args):
    name, phone = args
    return book.add_contact(name, phone)

@input_error
def add_birthday(book: AddressBook, args):
    name, dr = args
    return book.add_dr(name, dr)

@input_error
def show_birthday(book: AddressBook, args):
    name = args[0]
    return book.find(name)

@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()

def save_data(book: AddressBook, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl") -> AddressBook:
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено
       
def main():
    # book = AddressBook()
    book = load_data()
    
    # user_input = "add Toxa 1234567890"
    # command, *args = parse_input(user_input)
    # print(add_contact(book, args))
    # return 0

    # user_input = "add Den 0987654321"
    # command, *args = parse_input(user_input)
    # print(add_contact(book, args))

    # print(all_contact(book))

    # user_input = "phone Toxa"
    # command, *args = parse_input(user_input)
    # print(phone_contact(book, args))

    # user_input = "change Toxa 0987654321"
    # command, *args = parse_input(user_input)
    # print(change_contact(book, args))

    # print(all_contact(book))

    # user_input = "add-birthday Toxa 26.03.1979"
    # command, *args = parse_input(user_input)
    # print(add_birthday(book, args))

    # user_input = "add-birthday Den 25.02.1979"
    # command, *args = parse_input(user_input)
    # print(add_birthday(book, args))
    # print(all_contact(book))

    # user_input = "show-birthday Toxa"
    # command, *args = parse_input(user_input)
    # print(show_birthday(book, args))

    # user_input = "birthdays"
    # command, *args = parse_input(user_input)
    # print(birthdays(book))

    # return 0

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(book, args)) 

        elif command == "change":
            print(change_contact(book, args))

        elif command == "phone":
            print(phone_contact(book, args))

        elif command == "all":
            print(all_contact(book))

        elif command == "add-birthday":
            print(add_birthday(book, args))

        elif command == "show-birthday":
            print(show_birthday(book, args))

        elif command == "birthdays":
           print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()