import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Law of Large Numbers Demonstration",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Law of Large Numbers Demonstration")
st.subheader("by Chisom Ibezim")
st.write(
    """
    Explore how the observed probability of an event (like getting heads in a coin flip)
    approaches its theoretical probability as the number of trials increases.
    """
)

# --- Sidebar Controls ---
st.sidebar.header("Simulation Settings")

num_flips_per_sim = st.sidebar.slider(
    "Number of Flips per Simulation (N)",
    min_value=1,
    max_value=1000,
    value=50,
    step=1,
    help="This is 'N' - the number of coin flips in each individual simulation."
)

num_simulations = st.sidebar.slider(
    "Number of Simulations",
    min_value=10,
    max_value=5000,
    value=100,
    step=10,
    help="This is the number of times we repeat the set of 'N' coin flips."
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**The Law of Large Numbers states that as the number of trials in a sample grows (N), "
    "the observed proportion of successes will get closer and closer to the true theoretical probability.**"
)

# --- Simulation Logic ---
@st.cache_data
def run_simulation(n_flips, n_sims):
    """
    Runs coin flip simulations and calculates the proportion of heads.
    """
    # Simulate coin flips: 0 for tails, 1 for heads
    # Each row is a simulation, each column is a flip
    results = np.random.randint(0, 2, size=(n_sims, n_flips))

    # Calculate the number of heads in each simulation
    heads_counts = np.sum(results, axis=1)

    # Calculate the proportion of heads for each simulation
    proportions_of_heads = heads_counts / n_flips

    return proportions_of_heads

proportions = run_simulation(num_flips_per_sim, num_simulations)

# --- Key Statistics (Moved Before Chart) ---
st.subheader("Key Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Proportion of Heads Across All Simulations", f"{np.mean(proportions):.4f}")
with col2:
    st.metric("Standard Deviation of Proportions", f"{np.std(proportions):.4f}")
with col3:
    st.metric("Number of Unique Proportions Observed", len(np.unique(proportions)))

st.markdown("---") # Add a separator

# --- Visualization ---
st.subheader("Distribution of Proportion of Heads")
st.write(
    f"Each point on the x-axis represents the proportion of heads out of {num_flips_per_sim} flips. "
    f"The y-axis shows how many of the {num_simulations} total simulations resulted in that proportion."
)

# Create a histogram using Plotly
fig = go.Figure(data=[go.Histogram(x=proportions, nbinsx=min(50, num_flips_per_sim + 1))]) # Adjust bins based on N

# Add a vertical line for the theoretical probability (0.5 for a fair coin)
fig.add_vline(x=0.5, line_dash="dash", line_color="red", annotation_text="Theoretical Probability (0.5)")

fig.update_layout(
    xaxis_title="Proportion of Heads",
    yaxis_title="Number of Simulations",
    bargap=0.05,
    hovermode="x unified",
    height=450,
    width=800
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("How to interpret the chart:")
st.markdown(
    """
    * **Increase "Number of Flips per Simulation (N)"**: Observe how the histogram becomes narrower and more centered around 0.5. This shows that as 'N' (the sample size) increases, the *observed proportion of heads in each simulation* tends to get closer to the theoretical 0.5. This directly illustrates the Law of Large Numbers.
    * **Increase "Number of Simulations"**: A higher number of simulations will make the histogram smoother and provide a more accurate representation of the underlying distribution of proportions, but it's the 'N' (number of flips per simulation) that primarily demonstrates the Law of Large Numbers.
    """
)