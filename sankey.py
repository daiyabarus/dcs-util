import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Streamlit page configuration
st.set_page_config(page_title="DCS Traffic Offload Simulation", layout="wide")

# Load the provided data
data = {
    'Source Cellid': ['BI3411E', 'BI3411E', 'BI3411E', 'BI3411E', 'BI3411E', 'BI3411E', 'BI3411F', 'BI3411F', 'BI3411F', 'BI3411F', 'BI3411F', 'BI3411G', 'BI3411G', 'BI3411G', 'BI3411G', 'BIR411U', 'BIR411U', 'BIR411U', 'BIR411U', 'BIR411U'],
    'TCH_Traffic Erlang Source Before': [8.01, 8.01, 8.01, 8.01, 8.01, 8.01, 2.59, 2.59, 2.59, 2.59, 2.59, 16.68, 16.68, 16.68, 16.68, 38.79, 38.79, 38.79, 38.79, 38.79],
    'Target Offload Cell': ['BIR411A', 'BIR411A', 'BIR411A', 'BIR411A', 'BIR411A', 'BIR411A', 'BIR411B', 'BIR411B', 'BIR411B', 'BIR411B', 'BIR411B', 'BIR411C', 'BIR411C', 'BIR411C', 'BIR411C', 'BIR411R', 'BIR411R', 'BIR411R', 'BIR411R', 'BIR411R'],
    'TCH_Traffic Erlang Target Before': [6.65, 6.65, 6.65, 6.65, 6.65, 6.65, 2.63, 2.63, 2.63, 2.63, 2.63, 7.10, 7.10, 7.10, 7.10, 22.07, 22.07, 22.07, 22.07, 22.07],
    'TCH_Traffic Source After': [5.08, 5.08, 5.08, 5.08, 5.08, 5.08, 2.28, 2.28, 2.28, 2.28, 2.28, 16.63, 16.63, 16.63, 16.63, 29.17, 29.17, 29.17, 29.17, 29.17],
    'Target Cellid': ['BIR411A', 'BIR411A', 'BIR411A', 'BIR411A', 'BIR411A', 'BIR411A', 'BIR411B', 'BIR411B', 'BIR411B', 'BIR411B', 'BIR411B', 'BIR411C', 'BIR411C', 'BIR411C', 'BIR411C', 'BIR411R', 'BIR411R', 'BIR411R', 'BIR411R', 'BIR411R'],
    'TCH_Traffic Target::::After': [9.83, 9.83, 9.83, 9.83, 9.83, 9.83, 5.08, 5.08, 5.08, 5.08, 5.08, 13.18, 13.18, 13.18, 13.18, 38.39, 38.39, 38.39, 38.39, 38.39],
    '1st Tier': ['BI3363B', 'BI3363C', 'BI3363F', 'BIR363G', 'BIR363T', 'SI1043E', 'BI3363B', 'BI3108A', 'BI3363F', 'BI3108E', 'BIR587F', 'BI3108A', 'BI3297E', 'BIR297S', 'BIR314E', 'SGI130A', 'SI1075A', 'SGI512A', 'SGI130S', 'SI1075E'],
    'TCH_Traffic 1stTier After': [5.08, 6.61, 13.18, 5.08, 13.18, 5.08, 5.08, 5.08, 13.18, 18.38, 13.18, 5.08, 9.83, 5.08, 0.00, 18.38, 14.90, 5.08, 34.68, 14.90]
}
df = pd.DataFrame(data)

# Update cell IDs: Replace BI3 with BIR
def update_cell_id(cellid):
    return cellid.replace('BI3', 'BIR')

for col in ['Source Cellid', 'Target Offload Cell', 'Target Cellid', '1st Tier']:
    df[col] = df[col].apply(update_cell_id)

# Define co-sector mapping
cosector_mapping = {
    'BIR411E': 'BIR411A',
    'BIR411F': 'BIR411B',
    'BIR411G': 'BIR411C',
    'BIR411U': 'BIR411R'
}

# Identify co-site cells (same site prefix, e.g., BIR411)
def get_site(cellid):
    return cellid[:6]  # First 6 characters denote the site

df['Source Site'] = df['Source Cellid'].apply(get_site)
df['Target Site'] = df['Target Cellid'].apply(get_site)

# Calculate total offloaded traffic for Stage 2
df['Offloaded_Traffic_Erlangs'] = df['TCH_Traffic Erlang Source Before'] - df['TCH_Traffic Source After']

# Simulate offload distribution to co-site, 1st-tier, and co-sector cells (Stage 2 to Stage 3)
source_cells = df['Source Cellid'].unique()
offload_data = []

for src_cell in source_cells:
    src_data = df[df['Source Cellid'] == src_cell]
    total_offload = src_data['Offloaded_Traffic_Erlangs'].iloc[0]
    
    # Identify co-site cells (same site as source, excluding source itself)
    src_site = get_site(src_cell)
    cosite_cells = df[df['Source Site'] == src_site]['Source Cellid'].unique()
    cosite_cells = [c for c in cosite_cells if c != src_cell]
    
    # Identify 1st-tier cells
    first_tier_cells = src_data['1st Tier'].unique()
    
    # Identify co-sector cell
    cosector_cell = cosector_mapping.get(src_cell, None)
    
    # Get traffic data for co-site, 1st-tier, and co-sector cells
    cosite_traffic = {c: df[df['Target Cellid'] == c]['TCH_Traffic Target::::After'].iloc[0] if c in df['Target Cellid'].values else 0 for c in cosite_cells}
    first_tier_traffic = {c: df[df['1st Tier'] == c]['TCH_Traffic 1stTier After'].iloc[0] for c in first_tier_cells}
    cosector_traffic = {cosector_cell: df[df['Target Cellid'] == cosector_cell]['TCH_Traffic Target::::After'].iloc[0] if cosector_cell in df['Target Cellid'].values else 0} if cosector_cell else {}
    
    # Total traffic for proportional distribution
    total_target_traffic = sum(cosite_traffic.values()) + sum(first_tier_traffic.values()) + sum(cosector_traffic.values())
    
    # Distribute offloaded traffic proportionally
    if total_target_traffic > 0 and total_offload > 0:  # Ensure there's traffic to offload
        for c_cell in cosite_cells:
            if c_cell in cosite_traffic and cosite_traffic[c_cell] > 0:
                offload = total_offload * (cosite_traffic[c_cell] / total_target_traffic)
                offload_pct = (offload / total_offload * 100).round(2)
                receive_pct = (offload / cosite_traffic[c_cell] * 100).round(2) if cosite_traffic[c_cell] > 0 else 0
                offload_data.append({
                    'Source Cellid': src_cell,
                    'Target Cellid': c_cell,
                    'Type': 'Co-site',
                    'Offloaded_Traffic_Erlangs': offload,
                    'Offload_Percentage': offload_pct,
                    'Receive_Percentage': receive_pct
                })
        
        for f_cell in first_tier_cells:
            # Include all 1st-tier cells, but only assign traffic if non-zero
            if f_cell in first_tier_traffic and first_tier_traffic[f_cell] > 0:
                offload = total_offload * (first_tier_traffic[f_cell] / total_target_traffic)
                offload_pct = (offload / total_offload * 100).round(2)
                receive_pct = (offload / first_tier_traffic[f_cell] * 100).round(2) if first_tier_traffic[f_cell] > 0 else 0
                offload_data.append({
                    'Source Cellid': src_cell,
                    'Target Cellid': f_cell,
                    'Type': '1st Tier',
                    'Offloaded_Traffic_Erlangs': offload,
                    'Offload_Percentage': offload_pct,
                    'Receive_Percentage': receive_pct
                })
        
        if cosector_cell and cosector_traffic.get(cosector_cell, 0) > 0:
            offload = total_offload * (cosector_traffic[cosector_cell] / total_target_traffic)
            offload_pct = (offload / total_offload * 100).round(2)
            receive_pct = (offload / cosector_traffic[cosector_cell] * 100).round(2) if cosector_traffic[cosector_cell] > 0 else 0
            offload_data.append({
                'Source Cellid': src_cell,
                'Target Cellid': cosector_cell,
                'Type': 'Co-sector',
                'Offloaded_Traffic_Erlangs': offload,
                'Offload_Percentage': offload_pct,
                'Receive_Percentage': receive_pct
            })

# Create DataFrame for Stage 2 to Stage 3 offload
offload_df = pd.DataFrame(offload_data)

# Simulate Stage 3 to Stage 4 offload (to BIR411E and BIR411F)
stage4_cells = ['BIR411E', 'BIR411F']
stage4_traffic = {cell: df[df['Source Cellid'] == cell]['TCH_Traffic Source After'].iloc[0] if cell in df['Source Cellid'].values else 0 for cell in stage4_cells}
total_stage4_traffic = sum(stage4_traffic.values())  # 5.08 + 2.28 = 7.36 Erl

stage4_offload_data = []
for _, row in offload_df.iterrows():
    src_cell = row['Target Cellid']  # Stage 3 cell becomes source for Stage 4
    stage3_offload = row['Offloaded_Traffic_Erlangs']
    
    # Distribute Stage 3 offload to BIR411E and BIR411F
    for s4_cell in stage4_cells:
        offload = stage3_offload * (stage4_traffic[s4_cell] / total_stage4_traffic)
        offload_pct = (offload / stage3_offload * 100).round(2) if stage3_offload > 0 else 0
        receive_pct = (offload / stage4_traffic[s4_cell] * 100).round(2) if stage4_traffic[s4_cell] > 0 else 0
        stage4_offload_data.append({
            'Stage3 Cellid': src_cell,
            'Stage4 Cellid': s4_cell,
            'Type': 'Stage 4',
            'Offloaded_Traffic_Erlangs': offload,
            'Offload_Percentage': offload_pct,
            'Receive_Percentage': receive_pct
        })

# Create DataFrame for Stage 3 to Stage 4 offload
stage4_offload_df = pd.DataFrame(stage4_offload_data)

# Calculate total traffic for Stage 1, Stage 3, and Stage 4
stage1_traffic = {cell: df[df['Source Cellid'] == cell]['TCH_Traffic Erlang Source Before'].iloc[0] for cell in source_cells}
stage3_traffic = {}
for cell in offload_df['Target Cellid'].unique():
    if cell in df['Target Cellid'].values:
        stage3_traffic[cell] = df[df['Target Cellid'] == cell]['TCH_Traffic Target::::After'].iloc[0]
    elif cell in df['1st Tier'].values:
        stage3_traffic[cell] = df[df['1st Tier'] == cell]['TCH_Traffic 1stTier After'].iloc[0]
stage4_traffic = stage4_traffic  # Already calculated

stage1_total = sum(stage1_traffic.values())
stage3_total = sum(stage3_traffic.values())
stage4_total = sum(stage4_traffic.values())

# Calculate percentages
stage1_percentages = {cell: (traffic / stage1_total * 100).round(2) for cell, traffic in stage1_traffic.items()}
stage3_percentages = {cell: (traffic / stage3_total * 100).round(2) for cell, traffic in stage3_traffic.items()}
stage4_percentages = {cell: (traffic / stage4_total * 100).round(2) for cell, traffic in stage4_traffic.items()}

# Prepare Sankey diagram data
source_nodes = [f"{cell}_Before" for cell in source_cells]
offload_nodes = [f"{src}_to_{tgt}_{typ}_Offload" for src, tgt, typ in zip(offload_df['Source Cellid'], offload_df['Target Cellid'], offload_df['Type'])]
target_nodes = [f"{cell}_After" for cell in offload_df['Target Cellid'].unique()]
stage4_nodes = [f"{cell}_Stage4" for cell in stage4_cells]
nodes = source_nodes + offload_nodes + target_nodes + stage4_nodes

# Create node indices
node_indices = {node: i for i, node in enumerate(nodes)}

# Create node labels with total Erlangs and percentages
node_labels = []
for node in nodes:
    cell = node.split('_')[0]
    if 'Before' in node:
        erl = stage1_traffic.get(cell, 0)
        pct = stage1_percentages.get(cell, 0)
        node_labels.append(f"{cell}: {erl:.2f} Erl ({pct}%)")
    elif 'Offload' in node:
        node_labels.append(f"{cell}_Offload")
    elif 'After' in node:
        erl = stage3_traffic.get(cell, 0)
        pct = stage3_percentages.get(cell, 0)
        node_labels.append(f"{cell}: {erl:.2f} Erl ({pct}%)")
    elif 'Stage4' in node:
        erl = stage4_traffic.get(cell, 0)
        pct = stage4_percentages.get(cell, 0)
        node_labels.append(f"{cell}: {erl:.2f} Erl ({pct}%)")

# Create links
source_indices = []
target_indices = []
values = []
link_labels = []

# Stage 1 to Stage 2: Source Before to Offload
for i, row in offload_df.iterrows():
    src_node = f"{row['Source Cellid']}_Before"
    offload_node = f"{row['Source Cellid']}_to_{row['Target Cellid']}_{row['Type']}_Offload"
    # Ensure offload_node exists in node_indices
    if offload_node in node_indices:
        source_indices.append(node_indices[src_node])
        target_indices.append(node_indices[offload_node])
        values.append(row['Offloaded_Traffic_Erlangs'])
        link_labels.append(f"{row['Offloaded_Traffic_Erlangs']:.2f} Erl ({row['Offload_Percentage']}% of Source)")
    else:
        st.warning(f"Offload node {offload_node} not found in node_indices. Skipping.")

# Stage 2 to Stage 3: Offload to Target After
for i, row in offload_df.iterrows():
    offload_node = f"{row['Source Cellid']}_to_{row['Target Cellid']}_{row['Type']}_Offload"
    tgt_node = f"{row['Target Cellid']}_After"
    if offload_node in node_indices and tgt_node in node_indices:
        source_indices.append(node_indices[offload_node])
        target_indices.append(node_indices[tgt_node])
        values.append(row['Offloaded_Traffic_Erlangs'])
        link_labels.append(f"{row['Offloaded_Traffic_Erlangs']:.2f} Erl ({row['Receive_Percentage']}% to Target)")
    else:
        st.warning(f"Link from {offload_node} to {tgt_node} skipped due to missing node.")

# Stage 3 to Stage 4: Target After to Stage 4
for i, row in stage4_offload_df.iterrows():
    src_node = f"{row['Stage3 Cellid']}_After"
    tgt_node = f"{row['Stage4 Cellid']}_Stage4"
    if src_node in node_indices and tgt_node in node_indices:
        source_indices.append(node_indices[src_node])
        target_indices.append(node_indices[tgt_node])
        values.append(row['Offloaded_Traffic_Erlangs'])
        link_labels.append(f"{row['Offloaded_Traffic_Erlangs']:.2f} Erl ({row['Receive_Percentage']}% to Stage 4)")
    else:
        st.warning(f"Link from {src_node} to {tgt_node} skipped due to missing node.")

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=30,          # Increased from 20 to 30
        line=dict(color="red", width=0.5),
        label=node_labels,
        # Enhanced node colors
        color=[
            "#1f77b4" if "Before" in n else  # Blue for Before
            "#2ca02c" if "Offload" in n else  # Green for Offload
            "#ff7f0e" if "After" in n else    # Orange for After
            "#9467bd" for n in nodes          # Purple for Stage4
        ]
    ),
    link=dict(
        source=source_indices,
        target=target_indices,
        value=values,
        label=link_labels,
        color="rgb(232, 182, 157)",
        colorscales=[{'colorscale': 'YlGnBu'}],
        hovertemplate="From %{source.label} to %{target.label}: %{value:.2f} Erlangs (%{label})<extra></extra>"
    )
)])

# Add global font styling for the figure
fig.update_layout(
    font=dict(
        size=16,              # Increase label text size
        color='red',        # Set label text color to white
        family='Arial'        # Specify font family
    )
)

# Streamlit layout
st.title("DCS Traffic Offload Simulation: 4-Stage Sankey Diagram")

# Inject CSS to style Sankey node label text color
st.markdown(
    """
    <style>
    /* Default text color for all Sankey node labels */
    .js-plotly-plot .plotly .sankey .node text {
        fill: black !important;  /* Default color for non-Offload nodes */
        font-size: 12px !important;  /* Optional: Set font size */
    }
    /* Specific text color for Offload node labels */
    .js-plotly-plot .plotly .sankey .node text:not(:empty):not(:only-child) {
        fill: #0000FF !important;  /* Blue for Offload node labels */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.plotly_chart(fig, use_container_width=True)

# Display Markdown summary
st.markdown("""
# 📊 DCS Traffic Offload Simulation Summary

## 🌟 Overview
This interactive 4-stage Sankey diagram simulates the offload of **Digital Cellular System (DCS)** traffic across multiple cell types in the `BIR411` site, located in Samalanga, Bireuen, Aceh. It visualizes the redistribution of **Traffic Channel (TCH)** traffic, measured in Erlangs, to optimize network performance by balancing loads across **co-site**, **1st-tier**, **co-sector**, and **additional receiver cells** (`BIR411E` and `BIR411F`). The simulation is derived from detailed cell metrics, including traffic, utilization, and offload predictions, to support network planning.

## 🛠️ Diagram Structure
The diagram is organized into four stages, each representing a phase in the traffic offload process:

### Stage 1: Source Cells (Before Offload)
- **Description**: Displays the initial TCH traffic (`TCH_Traffic Erlang Source Before`) for source cells (`BIR411E`, `BIR411F`, `BIR411G`, `BIR411U`), which are DCS cells with high traffic loads.
- **Details**: Each node shows the total Erlangs and the percentage of the total source traffic. For example, `BIR411U` contributes 38.79 Erlangs, a significant portion of the total.

### Stage 2: Offload Distribution
- **Description**: Represents the offloaded traffic from source cells, distributed to co-site, 1st-tier, and co-sector cells.
- **Details**: Offload nodes are labeled by source, target, and type (Co-site, 1st Tier, Co-sector). Links show the offloaded Erlangs and the percentage of the source’s offloaded traffic. For instance, `BIR411E` offloads 2.93 Erlangs, split across multiple targets.

### Stage 3: Target Cells (After Initial Offload)
- **Description**: Shows the final TCH traffic for target cells, including co-site (`BIR411F`, `BIR411G`), 1st-tier (`BIR363B`, `BIR363C`, etc.), and co-sector cells (`BIR411A`, `BIR411B`, `BIR411C`, `BIR411R`).
- **Details**: Nodes display total Erlangs and the percentage of total target traffic. Links indicate the received Erlangs and the contribution to the target’s traffic (e.g., `BIR411A` receives 0.38 Erl from `BIR411E`, ~3.84% of its 9.83 Erl).

### Stage 4: Additional Receivers (BIR411E and BIR411F)
- **Description**: Simulates further offload from Stage 3 target cells to `BIR411E` and `BIR411F`, which are DCS cells acting as additional receivers despite their high utilization.
- **Details**: Nodes show the final traffic (`TCH_Traffic Source After`, 5.08 Erl for `BIR411E`, 2.28 Erl for `BIR411F`) and percentages (69% and 31% of the 7.36 Erl total). Links display the offloaded Erlangs and the percentage contribution to Stage 4 traffic.

## 🔑 Key Components
- **Co-site Cells**: Cells sharing the `BIR411` site prefix (e.g., `BIR411F`, `BIR411G` for `BIR411E`), excluding the source cell.
- **1st-Tier Cells**: Neighboring cells listed in the `1st Tier` column (e.g., `BIR363B`, `BIR363C`, `BIR363F`).
- **Co-sector Cells**: Mapped as follows:
  - `BIR411E` → `BIR411A`
  - `BIR411F` → `BIR411B`
  - `BIR411G` → `BIR411C`
  - `BIR411U` → `BIR411R`
- **Stage 4 Receivers**: `BIR411E` and `BIR411F`, receiving traffic proportional to their `TCH_Traffic Source After` (69% to `BIR411E`, 31% to `BIR411F`).
- **Offload Simulation**:
  - **Stage 2**: Offloaded traffic (`TCH_Traffic Erlang Source Before` - `TCH_Traffic Source After`) is distributed to Stage 3 targets based on their final traffic.
  - **Stage 4**: Stage 3 traffic is redistributed to `BIR411E` and `BIR411F`, simulating a secondary offload phase.
- **Percentages**:
  - **Offload Percentage**: Proportion of a cell’s offloaded traffic to each target (e.g., 12.87% from `BIR411E` to `BIR411A` in Stage 2).
  - **Receive Percentage**: Proportion of a target’s final traffic from offload (e.g., 3.84% for `BIR411A` in Stage 3).

## 🎯 Purpose
The 4-stage Sankey diagram models a complex DCS traffic offload scenario, reflecting real-world network dynamics in the `BIR411` site. It helps network planners:
- **Balance Traffic Loads**: By redistributing traffic from high-utilization DCS cells (e.g., `BIR411E` at 81.51% TCH utilization) to GSM cells (`BIR411A`, `BIR411B`) and neighbors.
- **Evaluate Capacity**: Assess the impact of offloading to co-site, 1st-tier, co-sector, and additional receivers (`BIR411E`, `BIR411F`).
- **Optimize Performance**: Support actions like activating VAMOS, reconfiguring PDCH, or maximizing HR settings, as indicated in the dataset’s `Remark Offload`.

## 📈 Insights from Dataset
- **DCS Cells**: `BIR411E`, `BIR411F`, `BIR411G`, and `BIR411U` are marked “Not Safe” due to high TCH utilization (e.g., 81.51% for `BIR411E`), requiring offload to GSM cells or neighbors.
- **GSM Cells**: `BIR411A`, `BIR411B`, `BIR411C`, and `BIR411R` are ready to receive traffic, with lower utilization (e.g., 60.43% for `BIR411A`) and VAMOS enabled on some cells.
- **Stage 4 Consideration**: Including `BIR411E` and `BIR411F` as receivers is unconventional due to their high utilization, but it simulates a scenario where these cells absorb residual traffic, possibly after optimization (e.g., VAMOS activation).
- **Offload Predictions**: The dataset’s `Prediction TCH Traffic Need Offload` aligns with the simulation (e.g., -2.93 Erl for `BIR411E` matches 2.93 Erl offloaded).
- **Network Context**: The `BIR411` site operates both GSM and DCS bands, with DCS cells needing offload due to high traffic and blocking (e.g., 5% TCH blocking for `BIR411U`).

## 📝 Notes
- **Cell ID Update**: Replaced old nomenclature (`BI3`) with `BIR` (e.g., `BI3411E` → `BIR411E`) for consistency.
- **Data Assumption**: Corrected a typo in `TCH_Traffic Source After` for `BIR411G` (`chastity` → 16.63 Erl). Confirmation of the correct value is recommended.
- **Zero Traffic**: Excluded cells with 0.00 Erlangs (e.g., `BIR314E`) to avoid computational errors, but ensured all valid 1st-tier cells are processed.
- **Diagram Complexity**: The 4-stage diagram is dense due to multiple targets and stages. Filtering to specific source cells can simplify visualization.
- **Streamlit**: Provides an interactive interface, allowing users to zoom and explore the Sankey diagram.

This visualization is a powerful tool for network optimization, offering a clear view of traffic redistribution and supporting data-driven decisions in the `BIR411` site.
""")