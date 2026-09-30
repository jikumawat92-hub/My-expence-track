import json
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


FILE = "expenses.json"


class ExpenseApp(App):

    def build(self):
        self.data = self.load_data()

        main = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        self.balance_label = Label(
            text="",
            font_size=24,
            size_hint_y=None,
            height=90
        )
        main.add_widget(self.balance_label)

        self.amount = TextInput(
            hint_text="Enter amount",
            input_filter="float",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        main.add_widget(self.amount)

        self.category = Spinner(
            text="Category",
            values=(
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Other"
            ),
            size_hint_y=None,
            height=50
        )
        main.add_widget(self.category)

        buttons = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )

        income_btn = Button(text="Add Income")
        expense_btn = Button(text="Add Expense")

        income_btn.bind(on_press=self.add_income)
        expense_btn.bind(on_press=self.add_expense)

        buttons.add_widget(income_btn)
        buttons.add_widget(expense_btn)

        main.add_widget(buttons)

        self.message = Label(
            text="Enter an amount",
            font_size=16,
            size_hint_y=None,
            height=40
        )
        main.add_widget(self.message)

        history_title = Label(
            text="Transaction History",
            font_size=20,
            size_hint_y=None,
            height=40
        )
        main.add_widget(history_title)

        scroll = ScrollView()

        self.history_layout = BoxLayout(
            orientation="vertical",
            spacing=5,
            size_hint_y=None
        )

        self.history_layout.bind(
            minimum_height=self.history_layout.setter("height")
        )

        scroll.add_widget(self.history_layout)
        main.add_widget(scroll)

        self.update_balance()
        self.update_history()

        return main

    def load_data(self):
        if os.path.exists(FILE):
            try:
                with open(FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                data.setdefault("income", 0)
                data.setdefault("expense", 0)
                data.setdefault("transactions", [])

                return data

            except Exception:
                pass

        return {
            "income": 0,
            "expense": 0,
            "transactions": []
        }

    def save_data(self):
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                indent=4,
                ensure_ascii=False
            )

    def get_amount(self):
        try:
            amount = float(self.amount.text)

            if amount <= 0:
                return None

            return amount

        except ValueError:
            return None

    def add_income(self, instance):
        amount = self.get_amount()

        if amount is None:
            self.message.text = "Please enter a valid amount"
            return

        self.data["income"] += amount

        self.data["transactions"].append({
            "type": "Income",
            "amount": amount,
            "category": "Income",
            "date": datetime.now().strftime("%d-%m-%Y %H:%M")
        })

        self.save_data()

        self.amount.text = ""
        self.message.text = "Income added successfully"

        self.update_balance()
        self.update_history()

    def add_expense(self, instance):
        amount = self.get_amount()

        if amount is None:
            self.message.text = "Please enter a valid amount"
            return

        if self.category.text == "Category":
            self.message.text = "Please select a category"
            return

        self.data["expense"] += amount

        self.data["transactions"].append({
            "type": "Expense",
            "amount": amount,
            "category": self.category.text,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M")
        })

        self.save_data()

        self.amount.text = ""
        self.message.text = "Expense added successfully"

        self.update_balance()
        self.update_history()

    def update_balance(self):
        balance = (
            self.data["income"]
            - self.data["expense"]
        )

        self.balance_label.text = (
            f"Balance: ₹{balance:.2f}\n"
            f"Income: ₹{self.data['income']:.2f}    "
            f"Expense: ₹{self.data['expense']:.2f}"
        )

    def update_history(self):
        self.history_layout.clear_widgets()

        transactions = self.data["transactions"]

        if not transactions:
            self.history_layout.add_widget(
                Label(
                    text="No transactions yet",
                    size_hint_y=None,
                    height=40
                )
            )
            return

        for index in range(len(transactions) - 1, -1, -1):

            transaction = transactions[index]

            row = BoxLayout(
                size_hint_y=None,
                height=65,
                spacing=5
            )

            if transaction["type"] == "Income":
                sign = "+"
            else:
                sign = "-"

            info = Label(
                text=(
                    f"{sign} ₹{transaction['amount']:.2f}\n"
                    f"{transaction['category']} | "
                    f"{transaction['date']}"
                )
            )

            delete_btn = Button(
                text="Delete",
                size_hint_x=None,
                width=80
            )

            delete_btn.bind(
                on_press=lambda btn, i=index:
                self.confirm_delete(i)
            )

            row.add_widget(info)
            row.add_widget(delete_btn)

            self.history_layout.add_widget(row)

    def confirm_delete(self, index):
        transaction = self.data["transactions"][index]

        content = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        label = Label(
            text=(
                f"Delete this transaction?\n\n"
                f"{transaction['type']}: "
                f"₹{transaction['amount']:.2f}"
            )
        )

        buttons = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )

        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")

        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)

        content.add_widget(label)
        content.add_widget(buttons)

        popup = Popup(
            title="Confirm Delete",
            content=content,
            size_hint=(0.8, 0.4)
        )

        yes_btn.bind(
            on_press=lambda x:
            self.delete_transaction(index, popup)
        )

        no_btn.bind(on_press=popup.dismiss)

        popup.open()

    def delete_transaction(self, index, popup):
        transaction = self.data["transactions"][index]

        if transaction["type"] == "Income":
            self.data["income"] -= transaction["amount"]
        else:
            self.data["expense"] -= transaction["amount"]

        del self.data["transactions"][index]

        self.save_data()

        popup.dismiss()

        self.update_balance()
        self.update_history()

        self.message.text = "Transaction deleted"


if __name__ == "__main__":
    ExpenseApp().run()
