from faicons import icon_svg
import faicons as fa
import plotly.express as px
from shinywidgets import render_plotly, render_widget, output_widget
import random
from shiny import reactive, render
from datetime import datetime
import pandas as pd
from shiny import reactive, render, req
from shiny.express import input, ui,render
from collections import deque
from scipy import stats

UPDATE_INTERVAL_SECS: int = 10
DEQUE_SIZE: int=10
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

#import icons from faicons----------------------------------------------------------------------
ICONS={
    "user": fa.icon_svg("user", "regular"),
    "person": fa.icon_svg("person"),
    "wallet": fa.icon_svg("wallet"),
    "credit-card": fa.icon_svg("credit-card"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

tips = px.data.tips() #call in tipping data
bill_rng = (min(tips.total_bill), max(tips.total_bill))

#page title-----------------------------------------------------------------------------------------
ui.page_opts(title="Tipping Culture in the USA", fillable=True)

with ui.sidebar(open="open"):
    ui.h1("Tip Filters")
    # Selecting Gender Filter
    ui.input_checkbox_group("Gender_selection","Customer's Gender: ", choices=["Male","Female"], inline=True)
    # Selecting Smoking Filter
    ui.input_checkbox_group("Smoker_selection","Is Customer a Smoker?", choices=["Yes","No"], inline=True)

    # Selecting Dining Time Filter
    ui.input_checkbox_group("Dining_Time_Selection","Food Service: ", choices=["Lunch","Dinner"], inline=True)
    ui.input_slider("total_bill","Total Bill Amount",min= bill_rng[0],max= bill_rng[1], value=bill_rng,pre="$",step=0.01)

#------------------------------------------------------------------------------------------------


# Live data
with ui.layout_columns(fill=False):
    # Average tip per table
    with ui.value_box(
        showcase=ICONS["credit-card"],  # Replace with your actual icon value
        theme="bg-gradient-orange-red", height=200
    ):
        "Average Tip per Table"
        @render.text
        def display_avg_tip():
            _, df, _ = reactive_tips_combined()  # Get reactive tip data
            avg_tip = df["avg_tip"].mean()  # Calculate the average tip for girls
            return f"${avg_tip:.2f}"

    # Average bill per table
    with ui.value_box(
        showcase=ICONS["currency-dollar"],  # Replace with your actual icon value
        theme="bg-gradient-green-blue", height=200
    ):
        "Average Bill per Table"
        @render.text
        def display_avg_bill():
            _, df, _ = reactive_tips_combined()  # Get reactive tip data
            avg_bill = df["avg_bill"].mean()  # Calculate the average bill for boys
            return f"${avg_bill:.2f}"

# Data Table and Visualizations ------------------------------------------------------------------
with ui.layout_columns(fill=False):
    # Data Table
    with ui.card():
        "Filtered Tipping Data"
        @render.data_frame
        def tipping_df():
            return render.DataTable(filtered_data(), selection_mode='row')

    # Scatterplot with regression line
    with ui.card(full_screen=True):
        ui.card_header("Scatterplot: Total Bill vs Tip")
        @render_plotly
        def scatterplot_with_regression():
            filtered = filtered_data()  # Get filtered data based on user selections
            fig = px.scatter(
                filtered,
                x="total_bill",
                y="tip",
                color="sex",
                labels={"total_bill": "Total Bill ($)", "tip": "Tip ($)"},
                title="Scatterplot: Total Bill vs Tip"
            )
            return fig

    # Bar chart for Total Tips by Day
    with ui.card(full_screen=True):
        ui.card_header("Bar chart: Group by Day vs Tip")
        @render_plotly
        def barchart():
            filtered = filtered_data()  # Get filtered data based on user selections
            day_tips = filtered.groupby("day")["tip"].sum().reset_index()
            fig = px.bar(
                day_tips,
                x="day",
                y="tip",
                labels={"day": "Day", "tip": "Total Tips ($)"},
                title="Total Tips by Day of the Week"
            )
            return fig

#------------------------------------------------------------------------------------------------


@reactive.calc
def filtered_data():
    req(input.Gender_selection(), input.Smoker_selection(), input.Dining_Time_Selection(), input.total_bill())
    df = tips[
        (tips["sex"].isin(input.Gender_selection())) &
        (tips["smoker"].isin(input.Smoker_selection())) &
        (tips["time"].isin(input.Dining_Time_Selection())) &
        (tips["total_bill"].between(input.total_bill()[0], input.total_bill()[1]))
    ]
    return df

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


