import string
from typing import Tuple, List


ALPHABET = string.ascii_lowercase
ALIST: List[str] = list(ALPHABET)

def shift_character(ch: str, shift: int, direction: int) -> str:
    if ch.isalpha():
        base = ord('a')
        idx = (ord(ch.lower()) - base + direction * (shift % 26)) % 26
        return chr(base + idx)
    return ch 

def encode(input_text: str, shift: int) -> Tuple[List[str], str]:
    encoded = ''.join(shift_character(ch, shift, +1) for ch in input_text)
    return ALIST, encoded

def decode(input_text: str, shift: int) -> str:
     return ''.join(shift_character(ch, shift, -1) for ch in input_text)


import datetime

class BankAccount:
    def __init__(self, name="Rainy", ID="1234", creation_date=None, balance=0):
        if creation_date is None:
            creation_date = datetime.date.today()
        if not isinstance(creation_date, datetime.date):
            raise Exception("creation_date must be datetime.date")
        if creation_date > datetime.date.today():
            raise Exception("creation_date cannot be in the future")

        self.name = name
        self.ID = ID
        self.creation_date = creation_date
        self.balance = float(balance)

    def deposit(self, amount):
        if amount is None or amount < 0:
            print(f"Balance: {self.balance:.2f}")
        else:
            self.balance += amount
            print(f"Balance: {self.balance:.2f}")

    def withdraw(self, amount):
        if amount is None:
            print(f"Balance: {self.balance:.2f}")
        else:
            self.balance -= amount
            print(f"Balance: {self.balance:.2f}")

    def view_balance(self):
        return self.balance

import datetime

class SavingsAccount(BankAccount):
    MIN_DAYS = 180
    
    def withdraw(self, amount):
        age_days = (datetime.date.today() - self.creation_date).days
        if amount is None:
            print(f"Balance: {self.balance:.2f}")
        elif age_days < self.MIN_DAYS:
            print(f"Balance: {self.balance:.2f}")
        elif amount > self.balance:
            print(f"Balance: {self.balance:.2f}")
        else:
            self.balance -= amount
            print(f"Balance: {self.balance:.2f}")


class CheckingAccount(BankAccount):
    OVERDRAFT_FEE = 30

    def withdraw(self, amount):
        if amount is None:
            print(f"Balance: {self.balance:.2f}")
        else:
            self.balance -= amount
            if self.balance < 0:
                self.balance -= self.OVERDRAFT_FEE
            print(f"Balance: {self.balance:.2f}")
