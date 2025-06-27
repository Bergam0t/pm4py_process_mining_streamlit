import streamlit as st
import pandas as pd
from vidigi.animation import animate_activity_log
import datetime
import numpy as np

import pm4py
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer

PM4PY_TIMESTAMP_COL = "time:timestamp"

st.set_page_config(layout="wide")
st.title("Process Mining Helper")

raw_event_log = st.file_uploader("Upload a csv file")

if raw_event_log is not None:
    raw_event_log_df = pd.read_csv(raw_event_log)

    with st.expander("Click to view uploaded dataframe"):
        st.dataframe(raw_event_log_df)

    df_colnames = list(raw_event_log_df.columns)

    col1, col2, col3 = st.columns(3)

    # Case ID
    case_id_col_name = col1.selectbox(
        label="Select Case ID column",
        options=["Choose a Column"] + df_colnames,
        index=0
        )

    # Activity Key
    activity_key_col_name = col2.selectbox(
        label="Select Activity column",
        options=["Choose a Column"] + df_colnames,
        index=0
        )

    # Timestamp key
    timestamp_key_col_name = col3.selectbox(
        label="Select Timestamp column",
        options=["Choose a Column"] + df_colnames,
        index=0
        )

    timestamp_format = st.text_input(
        "Enter the timestamp format",
        value="%d/%m/%Y %H:%M:%S",
        help="Example: For '25/12/2024 14:30', use `%d/%m/%Y %H:%M`")

    # raw_event_log_df["date_col_GEN"] = pd.to_datetime(raw_event_log_df[timestamp_key_col_name], format=timestamp_format).dt.date

    # raw_event_log_df["date_col_GEN"] = raw_event_log_df[timestamp_key_col_name].apply(lambda x: datetime.datetime.strptime(x, timestamp_format) if type(x)==str else np.NaN)
    if "Choose a Column" not in [case_id_col_name, activity_key_col_name, timestamp_key_col_name]:
        try:
        # raw_event_log_df["date_col_GEN"] = pd.to_datetime(
        #     raw_event_log_df[timestamp_key_col_name],
        #     format=timestamp_format,
        #     errors='coerce'  # turns unparsable values into NaT
        # )

        # raw_event_log_df["date_col_GEN"] = raw_event_log_df["date_col_GEN"].dt.date

            # Convert to pm4py format
            event_log_df = pm4py.format_dataframe(
                raw_event_log_df,
                case_id=case_id_col_name,
                activity_key=activity_key_col_name,
                timestamp_key=timestamp_key_col_name,
                timest_format=timestamp_format
            )



            with st.expander("Click to view processed dataframe"):
                st.dataframe(event_log_df)


            tab1, tab2, tab3 = st.tabs(["Directly-Follows Graphs (DFG)", "Petri Nets", "Other Plots"])


            # # Visualisation tab
            @st.fragment
            def generate_dfgs():

                def generate_dfg(final_log, graph_type, output_filepath="dfg.png"):
                        dfg, start_activities, end_activities = pm4py.discover_dfg(final_log)

                        if graph_type=="Frequency":
                            pm4py.save_vis_dfg(dfg, start_activities, end_activities, file_path=output_filepath)
                        elif graph_type=="Performance":
                            pm4py.save_vis_performance_dfg(dfg, start_activities, end_activities, file_path=output_filepath)

                        st.image(output_filepath)

                viz_col_main, viz_col_selectors = st.columns([0.7, 0.3])

                with viz_col_selectors:
                    graph_type = st.radio("Graph Type", ["Frequency", "Performance"], horizontal=True)

                    min_date = event_log_df[PM4PY_TIMESTAMP_COL].min().date()
                    max_date = event_log_df[PM4PY_TIMESTAMP_COL].max().date()

                    date_filters = st.slider(
                        label="Filter by Date Range",
                        min_value=min_date,
                        max_value=max_date,
                        value=(min_date, max_date),
                        format="DD/MM/YYYY"
                    )
                    start_date_filter, end_date_filter = date_filters

                    # TODO: Do we need to consider NA values?
                    # Apply date filter first
                    # The slider returns datetime.date, so we compare the date part of the timestamp
                    final_log = event_log_df[
                            (event_log_df[PM4PY_TIMESTAMP_COL].dt.date >= start_date_filter) &
                            (event_log_df[PM4PY_TIMESTAMP_COL].dt.date <= end_date_filter)
                        ].copy()

                    # Set up variant filters

                    filter_top_variants = st.toggle("Filter by top variants", value=False)

                    if filter_top_variants:
                        # Get the number of variants to suggest a max value for the slider
                        max_variants = len(pm4py.get_variants_as_tuples(event_log_df))

                        top_variants = st.slider("Number of top variants to include",
                                                min_value=1, max_value=max_variants,
                                                value=min(10, max_variants))

                    facet_by_col = st.toggle("Facet by another variable?", value=False)
                    if facet_by_col:
                        # Create a list of columns available for faceting
                        facet_options = [i for i in df_colnames if i not in [
                            case_id_col_name, activity_key_col_name, timestamp_key_col_name
                        ]]

                        # Sort by number of unique values in each column
                        facet_options_sorted = sorted(
                            facet_options,
                            key=lambda col: final_log[col].nunique()
                        )

                        if not facet_options_sorted:
                            st.warning("No other columns available to facet by.")
                            facet_by_col = False # Disable if no options
                        else:
                            facet_col = st.selectbox("Select column for faceting", facet_options_sorted)
                            # st.write(f"This will generate {len(final_log[facet_col].unique())} plots")
                            for col in facet_options_sorted:
                                st.caption(f"{col} has {final_log[col].nunique()} unique options")

                with viz_col_main:

                    # Generate and display the graph(s)
                    if facet_by_col:
                        for value in sorted(final_log[facet_col].unique()):
                            st.markdown(f"--- \n#### {facet_col}: `{value}`")

                            category_log = final_log[final_log[facet_col] == value]
                            # Apply variant filter
                            if filter_top_variants:
                                category_log = pm4py.filter_variants_top_k(category_log, k=top_variants)

                            if not category_log.empty:
                                generate_dfg(category_log, graph_type=graph_type, output_filepath="dfg_{i}.png")
                    else:
                        if filter_top_variants:
                            final_log = pm4py.filter_variants_top_k(final_log, k=top_variants)
                        generate_dfg(final_log, graph_type=graph_type, output_filepath="dfg.png")

            with tab1:
                generate_dfgs()

            with tab2:
                st.write("Coming Soon!")

            with tab3:
                st.write("Coming Soon!")

        except Exception as e:
            st.error(f"An error occurred during data processing: {e}", icon="🚨")
            st.warning("Please ensure the selected timestamp column matches the provided format string. "
                    "For example, if your date is '2024-12-25 14:30', the format should be '%Y-%m-%d %H:%M'.")
            st.warning("Check that you have mapped the correct column names to your ")
