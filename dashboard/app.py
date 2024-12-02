from faicons import icon_svg
import faicons as fa
import plotly.express as px
from shinywidgets import render_plotly, render_widget, output_widget
import random
from shiny import reactive, render
from datetime import datetime
import pandas as pd
from shiny import reactive, render, req
from shiny.express import input, ui, render
from collections import deque
from scipy import stats

# Constants
UPDATE_INTERVAL_SECS = 3
DEQUE_SIZE = 2
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# Load dataset
tips = px.data.tips()
bill_rng = (tips["total_bill"].min(), tips["total_bill"].max())

ICONS={
    "user": fa.icon_svg("user", "regular"),
    "person": fa.icon_svg("person"),
    "wallet": fa.icon_svg("wallet"),
    "credit-card": fa.icon_svg("credit-card"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

# UI
ui.page_opts(title="Tipping Culture in the USA", fillable=True)

with ui.sidebar(open="open"):
    ui.h1("Tip Filters")
    # Default selected checkboxes for Gender, Smoker, and Dining Time
    ui.input_checkbox_group("Gender_selection", "Customer's Gender:", choices=["Male", "Female"], inline=True, selected=["Male", "Female"])
    ui.input_checkbox_group("Smoker_selection", "Is Customer a Smoker?", choices=["Yes", "No"], inline=True, selected=["Yes", "No"])
    ui.input_checkbox_group("Dining_Time_Selection", "Food Service:", choices=["Lunch", "Dinner"], inline=True, selected=["Lunch", "Dinner"])
    ui.input_slider("total_bill", "Total Bill Amount", min=bill_rng[0], max=bill_rng[1], value=bill_rng, pre="$", step=0.01)

# Live Data Display
with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["wallet"],theme="bg-gradient-orange-red", height=200):
        "Average Tip per Table"
        @render.text
        def display_avg_tip():
            filtered = filtered_data()
            avg_tip = filtered["tip"].mean() if not filtered.empty else 0
            return f"${avg_tip:.2f}"

    with ui.value_box(showcase=ICONS["credit-card"],theme="bg-gradient-green-blue", height=200):
        "Average Bill per Table"
        @render.text
        def display_avg_bill():
            filtered = filtered_data()
            avg_bill = filtered["total_bill"].mean() if not filtered.empty else 0
            return f"${avg_bill:.2f}"

# Data Table and Visualizations
with ui.layout_columns(fill=False):
    with ui.card():
        "Data Table"
        @render.data_frame
        def tipping_df():
            return filtered_data()

    with ui.card(full_screen=True):
        ui.card_header("Do males or females tip more?")
        @render_plotly
        def scatterplot_with_regression():
            filtered = filtered_data()
            fig = px.scatter(
                filtered,
                x="tip",
                y="total_bill",
                color="smoker",
                labels={"total_bill": "Total Bill ($)", "tip": "Tip ($)"},
                title="Scatterplot: Total Bill vs Tip"
            )
            return fig

    with ui.card(full_screen=True):
        ui.card_header("How does size affect overall tips?")
        @render_plotly
        def barchart():
            filtered = filtered_data()
            day_tips = filtered.groupby("size")["tip"].sum().reset_index()
            fig = px.bar(
                day_tips,
                x="size",
                y="tip",
                labels={"size": "Size", "tip": "Total Tips ($)"},
                title="Total Tips by Day of the Week"
            )
            return fig

# Reactive Functions
@reactive.calc
def filtered_data():
    # Ensure the values are being properly accessed and are not empty
    gender_selection = input.Gender_selection()  # These need to be reactive inputs
    smoker_selection = input.Smoker_selection()
    dining_time_selection = input.Dining_Time_Selection()
    total_bill = input.total_bill()

    req(gender_selection, smoker_selection, dining_time_selection, total_bill)

    print(f"Gender_selection: {input.Gender_selection}")
    print(f"Smoker_selection: {input.Smoker_selection}")
    print(f"Dining_Time_Selection: {input.Dining_Time_Selection}")
    print(f"total_bill: {input.total_bill}")
    

    # Filter the dataset based on the input values
    filtered = tips[
        (tips["sex"].isin(gender_selection)) &
        (tips["smoker"].isin(smoker_selection)) &
        (tips["time"].isin(dining_time_selection)) &
        (tips["total_bill"].between(total_bill[0], total_bill[1]))
    ]
    return filtered

@reactive.calc
def reactive_tips_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    avg_tip = round(random.uniform(1, 50), 1)
    avg_bill = round(random.uniform(1, 50), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = {"avgTip": avg_tip, "avgBill": avg_bill, "timestamp": timestamp}
    reactive_value_wrapper.get().append(new_entry)
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)

    return deque_snapshot, df, new_entry

    




