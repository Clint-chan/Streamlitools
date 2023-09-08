import streamlit as st
import altair as alt
def perform_descriptive_stats(df):
    st.subheader('描述性统计')
    
    # 设置单个图形的宽度
    single_chart_width = 200
    
    # 频率条形图
    bar_charts = [alt.Chart(df).mark_bar(color='steelblue').encode(
            alt.X(column, bin=True),
            y='count()'
        ).properties(width=single_chart_width, title=f"{column} 分布") for column in df.columns[2:]]
    
    combined_bar_chart = alt.hconcat(*bar_charts)
    st.altair_chart(combined_bar_chart, use_container_width=True)
    
    # 箱型图
    box_plots = [alt.Chart(df).mark_boxplot(color='salmon').encode(
            x='学历:O',
            y=alt.Y(f"{column}:Q")
        ).properties(width=single_chart_width, title=f"{column} 箱型图") for column in df.columns[2:]]
    
    combined_box_plot = alt.hconcat(*box_plots)
    st.altair_chart(combined_box_plot, use_container_width=True)
    
    # 相关性矩阵
    st.write("### 数值型特征的相关性矩阵")
    corr_data = df.iloc[:, 2:].corr().stack().reset_index().rename(columns={0: 'correlation', 'level_0': 'variable', 'level_1': 'variable2'})
    corr_chart = alt.Chart(corr_data).mark_rect().encode(
        x='variable:O',
        y='variable2:O',
        color='correlation:Q',
        tooltip=['variable', 'variable2', 'correlation']
    )
    st.altair_chart(corr_chart, use_container_width=True)
    
    # 散点图
    scatter_plots = []
    for i, column in enumerate(df.columns[2:]):
        for j, column2 in enumerate(df.columns[i+2:]):
            scatter_plot = alt.Chart(df).mark_circle(color='green').encode(
                x=f"{column}:Q",
                y=f"{column2}:Q",
                tooltip=['学历', '年龄', column, column2]
            ).properties(width=single_chart_width, title=f"{column} vs {column2}")
            scatter_plots.append(scatter_plot)
    
    combined_scatter_plot = alt.hconcat(*scatter_plots)
    st.altair_chart(combined_scatter_plot, use_container_width=True)