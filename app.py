import streamlit as st
import pandas as pd
from datetime import date

from database import (
    create_table,
    add_expense,
    get_expenses,
    get_total_spending,
    get_category_spending,
    get_monthly_spending,
    delete_expense,
    update_expense,
    save_monthly_budget,
    get_monthly_budget,
    get_monthly_total,
    filter_expenses
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
    }

    /* Make metric text readable on white cards */
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #1e293b;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    h1, h2, h3 {
        color: #1e293b;
    }

    </style>
""", unsafe_allow_html=True)


create_table()

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("💰 Expense Tracker")
st.sidebar.write("Manage your personal finances")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Expense",
        "Manage Expenses",
        "Budget",
        "Reports"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Personal Expense Tracker | Python + SQLite")


# --------------------------------------------------
# 1. DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.title("📊 Dashboard")
    st.write("Overview of your spending and financial activity.")

    total_spending = get_total_spending()
    expenses = get_expenses()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Spending",
            f"₹{total_spending:,.2f}"
        )

    with col2:
        st.metric(
            "Total Transactions",
            len(expenses)
        )

    st.divider()

    # Category analytics
    st.subheader("📊 Spending by Category")

    category_data = get_category_spending()

    if category_data:
        category_chart_data = {
            "Category": [row[0] for row in category_data],
            "Amount": [row[1] for row in category_data]
        }

        st.bar_chart(
            category_chart_data,
            x="Category",
            y="Amount"
        )
    else:
        st.info("No category data available yet.")

    st.divider()

    # Monthly analytics
    st.subheader("📅 Monthly Spending")

    monthly_data = get_monthly_spending()

    if monthly_data:
        monthly_chart_data = {
            "Month": [row[0] for row in monthly_data],
            "Amount": [row[1] for row in monthly_data]
        }

        st.bar_chart(
            monthly_chart_data,
            x="Month",
            y="Amount"
        )
    else:
        st.info("No monthly spending data available yet.")

    st.divider()

    # Recent expenses
    st.subheader("🧾 Recent Expenses")

    if expenses:
        st.dataframe(
            expenses[:5],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No expenses recorded yet.")


# --------------------------------------------------
# 2. ADD EXPENSE
# --------------------------------------------------

elif page == "Add Expense":
    st.title("➕ Add a New Expense")
    st.write("Enter the details of your expense below.")

    with st.form("expense_form"):
        expense_name = st.text_input("Expense Name")

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            value=100.0,
            step=10.0
        )

        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Education", "Other"]
        )

        expense_date = st.date_input(
            "Expense Date",
            value=date.today()
        )

        notes = st.text_input("Notes (optional)")

        submitted = st.form_submit_button("Save Expense")

        if submitted:
            if expense_name.strip():
                saved = add_expense(
                    expense_name.strip(),
                    amount,
                    category,
                    expense_date.isoformat(),
                    notes.strip()
                )

                if saved:
                    st.success("Expense saved successfully!")
                else:
                    st.error("Unable to save expense. Please try again.")

            else:
                st.error("Please enter an expense name.")


# --------------------------------------------------
# 3. MANAGE EXPENSES
# --------------------------------------------------

elif page == "Manage Expenses":

    st.title("📋 Manage Expenses")

    expenses = get_expenses()

    if expenses:

        st.subheader("All Saved Expenses")

        st.dataframe(
            expenses,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Delete expense
        st.subheader("🗑️ Delete Expense")

        delete_options = {
            f"ID {row['id']} - {row['expense_name']} (₹{row['amount']})": row['id']
            for row in expenses
        }

        selected_delete = st.selectbox(
            "Select expense to delete",
            list(delete_options.keys()),
            key="delete_expense"
        )

        if st.button("Delete Selected Expense"):

            delete_expense(delete_options[selected_delete])

            st.success("Expense deleted successfully!")
            st.rerun()

        st.divider()

        # Edit expense
        st.subheader("✏️ Edit Expense")

        edit_options = {
            f"ID {row['id']} - {row['expense_name']} (₹{row['amount']})": row
            for row in expenses
        }

        selected_label = st.selectbox(
            "Select expense to edit",
            list(edit_options.keys()),
            key="edit_expense"
        )

        selected = edit_options[selected_label]

        categories = [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Education",
            "Other"
        ]

        with st.form("edit_expense_form"):

            edited_name = st.text_input(
                "Expense Name",
                value=selected["expense_name"]
            )

            edited_amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                value=float(selected["amount"]),
                step=10.0
            )

            edited_category = st.selectbox(
                "Category",
                categories,
                index=(
                    categories.index(selected["category"])
                    if selected["category"] in categories else 0
                )
            )

            edited_date = st.date_input(
                "Expense Date",
                value=date.fromisoformat(selected["expense_date"])
            )

            edited_notes = st.text_input(
                "Notes",
                value=selected["notes"] or ""
            )

            update_button = st.form_submit_button("Save Changes")

            if update_button:

                if edited_name.strip():

                    update_expense(
                        selected["id"],
                        edited_name.strip(),
                        edited_amount,
                        edited_category,
                        edited_date.isoformat(),
                        edited_notes.strip()
                    )

                    st.success("Expense updated successfully!")
                    st.rerun()

                else:
                    st.error("Please enter an expense name.")

    else:
        st.info("No expenses available. Add your first expense.")


# --------------------------------------------------
# 4. MONTHLY BUDGET
# --------------------------------------------------

elif page == "Budget":

    st.title("💰 Monthly Budget Management")

    selected_month = st.date_input(
        "Select Month",
        value=date.today().replace(day=1),
        key="budget_month"
    )

    month_key = selected_month.strftime("%Y-%m")

    current_budget = get_monthly_budget(month_key)

    monthly_spending = get_monthly_total(month_key)

    remaining_budget = current_budget - monthly_spending

    st.divider()

    # Budget metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Monthly Budget",
            f"₹{current_budget:,.2f}"
        )

    with col2:
        st.metric(
            "Monthly Spending",
            f"₹{monthly_spending:,.2f}"
        )

    with col3:
        st.metric(
            "Remaining Budget",
            f"₹{remaining_budget:,.2f}"
        )

    # Budget warning
    if current_budget > 0:

        if remaining_budget < 0:
            st.error("⚠️ You have exceeded your monthly budget!")

        else:
            st.success(
                f"₹{remaining_budget:,.2f} remaining."
            )

        # Progress bar
        st.subheader("📈 Budget Usage")

        budget_percentage = monthly_spending / current_budget

        st.progress(min(budget_percentage, 1.0))

        st.write(
            f"You have used {budget_percentage * 100:.1f}% "
            "of your monthly budget."
        )

    else:
        st.info("Set a monthly budget to start tracking.")

    st.divider()

    # Save budget
    st.subheader("Set Your Monthly Budget")

    with st.form("budget_form"):

        monthly_budget = st.number_input(
            "Monthly Budget (₹)",
            min_value=0.0,
            value=float(current_budget),
            step=500.0
        )

        budget_submitted = st.form_submit_button("Save Budget")

        if budget_submitted:

            if monthly_budget > 0:

                save_monthly_budget(
                    month_key,
                    monthly_budget
                )

                st.success("Monthly budget saved successfully!")
                st.rerun()

            else:
                st.error("Please enter a budget greater than zero.")


# --------------------------------------------------
# 5. REPORTS AND CSV EXPORT
# --------------------------------------------------

elif page == "Reports":

    st.title("📑 Expense Reports")

    st.write("Filter your transactions and download expense reports.")

    st.subheader("🔎 Filter Expenses")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today().replace(day=1),
            key="report_start_date"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=date.today(),
            key="report_end_date"
        )

    selected_category = st.selectbox(
        "Select Category",
        [
            "All",
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Education",
            "Other"
        ],
        key="report_category"
    )

    if st.button("Apply Filters"):

        if start_date <= end_date:

            filtered_data = filter_expenses(
                start_date.isoformat(),
                end_date.isoformat(),
                selected_category
            )

            if filtered_data:

                st.subheader("📋 Filtered Expense Results")

                st.dataframe(
                    filtered_data,
                    use_container_width=True,
                    hide_index=True
                )

                filtered_df = pd.DataFrame(filtered_data)

                csv_data = filtered_df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="Download Filtered Expenses",
                    data=csv_data,
                    file_name="filtered_expenses.csv",
                    mime="text/csv"
                )

                filtered_total = sum(
                    row["amount"] for row in filtered_data
                )

                st.metric(
                    "Filtered Spending",
                    f"₹{filtered_total:,.2f}"
                )

            else:
                st.info("No expenses found for these filters.")

        else:
            st.error("Start date cannot be after end date.")

    st.divider()

    # Export all expenses
    st.subheader("📥 Export All Expenses")

    all_expenses = get_expenses()

    if all_expenses:

        all_df = pd.DataFrame(all_expenses)

        all_csv = all_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download All Expenses as CSV",
            data=all_csv,
            file_name="my_expenses.csv",
            mime="text/csv"
        )

    else:
        st.info("No expenses available to export.")