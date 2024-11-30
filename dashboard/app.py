# --------------------------------------------
# Imports
# --------------------------------------------
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg
import faicons as fa

# --------------------------------------------
# Constants
# --------------------------------------------
UPDATE_INTERVAL_SECS: int = 3
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# importing icons
ICONS={
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}
tips = px.data.tips()

bill_rng = (min(tips.total_bill), max(tips.total_bill))

# --------------------------------------------
# Reactive Calculation
# --------------------------------------------
@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"temp": temp, "timestamp": timestamp}
    reactive_value_wrapper.get().append(new_entry)
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)
    return deque_snapshot, df, new_entry

# --------------------------------------------
# UI Layout
# --------------------------------------------
ui.page_opts(title="Tipping Culture in the USA", fillable=True)

# Sidebar
with ui.sidebar(open="open"):
    ui.h1("Tip Filters")
    # Selecting Gender Filter
    ui.input_checkbox_group("Gender_selection","Customer's Gender: ", choices=["Male","Female"], inline=True)
    # Selecting Smoking Filter
    ui.input_checkbox_group("Smoker_selection","Is Customer a Smoker?", choices=["Yes","No"], inline=True)

    # Selecting Dining Time Filter
    ui.input_checkbox_group("Dining_Time_Selection","Food Service: ", choices=["Lunch","Dinner"], inline=True)
    ui.input_slider("total_bill","Total Bill Amount",min= bill_rng[0],max= bill_rng[1], value=bill_rng,pre="$",step=0.01)
    

# Main Panel
with ui.layout_columns():
    with ui.value_box(showcase=icon_svg("wallet"),theme="bg-gradient-blue-purple", height=200): 
        "Average Tip per Table"
    @render.text
    def show_average_tip():
        total_tips = tips['tip'].sum()
        total_people = tips['size'].sum()  # Assuming 'size' represents the number of people at each table
        average_tip_per_person = total_tips / total_people if total_people > 0 else 0
        return f"${average_tip_per_person:.2f}"
