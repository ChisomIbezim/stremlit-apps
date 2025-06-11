import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Simple Robo-Advisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- App Title and Description ---
st.title("Your Personal Robo-Advisor")
st.subheader("by Chisom Ibezim")
st.write(
    """
    Welcome to your personalized investment guide! Fill in the details in the sidebar
    to get a tailored asset allocation and a projection of your future wealth.

    **Disclaimer:** This is a simplified educational tool and should not be considered
    financial advice. Always consult with a qualified financial advisor before
    making investment decisions.
    """
)

# --- Investment Assumptions (Average Annual Returns) ---
# These are simplified for demonstration purposes. Real-world returns vary.
AVG_STOCK_RETURN = 0.08  # 8% average annual return for stocks
AVG_BOND_RETURN = 0.03   # 3% average annual return for bonds
INFLATION_RATE = 0.02    # 2% annual inflation rate (for real return calculation)

# --- Asset Allocation Strategy Based on Risk Tolerance ---
# Stocks (%) | Bonds (%)
ALLOCATION_STRATEGY = {
    "Conservative": {"Stocks": 30, "Bonds": 70},
    "Moderate":     {"Stocks": 60, "Bonds": 40},
    "Aggressive":   {"Stocks": 90, "Bonds": 10},
}

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("Your Financial Profile")

    # User Inputs
    age = st.slider("Your Current Age (Years)", min_value=18, max_value=80, value=30)
    investment_horizon = st.slider("Investment Horizon (Years)", min_value=1, max_value=50, value=20)
    current_savings = st.number_input("Current Savings ($)", min_value=0, value=10000, step=1000)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0, value=200, step=50)

    st.subheader("Your Risk Tolerance")
    risk_tolerance = st.radio(
        "How would you describe your risk tolerance?",
        ("Conservative", "Moderate", "Aggressive"),
        help="""
        * **Conservative:** Prioritizes capital preservation, lower potential returns, lower risk.
        * **Moderate:** Balances growth and preservation, moderate potential returns, moderate risk.
        * **Aggressive:** Prioritizes growth, higher potential returns, higher risk (willing to accept market volatility).
        """
    )

    st.markdown("---")
    if st.button("Calculate My Plan"):
        st.session_state.run_calculation = True
    else:
        # Initialize if not set, or reset if parameters changed
        if 'run_calculation' not in st.session_state:
            st.session_state.run_calculation = False
        # If parameters changed and it was previously run, reset to re-trigger
        # This is a bit of a hack as sliders don't trigger button clicks automatically
        # A more robust way might be to recalculate on every slider change.
        # For this example, we'll assume the button is needed to trigger.


# --- Core Logic Functions ---
def calculate_portfolio_return(risk_profile, stock_return, bond_return):
    """Calculates the weighted average expected annual return for the portfolio."""
    allocation = ALLOCATION_STRATEGY[risk_profile]
    stock_percent = allocation["Stocks"] / 100
    bond_percent = allocation["Bonds"] / 100
    expected_return = (stock_percent * stock_return) + (bond_percent * bond_return)
    return expected_return

def project_portfolio_growth(
    initial_savings,
    monthly_contribution,
    investment_horizon,
    annual_return
):
    """
    Projects portfolio growth year by year, considering initial savings
    and monthly contributions.
    """
    years = np.arange(investment_horizon + 1)
    portfolio_values = []
    current_value = initial_savings
    portfolio_values.append(current_value) # Value at Year 0

    # Convert annual return to monthly return
    monthly_return = (1 + annual_return)**(1/12) - 1

    for year in range(1, investment_horizon + 1):
        # Value of previous year's balance compounded for one year
        current_value = current_value * (1 + annual_return)

        # Value of monthly contributions compounded over the year
        # Future value of an ordinary annuity (PMT * (((1 + r_monthly)^n - 1) / r_monthly) )
        # n = 12 months, r_monthly
        fv_contributions_this_year = monthly_contribution * (((1 + monthly_return)**12 - 1) / monthly_return)

        current_value += fv_contributions_this_year
        portfolio_values.append(current_value)

    return years, portfolio_values

# --- Main Application Logic ---
if st.session_state.run_calculation:
    st.header("Your Investment Plan Summary")

    # 1. Determine Asset Allocation
    selected_allocation = ALLOCATION_STRATEGY[risk_tolerance]
    st.subheader("Recommended Asset Allocation:")
    st.write(f"Based on your **{risk_tolerance}** risk tolerance, we recommend the following allocation:")
    st.success(f"**Stocks: {selected_allocation['Stocks']}%** | **Bonds: {selected_allocation['Bonds']}%**")

    # 2. Calculate Expected Portfolio Return
    expected_portfolio_return = calculate_portfolio_return(
        risk_tolerance, AVG_STOCK_RETURN, AVG_BOND_RETURN
    )
    st.info(f"Your expected average annual portfolio return: **{(expected_portfolio_return * 100):.2f}%**")

    # 3. Project Portfolio Growth
    years, projected_values = project_portfolio_growth(
        current_savings, monthly_contribution, investment_horizon, expected_portfolio_return
    )

    df_projection = pd.DataFrame({
        'Year': years,
        'Projected Value ($)': projected_values
    })

    st.subheader("Projected Portfolio Growth Over Time:")
    st.write("This chart shows the potential growth of your portfolio over your chosen investment horizon, assuming average returns.")

    # Create Plotly Line Chart
    fig = go.Figure(data=go.Scatter(x=df_projection['Year'], y=df_projection['Projected Value ($)'], mode='lines+markers', name='Portfolio Value'))
    fig.update_layout(
        title='Portfolio Value Projection',
        xaxis_title='Year',
        yaxis_title='Portfolio Value ($)',
        hovermode='x unified',
        height=450,
        width=800
    )
    st.plotly_chart(fig, use_container_width=True)

    # 4. Display Key Projections
    final_projected_value = projected_values[-1]
    st.subheader("Key Projections:")
    col_final_value, col_total_contributed, col_total_gains = st.columns(3)

    with col_final_value:
        st.metric(label="Estimated Final Portfolio Value", value=f"${final_projected_value:,.2f}")

    total_contributed = current_savings + (monthly_contribution * 12 * investment_horizon)
    with col_total_contributed:
        st.metric(label="Total Contributions + Initial Savings", value=f"${total_contributed:,.2f}")

    total_gains = final_projected_value - total_contributed
    with col_total_gains:
        st.metric(label="Estimated Total Investment Gains", value=f"${max(0, total_gains):,.2f}") # Ensure gains are not negative if initial savings is huge and returns are low

    st.markdown("---")
    st.subheader("General Recommendations:")
    if risk_tolerance == "Conservative":
        st.write("""
        * Your focus on capital preservation is well-reflected in the bond-heavy allocation.
        * Consider reviewing your goals periodically to ensure this approach aligns with your long-term needs.
        * Even conservative investors might benefit from some stock exposure for inflation protection.
        """)
    elif risk_tolerance == "Moderate":
        st.write("""
        * Your balanced approach aims for both growth and stability.
        * This allocation is suitable for investors seeking reasonable returns without excessive risk.
        * Regularly rebalance your portfolio to maintain your desired stock/bond mix.
        """)
    else: # Aggressive
        st.write("""
        * Your aggressive stance targets higher growth, accepting more volatility.
        * This strategy is generally suitable for long-term investors who can ride out market fluctuations.
        * Ensure you are comfortable with potential short-term swings in value.
        """)
    st.write("Remember, consistency in contributions and long-term perspective are key!")

else:
    st.info("👈 Please fill in your financial profile in the sidebar and click 'Calculate My Plan' to get started.")

