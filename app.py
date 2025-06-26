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


    tab1, tab2, tab3 = st.tabs(["DFGs", "Petri Nets", "Other Plots"])


    # # Visualisation tab
    @st.fragment
    def generate_dfgs():

        def generate_dfg(final_log, graph_type, output_filepath="dfg.png"):
                dfg, start_activities, end_activities = pm4py.discover_dfg(final_log)

                if graph_type=="Activity":
                    pm4py.save_vis_dfg(dfg, start_activities, end_activities, file_path=output_filepath)
                elif graph_type=="Performance":
                    pm4py.save_vis_performance_dfg(dfg, start_activities, end_activities, file_path=output_filepath)

                st.image(output_filepath)

        viz_col_main, viz_col_selectors = st.columns([0.7, 0.3])

        with viz_col_selectors:
            graph_type = st.select_slider(label="Graph Type", options=["Activity", "Performance"])

            filter_top_variants = st.toggle("Filter Variants", value=False)
            if filter_top_variants:
                top_variants = st.slider("Choose top variants to visualise",
                                         min_value=1, max_value=100, value=10)

            facet_by_col = st.toggle("Facet by another variable?")
            if facet_by_col:
                facet_col = st.selectbox("Select the column of interest",
                                         [i for i in df_colnames if i not in [case_id_col_name, activity_key_col_name, timestamp_key_col_name]])

        with viz_col_main:

            generate_dfgs_button = st.button("Generate")

            if generate_dfgs_button:

                if filter_top_variants:
                    final_log = pm4py.filter_variants_top_k(event_log_df, k=top_variants)
                else:
                    final_log = event_log_df.copy()

                if facet_by_col:
                    for i in final_log[facet_col].unique():
                        category_log = pm4py.filter_event_attribute_values(
                            final_log, facet_col, [i],
                            level="case", retain=True
                            )
                        st.subheader(f"{i}")
                        generate_dfg(category_log, graph_type=graph_type, output_filepath="dfg_{i}.png")
                else:
                    generate_dfg(final_log, graph_type=graph_type, output_filepath="dfg.png")

        # # Filter trace frequency

        # #
    with tab1:
        generate_dfgs()

    with tab2:
        st.write("Coming Soon!")

    with tab3:
        st.write("Coming Soon!")
