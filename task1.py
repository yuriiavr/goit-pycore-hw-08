from datetime import datetime, timedelta
import re
import pickle

class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    def __init__(self, name):
        if not isinstance(name, str) or not name:
            raise ValueError("Name must be a non-empty string")
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone):
        if not self.validate_phone(phone):
            raise ValueError("Invalid phone number format. Use +380XXXXXXXXX")
        super().__init__(phone)

    @staticmethod
    def validate_phone(phone):
        return bool(re.match(r'^\+380\d{9}$', phone))


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def get_birthday(self):
        return self.birthday.value if self.birthday else None


class AddressBook:
    def __init__(self):
        self.contacts = {}

    def add_record(self, record):
        self.contacts[record.name.value] = record

    def find(self, name):
        return self.contacts.get(name)

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now()
        next_week = today + timedelta(days=7)

        for record in self.contacts.values():
            if record.birthday:
                birthday = record.get_birthday()
                if (birthday.month == today.month and birthday.day >= today.day) or \
                   (birthday.month == next_week.month and birthday.day <= next_week.day):
                    upcoming_birthdays.append(record.name.value)

        return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return wrapper


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError("Please provide both name and birthday.")
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    record.add_birthday(birthday)
    return f"Birthday for {name} added."


@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise ValueError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    birthday = record.get_birthday()
    return f"{name}'s birthday is on {birthday.strftime('%d.%m.%Y')}" if birthday else f"{name} has no birthday recorded."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "Upcoming birthdays: " + ", ".join(upcoming_birthdays)


def parse_input(user_input):
    return user_input.split()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
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
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Please provide both name and phone number.")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise ValueError("Please provide name, old phone number, and new phone number.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    for phone_record in record.phones:
        if phone_record.value == old_phone:
            phone_record.value = new_phone
            return f"Updated {name}'s phone from {old_phone} to {new_phone}."
    raise ValueError(f"Phone {old_phone} not found for {name}.")


@input_error
def show_phone(args, book: AddressBook):
    if len(args) < 1:
        raise ValueError("Please provide a name.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    phones = ", ".join(phone.value for phone in record.phones)
    return f"{name}'s phone numbers: {phones}"


@input_error
def show_all_contacts(book: AddressBook):
    if not book.contacts:
        return "No contacts in the address book."
    return "\n".join([f"{name}: {', '.join(phone.value for phone in record.phones)}" for name, record in book.contacts.items()])


if __name__ == "__main__":
    main()
