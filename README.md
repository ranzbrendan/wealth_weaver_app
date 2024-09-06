# WEALTH WEAVER
#### Video Demo: [Wealth Weaver App [CS50x Final Project]](https://youtu.be/tsO5AlyXQ-k?si=1NhTtpIAZ5Jua8SW)
### Description

```
Wealth Weaver is a simple financial tracker web app which aids users in managing their financial transactions. The app was designed to make it as simple and efficient as possible for the user. Main features include dashboard page which showcases summary statistics and visualizations of user expenses, and a transaction page wherein users can add or delete transactions, and also view their transaction history.

This version will not be the last one, as the finance web app will still be improved in the future.
```
---
### Files Included
#### `app.py`

The file `app.py` serves as the connection between the backend and frontend of the web app with the help of the Flask framework.

#### `helpers.py`

This file is basically a modified and trimmed down version of the `helpers.py` from WEEK9. Included functions are the apology (still used it), login requirement, and monetary unit symbol formatting (uses ₱ instead of $).

#### `finance.db`

The storage for all the data which includes the user info, transactions, and categories.

#### `layout.html`

Layout of every html file was established with the `layout.html`, which mainly includes the head with all the required style and script import declarations, the footer, the navbar, along with other bootstrap components such as modals and toasts connected with the navbar.

#### `index.html`

Serves as the initial landing page of newcomers, or users who have logged out of their sessions. This page invites people to start tracking their money using this web app. Users will only be redirected to either the registration or login page.

#### `login.html`

The login page which requires the user's username and password. Entering the correct credentials will send the user to their dashboards. If entered values are incorrect, they will be redirected to the apology page.

The navbar also shows the option to register, for those who do not have an account yet.

#### `register.html`

To create an account, users need to enter a username and matching passwords. If the account creation is successful, users will be sent directly to the dashboard page. On the other hand, incorrect values will redirect the user to the apology page.

#### `dashboard.html`

Showcases the summary of a user's financial status, mainly their expenses. For users who have just created their account and have no transactions added yet, a message is shown at the top which tells the user to get started by adding their current account balance.

- **Navigation:** The navbar has been modified, and it now shows `Dashboard`, `Transactions`, and `My Account` options.

- **Data Visualization:** Displayed on the right side is a visualization of the user's expenses using a line graph. The default graph is based on a daily timescale, but users can change this by clicking on the 3 other options on the left side of the graph.

- **Aggregated Expenses:** The bottom row shows the aggregations of user expenses for the current date, last week, last month, and their average monthly expenses.

- **Account Balance:** The user's account balance can be shown by clicking on the `Account Balance` button right below the welcome message.

#### `transactions.html`

This page allows you to track your income and expenses. Here are its functionalities:

- **Viewing Transaction History:** The user's transaction history is shown which allows them to check and analyze their own spending patterns aside from using the dashboard.

- **Adding Transactions:** Adding a transaction can be done by submitting the form on the top of the page. All except the description field is required to have inputs.

 - **Adding Categories:** For starters, no categories are listed yet so they will have to add by clicking on the "Add New Category" select option. This will trigger a modal wherein users will enter and save a new category. All category names will be capitalized automatically. Leaving the transactions page will result to deletion of categories which have not yet been included in any added transactions.

- **Deleting Transactions:** Listed transactions can also be deleted by clicking on the trash bin icon beside the transaction row of your choosing.

- **Description Tooltips:** Hovering over the transaction rows will reveal their description through a tooltip.

#### `apology.html`

Incorrect inputs in the login and registration pages will lead you to this apology page. This was adopted from the same html file in CS50x's week 9 finance probset (because the cat looks cute). The page shows an image of a grumpy cat with an error message.

---

### Other Features
#### `My Account Navbar`

- **Modify Account:** Includes options to change your account's username or password through modals, or log out from your current session.

- **Status Updates:** The modals have forms which requires input from the user, and will have to be verified if the entered values are correct. Status updates are shown via toasts on the lower right corner to announce if the change is successful or not. Unsuccessful attempts will show a toast with a light-red background and tells the user to try again.



