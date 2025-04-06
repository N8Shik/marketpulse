from mftool import Mftool
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

mf = Mftool()

st.title('Mutual Fund Financial Dashboard')

# Sidebar Dropdown Menu
option = st.sidebar.selectbox(
    "Choose an action",
    [ "Compare NAVs",
     "Average AUM", "Performance Heatmap", "Risk and Volatility Analysis"]
)

# Fetching all scheme codes
scheme_codes = mf.get_scheme_codes()
if isinstance(scheme_codes, dict):
    scheme_name = {v: k for k, v in scheme_codes.items()}
else:
    scheme_name = {}

# View Available Schemes
if option == 'View Available Schemes':
    st.header('View Available Schemes')
    amc = st.sidebar.text_input("Enter AMC Name", "ICICI")
    schemes = mf.get_available_schemes(amc)

    if schemes:
        st.write(pd.DataFrame(schemes.items(), columns=["Scheme Code", "Scheme Name"]))
    else:
        st.write("No schemes found for the given AMC.")

# Compare NAVs
if option == 'Compare NAVs':
    st.header("Compare NAVs")

    # Multi-select dropdown for schemes
    selected_schemes = st.sidebar.multiselect("Select Schemes to Compare", options=list(scheme_name.keys()))

    if selected_schemes:
        comparison_df = pd.DataFrame()

        for scheme in selected_schemes:
            code = scheme_name[scheme]  # Get scheme code from name

            # Fetch historical NAV data
            nav_data = mf.get_scheme_historical_nav(code)

            # Convert dictionary response into DataFrame
            if isinstance(nav_data, dict) and "data" in nav_data:
                data = pd.DataFrame(nav_data["data"])
                data["date"] = pd.to_datetime(data["date"], dayfirst=True)  # Specify dayfirst=True
                data = data.sort_values(by="date")  # Ensure chronological order

                # Convert NAV column to numeric (handling missing or zero values)
                data["nav"] = pd.to_numeric(data["nav"], errors="coerce").interpolate()

                # Merge data into comparison DataFrame
                comparison_df[scheme] = data.set_index("date")["nav"]

        # Plot the comparison graph
        if not comparison_df.empty:
            fig = px.line(comparison_df, title="Comparison of NAVs")
            st.plotly_chart(fig)
        else:
            st.info("No NAV data available for the selected schemes.")

    else:
        st.info("Select at least one scheme to compare.")



# Performance Heatmap
if option == "Performance Heatmap":
    st.header("Performance Heatmap")

    # Fetch scheme codes
    scheme_codes = mf.get_scheme_codes()
    if isinstance(scheme_codes, dict):
        scheme_names = {v: k for k, v in scheme_codes.items()}
    else:
        scheme_names = {}

    # Dropdown for selecting scheme
    selected_scheme = st.sidebar.selectbox("Select a Scheme", list(scheme_names.keys()))

    if selected_scheme:
        scheme_code = scheme_names[selected_scheme]  # Get scheme code from name
        nav_data = mf.get_scheme_historical_nav(scheme_code)  # Removed 'as_DataFrame=True'

        # Check if data is retrieved properly
        if isinstance(nav_data, dict) and "data" in nav_data:
            # Convert to DataFrame
            nav_df = pd.DataFrame(nav_data["data"])

            # Ensure required columns exist
            if "date" in nav_df.columns and "nav" in nav_df.columns:
                nav_df["date"] = pd.to_datetime(nav_df["date"], dayfirst=True)
                nav_df["month"] = nav_df["date"].dt.month
                nav_df["nav"] = pd.to_numeric(nav_df["nav"], errors="coerce").interpolate() # Convert and interpolate

                # Compute daily change in NAV
                nav_df["dayChange"] = nav_df["nav"].diff().fillna(0)

                # Group by month to compute average daily change
                heatmap_data = nav_df.groupby("month")["dayChange"].mean().reset_index()
                heatmap_data["month"] = heatmap_data["month"].astype(str)

                # Plot the heatmap
                fig = px.density_heatmap(heatmap_data, x="month", y="dayChange",
                                            title=f"NAV Performance Heatmap for {selected_scheme}", color_continuous_scale="viridis")
                st.plotly_chart(fig)
            else:
                st.write("Required columns ('date', 'nav') not found in NAV data.")
        else:
            st.write(f"No historical NAV data available for the scheme: {selected_scheme}.")
    else:
        st.write("Please select a valid scheme for the heatmap.")

# Risk and Volatility Analysis
elif option == "Risk and Volatility Analysis":
    st.header("📊 Risk and Volatility Analysis")

    # Fetch scheme codes
    scheme_codes = mf.get_scheme_codes()
    if isinstance(scheme_codes, dict):
        scheme_names = {v: k for k, v in scheme_codes.items()}
    else:
        scheme_names = {}

    # Dropdown for selecting scheme
    selected_scheme = st.sidebar.selectbox("Select a Scheme", list(scheme_names.keys()))

    if selected_scheme:
        scheme_code = scheme_names[selected_scheme]  # Get scheme code from name
        nav_data = mf.get_scheme_historical_nav(scheme_code)

        # Check if valid data is retrieved
        if isinstance(nav_data, dict) and "data" in nav_data:
            # Convert to DataFrame
            nav_df = pd.DataFrame(nav_data["data"])

            # Ensure required columns exist
            if "date" in nav_df.columns and "nav" in nav_df.columns:
                nav_df["date"] = pd.to_datetime(nav_df["date"], dayfirst=True)
                nav_df["nav"] = pd.to_numeric(nav_df["nav"], errors="coerce").interpolate() # Convert and interpolate

                # Calculate Daily Returns
                nav_df["daily_return"] = nav_df["nav"].pct_change().fillna(0)

                # Compute Cumulative Returns
                nav_df["cumulative_return"] = (1 + nav_df["daily_return"]).cumprod()

                # Calculate Volatility (Standard Deviation of Returns)
                volatility = nav_df["daily_return"].std()

                # Calculate Rolling Volatility (30-day)
                nav_df["rolling_volatility"] = nav_df["daily_return"].rolling(window=30).std()

                # Calculate Sharpe Ratio (Assuming risk-free rate = 0)
                sharpe_ratio = nav_df["daily_return"].mean() / volatility if volatility > 0 else 0

                # Calculate Maximum Drawdown
                nav_df["cumulative_max"] = nav_df["nav"].cummax()
                nav_df["drawdown"] = (nav_df["nav"] - nav_df["cumulative_max"]) / nav_df["cumulative_max"]
                max_drawdown = nav_df["drawdown"].min()

                # Display results
                st.subheader(f"📈 Risk and Volatility Metrics for {selected_scheme}")
                st.write(f"📉 *Volatility (Standard Deviation of Returns):* {volatility:.6f}")
                st.write(f"⚡ *Sharpe Ratio (Risk-Adjusted Return):* {sharpe_ratio:.6f}")
                st.write(f"🚨 *Maximum Drawdown:* {max_drawdown:.2%}")

                # 📊 Plot Daily Returns
                fig1 = px.line(nav_df, x="date", y="daily_return",
                                    title=f"📊 Daily Returns of {selected_scheme}",
                                    labels={"daily_return": "Daily Return"})
                st.plotly_chart(fig1)

                # 📈 Plot Rolling 30-Day Volatility
                fig2 = px.line(nav_df, x="date", y="rolling_volatility",
                                    title="📊 Rolling 30-Day Volatility",
                                    labels={"rolling_volatility": "Volatility"})
                st.plotly_chart(fig2)

                # 📈 Plot Cumulative Returns
                fig3 = px.line(nav_df, x="date", y="cumulative_return",
                                    title="📈 Cumulative Returns Over Time",
                                    labels={"cumulative_return": "Cumulative Return"})
                st.plotly_chart(fig3)

            else:
                st.write("Required columns ('date', 'nav') not found in NAV data.")
        else:
            st.write(f"No historical NAV data available for the scheme: {selected_scheme}.")
    else:
        st.write("Please select a valid scheme for risk and volatility analysis.")