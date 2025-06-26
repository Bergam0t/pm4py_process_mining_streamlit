import streamlit as st
import pandas as pd
from vidigi.animation import animate_activity_log

import pm4py
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer


raw_event_log = st.file_uploader("Upload a csv file")

if raw_event_log is not None:
    raw_event_log_df = pd.read_csv(raw_event_log)

    with st.expander("Click to view uploaded dataframe"):
        st.dataframe(raw_event_log_df)

    df_colnames = raw_event_log_df.columns

    col1, col2, col3 = st.columns(3)

    # Case ID
    case_id_col_name = col1.selectbox(label="What column contains the case ID?", options=df_colnames)

    # Activity Key
    activity_key_col_name = col2.selectbox(label="What column contains the activities?", options=df_colnames)

    # Timestamp key
    timestamp_key_col_name = col3.selectbox(label="Timestamp columns ", options=df_colnames)


    # Convert to pm4py format
    event_log_df = pm4py.format_dataframe(
        raw_event_log_df,
        case_id=case_id_col_name,
        activity_key=activity_key_col_name,
        timestamp_key=timestamp_key_col_name
    )

    with st.expander("Click to view processed dataframe"):
        st.dataframe(event_log_df)


    # # Visualisation tab
    @st.fragment
    def generate_dfgs():
        viz_col_main, viz_col_selectors = st.columns([0.7, 0.3])

        with viz_col_selectors:
            type = st.select_slider(label="Graph Type", options=["Activity", "Performance"])

            filter_top_variants = st.toggle("Filter Variants", value=False)
            if filter_top_variants:
                top_variants = st.slider("Choose top variants to visualise",
                                         min_value=1, max_value=100, value=10)

        with viz_col_main:

            if filter_top_variants:
                final_log = pm4py.filter_variants_top_k(event_log_df, k=top_variants)
            else:
                final_log = event_log_df.copy()

            dfg, start_activities, end_activities = pm4py.discover_dfg(final_log)

            pm4py.save_vis_dfg(dfg, start_activities, end_activities, file_path="dfg.png")

            st.image("dfg.png")




        # # Filter trace frequency

        # #

    generate_dfgs()
