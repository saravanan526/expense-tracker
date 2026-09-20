# Project Guide: Expense Tracker and Data Analytics Dashboard

This file helps you understand, present and explain the project (viva / interview).

---

## 1. Project Explanation

**Problem:** Students and beginners often do not know where their money goes each month.

**Solution:** A web application where the user adds daily expenses, and the app stores them in a MySQL
database and analyzes them: category-wise spending, monthly trend, payment-method usage, budget
utilization, month-to-month comparison, and fixed vs variable expenses.

**What the project demonstrates**

| Skill | Where |
|---|---|
| Python | All files |
| Authentication (registration, login, password hashing) | `auth.py`, `pages/login.py` |
| MySQL + SQL | `database.py`, `sql/database.sql` |
| Pandas (cleaning, grouping, aggregation, CSV) | `analysis.py`, `expense_history.py` |
| Matplotlib | `analysis.py` (chart functions) |
| REST API | `api.py` (currency exchange) |
| Streamlit | `app.py`, `pages/` |
| Exploratory Data Analysis | `analytics.py`, summary and comparison logic |

**How the files work together**

- `auth.py` - registration, login and password hashing (uses only Python's built-in `hashlib`).
- `database.py` - only file that talks to MySQL. Returns data as Pandas DataFrames.
- `analysis.py` - only file with calculations and charts (no Streamlit code inside).
- `api.py` - only file that calls the REST API.
- `pages/*.py` - only user interface code, each page has a `show()` function.
- `app.py` - creates the sidebar and runs the selected page.

---

## 2. Project Workflow

```text
User opens the app (app.py)
        |
   Not logged in? -> Login / Register page (auth.py) -> session stores user id
        |
User opens a page from the sidebar (app.py)
        |
        v
Page (pages/*.py) asks database.py for the LOGGED-IN USER's data   <--- parameterized SQL (WHERE user_id = %s)
        |
        v
Data comes back as a Pandas DataFrame
        |
        v
analysis.py cleans / groups / calculates (Pandas)
        |
        v
Result is shown as metrics, tables and Matplotlib charts (Streamlit)

Add Expense:  form -> validation -> INSERT into MySQL
History:      filters -> SQL WHERE/BETWEEN -> table -> to_csv() -> download
Currency:     amount -> requests.get(API) -> JSON -> rate x amount
```

---

## 3. Five-Minute Interview Explanation

"My project is an Expense Tracker and Data Analytics Dashboard built using Python, Streamlit, MySQL,
Pandas and Matplotlib.

The user can add daily expenses with date, category, amount, payment method and description. The data is
validated and stored in a MySQL table. I used four tables: `users` for accounts, `expenses` for daily spending, `budgets` for
monthly budgets and `recurring_expenses` for fixed payments like rent or internet. The last three have a `user_id` foreign key so each user sees only his or her own data. Users register and login, and passwords are stored as salted PBKDF2 hashes, not plain text.

On the Expense History page the user can filter by date range, category and payment method. I used SQL
`WHERE` and `BETWEEN` with parameterized queries, and the page shows the total, count, average and
highest expense of the filtered data. The same filtered data can be downloaded as a CSV file using
Pandas `to_csv()`.

The Analytics page uses SQL `GROUP BY` with `SUM()` to get category-wise, payment-method-wise, monthly
and daily totals. I convert these results into Pandas DataFrames, calculate percentages, and draw bar
and line charts using Matplotlib.

For budget analysis, the user sets a monthly budget. The app calculates remaining amount and utilization
percentage, and shows one of three messages using simple if-else conditions: normal spending below 80%,
nearing limit between 80 and 100%, and exceeded above 100%.

I also compare the current month with the previous month using `YEAR()` and `MONTH()` in SQL, and handle
special cases like no previous data or previous month total being zero. Recurring expenses are treated as
fixed expenses and normal daily expenses as variable expenses, and the app shows their percentages.

There is a currency converter that calls a public exchange-rate REST API using the `requests` library,
with error handling for timeouts and connection problems. The home page also shows a rule-based spending
summary made with plain Python calculations. No machine learning is used.

The database password is stored in a `.env` file, not in the code. I kept the code in separate files for
database, analysis, API and pages so it is easy to maintain."

---

## 4. Technical Interview Questions and Answers

**1. Why did you choose Streamlit?**
It lets me build a data web app using only Python, without HTML/CSS/JavaScript. It has built-in forms, tables and chart support, so it is good for data projects.

**2. Why MySQL instead of a CSV file or SQLite?**
MySQL is a proper relational database. It supports multiple tables, data types, constraints and SQL functions like `YEAR()` and `MONTH()`, and it is what companies commonly use.

**3. Explain your database design.**
Four tables: `users`, `expenses`, `budgets` and `recurring_expenses`. The last three have a `user_id` column that is a FOREIGN KEY to `users(id)` with `ON DELETE CASCADE`. In `budgets`, the pair (`user_id`, `month_year`) is UNIQUE, so each user has one budget per month.

**4. Why is `amount` DECIMAL(10,2) and not FLOAT?**
DECIMAL stores exact values, which is important for money. FLOAT can give rounding errors.

**5. What is a parameterized query and why did you use it?**
A query where user values are passed separately as `%s` placeholders instead of joining strings. It prevents SQL injection.

**6. What is SQL injection?**
An attack where a user enters SQL code as input (like `' OR '1'='1`) to change the query. Parameterized queries stop it.

**7. How does date filtering work?**
`WHERE expense_date BETWEEN %s AND %s`, combined with `AND category = %s` and `AND payment_method = %s` when those filters are selected. The WHERE part is built dynamically in `_build_where()`.

**8. Difference between WHERE and HAVING?**
WHERE filters rows before grouping; HAVING filters groups after `GROUP BY`. My project only needs WHERE.

**9. What does GROUP BY do in your project?**
It groups rows by category / payment method / date / month so `SUM(amount)` gives the total for each group.

**10. Why do you use `ORDER BY ... LIMIT`?**
To get the recent 5 expenses on the home page: `ORDER BY expense_date DESC LIMIT 5`.

**11. How do you calculate the monthly total?**
`SELECT SUM(amount) FROM expenses WHERE YEAR(expense_date) = %s AND MONTH(expense_date) = %s`.

**12. What is `INSERT ... ON DUPLICATE KEY UPDATE`?**
(`user_id`, `month_year`) is UNIQUE in the budgets table. If this user already has a budget for that month, MySQL updates it, otherwise it inserts a new row. So the user can change a budget without duplicates.

**13. What is the role of Pandas in your project?**
Data cleaning (`to_datetime`, `to_numeric`, `dropna`, `fillna`), grouping (`groupby`), aggregation (`sum`, `mean`, `idxmax`), percentage calculation, and CSV export (`to_csv`).

**14. What data cleaning did you do?**
Converted date and amount columns to proper types, removed rows with invalid values, and filled empty descriptions.

**15. How is the CSV export done?**
The filtered DataFrame is renamed to user-friendly column names, converted with `to_csv(index=False)`, encoded to bytes and given to `st.download_button`. The download uses the same filters as the table.

**16. Why Matplotlib?**
It is the basic Python plotting library and gives full control over charts. It is also a required skill for data analytics.

**17. How does the budget rule work?**
Utilization = (Spent / Budget) x 100. Below 80% = normal, 80 to 100% = nearing limit, above 100% = exceeded. If the budget is 0 or missing, the app shows a message instead of dividing by zero.

**18. How do you calculate month-over-month change?**
Difference = Current - Previous; Percentage = (Difference / Previous) x 100. If there is no previous month data or it is 0, the percentage is shown as N/A.

**19. How did you find the previous month when the current month is January?**
`previous_month()` returns `(year - 1, 12)` when month is 1, otherwise `(year, month - 1)`.

**20. What is the difference between fixed and variable expenses?**
Fixed expenses repeat regularly with a set amount (rent, internet). Variable expenses change from day to day (food, transport). Recurring expenses are treated as fixed; normal daily expenses as variable.

**21. How do you compare weekly / yearly recurring expenses with monthly ones?**
By converting to a monthly amount: weekly x 52 / 12, yearly / 12.

**22. What is a REST API?**
A way for programs to communicate over HTTP. The client sends a request to a URL and receives data, usually JSON.

**23. How does the currency converter work?**
`requests.get()` calls `https://open.er-api.com/v6/latest/USD`, the JSON response contains rates, I take the INR rate and multiply by the entered amount.

**24. How do you handle API failures?**
`try/except` for `Timeout`, `ConnectionError` and other `RequestException`, a timeout of 10 seconds, and checking the `result` field of the response. The user sees a simple error message.

**25. Why use a `.env` file?**
So the database password is not written in the code or uploaded to GitHub. `python-dotenv` loads it into environment variables and `os.getenv()` reads it.

**26. How is MySQL connection failure handled?**
`setup_database()` is called inside try/except in `app.py`. If it fails, an error message is shown and `st.stop()` stops the app.

**27. Why separate `database.py`, `analysis.py` and `pages/`?**
Separation of concerns: SQL in one place, calculations in one place, UI in one place. It is easier to read, test and change.

**28. How does Streamlit handle button clicks?**
Every interaction re-runs the script from top to bottom. `st.session_state` is used to remember values between runs, like the applied filters.

**29. How is your project different from an ML project?**
It only uses SQL, Pandas calculations and rule-based logic. There is no model training or prediction. It is a data analytics and EDA project.

**30. What are the limitations?**
No edit option for expenses, login is lost when the page is refreshed, and there is no password reset or limit on wrong password attempts.

**31. How does registration and login work?**
Registration validates the input (username format, email format, password length and strength, matching passwords), checks that the username and email are not already used, hashes the password and inserts the user. Login finds the user by username, hashes the entered password with the stored salt, and compares it with the stored hash. On success the user's id and name are saved in `st.session_state`.

**32. Why not store passwords as plain text?**
If the database is leaked, everyone's passwords are exposed. A hash cannot be reversed, so only the hash is stored.

**33. What is a salt and why is it used?**
A salt is a random value added to the password before hashing. Two users with the same password get different hashes, and pre-computed rainbow tables do not work. I generate a 16-byte salt with `os.urandom()` for every user and store it with the hash as `salt$hash`.

**34. Which hashing algorithm did you use?**
PBKDF2-HMAC-SHA256 from Python's `hashlib`, with 200,000 iterations. Repeating the hash many times makes brute-force guessing slow. Plain SHA-256 or MD5 alone is too fast for passwords.

**35. Why `hmac.compare_digest()` to compare hashes?**
It compares in constant time, so an attacker cannot learn anything from how long the comparison takes.

**36. How do you make sure one user cannot see another user's data?**
The user id comes from the server-side session, and every query has `WHERE user_id = %s` with that id. Deleting a recurring expense also checks the user id, so a user cannot delete someone else's row by guessing an ID.

**37. Why does the login message not say which one was wrong (username or password)?**
So an attacker cannot find out which usernames exist.

**38. What is `st.session_state`?**
A dictionary that Streamlit keeps for each browser session. Streamlit re-runs the script on every click, so session_state is used to remember the logged-in user between runs.

**39. What happens to old data when login was added later?**
On start-up the app checks if `user_id` columns exist. If not, it adds them with `ALTER TABLE`, and old rows are assigned to the first registered user.

---

## 5. Resume Project Description

**Expense Tracker and Data Analytics Dashboard** | Python, Streamlit, MySQL, SQL, Pandas, Matplotlib, REST API

- Built a Streamlit web application to record daily expenses in a MySQL database with input validation and parameterized SQL queries.
- Implemented user registration and login with salted PBKDF2 password hashing, and isolated each user's data using foreign keys and `user_id` filters.
- Wrote SQL queries using WHERE, BETWEEN, GROUP BY, ORDER BY, aggregate functions and MONTH()/YEAR() to filter and summarize spending data.
- Performed data cleaning and exploratory analysis using Pandas; created category, monthly, payment-method and daily trend charts using Matplotlib.
- Implemented monthly budget tracking, month-over-month comparison, recurring expense management and fixed vs variable expense analysis.
- Integrated a public currency exchange REST API using Python `requests` with error handling, and added CSV export of filtered reports.

**Short version (one line):**
Developed a multi-user Python + MySQL expense analytics dashboard with secure login (salted PBKDF2 password hashing), Streamlit, Pandas and Matplotlib that tracks spending, budgets and monthly trends.

---

## 6. Logical Testing Checklist (Step 9)

| Test | Expected result |
|---|---|
| Register with a short password / bad email / existing username | Clear error message for each problem, no account created |
| Login with wrong password or unknown username | "Invalid username or password." |
| Register two users and add expenses to each | Each user sees only his or her own data |
| Click Logout | Returns to the login screen, menu is hidden |
| Wrong MySQL password in `.env` | Red error message, app stops, no crash |
| Add expense with empty amount | "Amount cannot be empty." |
| Amount = 0 or negative | "Amount must be greater than 0." |
| Empty description | "Description cannot be empty." |
| Future date | "Date cannot be in the future." |
| History with no matching rows | "No expenses found for the selected filters." |
| Start date after end date | "Start date cannot be after the end date." |
| Reset Filter | All filters return to default, all rows visible |
| CSV download after filtering | File contains only the filtered rows |
| Budget = 0 | Not saved: "Budget must be greater than 0." |
| Spent between 80% and 100% of budget | Warning: "Budget nearing limit" |
| Spent above budget | Error: "Budget exceeded" |
| Previous month has no data | Percentage change shows N/A with a message |
| Fixed vs variable with no recurring expenses | Warning shown, fixed = 0 |
| Internet off in currency converter | "Could not connect to the internet / API server." |
| Empty database | Home page shows an info message and pages do not crash |

**Known limitations to mention honestly:** login is lost on page refresh, no password reset, no edit/delete for expenses, sample data can only be
loaded when the expenses table is empty, and recurring expenses are not automatically added to the
`expenses` table (they are only used for fixed vs variable analysis).

---

## 7. Possible Future Enhancements

- Stay logged in after refresh (cookies) and password reset by email
- Edit and delete expenses
- Category-wise budgets and email reminders
- Import expenses from a bank statement CSV
- Download charts as images or a PDF report
- Deploy on Streamlit Cloud with a cloud MySQL database
