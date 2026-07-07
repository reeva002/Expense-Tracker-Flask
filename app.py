from flask import Flask,render_template,request
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app=Flask(__name__)

expenses=[]

@app.route('/')
def home():
     # 1. Calculate Total Amount
    total_spent = 0
    for e in expenses:
        total_spent += int(e['amount'])
    
    # 2. Render HTML with data
    return render_template('index.html', expenses=expenses, total=total_spent)

def predict_category(item):
    try:
        prompt = f"""
        Predict the expense category for this item: {item}

        Choose only one category from:
        Food, Travel, Shopping, Bills

        Return only the category name.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception:
        return "Other"

@app.route('/add', methods=['POST'])
def add_expense():
    # 1. Get Form Data
    item = request.form.get('item')
    category = predict_category(item)
    amount = request.form.get('amount')

    # 2. Add to List
    if item and amount:
        expenses.append({
            'item': item,
            'category': category,
            'amount': amount
        })

    return home()

@app.route('/ai')
def ai_insights():
    try:
        expense_text = ""

        for e in expenses:
            expense_text += f"{e['item']} - {e['category']} - ₹{e['amount']}\n"

        prompt = f"""
        You are a financial advisor.

        These are my expenses:
        {expense_text}

        Tell me:
        1. Where I spend the most.
        2. How I can save money.
        3. Give 3 simple suggestions.

        Keep the answer under 100 words.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        return response.text

    except Exception:
        return "AI service is temporarily unavailable. Please try again in a few minutes."

@app.route('/clear')
def clear_expenses():
    expenses.clear() # Deletes everything in the list
    return home()

if __name__ == '__main__':
    app.run(debug=True)