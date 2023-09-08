import streamlit as st
from itertools import product
from scipy.stats import chi2_contingency
import pandas as pd
import altair as alt
from scipy.stats import mannwhitneyu
def perform_chi_square_analysis(df, significance_level=0.05):
    try:
        # 获取列名
        col1_name = df.columns[0]  # 第一列作为行联表
        col2_name = df.columns[1]  # 第二列作为列联表的子集
        
        results_fully_dynamic = {}
        
        # 使用product获取所有的组合
        for var1, var2 in product(df[col1_name].unique(), df[col2_name].unique()):
            key = f"{var1}_{var2}"
            
            # 为每个组合构建频率表
            rows = []
            for col in df.columns[2:]:
                row = df[(df[col1_name] == var1) & (df[col2_name] == var2)][col].values
                if row.size > 0:
                    rows.append(row[0])
                else:
                    rows.append(0)
            
            expected = [sum(rows)/len(rows)] * len(rows)
            chi2, p, _, _ = chi2_contingency([rows, expected])
            
            results_fully_dynamic[key] = {"Chi-Square": chi2, "P值": p}
        
        # Format output
        data = []
        for key, res in results_fully_dynamic.items():
            variables = key.split('_')
            chi_square = res['Chi-Square']
            p_value = res['P值']
            significance = "有关联" if p_value < significance_level else "无关"
            row_data = variables + [chi_square, p_value, significance]
            data.append(row_data)
        
        columns = list(df.columns[:2]) + ['卡方值', 'P值', '显著性']
        df_results = pd.DataFrame(data, columns=columns)
        df_results.sort_values(by=['卡方值','P值'], ascending=[False, True], inplace=True)
        
        # Display the results
        styled_df = df_results.style.format({
            '卡方值': "{:.2f}",
            'P值': "{:.2f}"
        }).apply(lambda _: ["text-align: center" for _ in df_results.columns], axis=1)
        styled_df = styled_df.apply(lambda s: highlight_significant_rows(s, significance_level), subset=['P值'])
        st.table(styled_df)
    
        keys = list(results_fully_dynamic.keys())
        chi2_values = [res['Chi-Square'] for res in results_fully_dynamic.values()]
        p_values = [res['P值'] for res in results_fully_dynamic.values()]
    
        col1, col2 = st.columns(2)
        col1.title("卡方值")
        col1.bar_chart(pd.Series(chi2_values, index=keys, name="卡方值"), use_container_width=True)
        
        col2.title("P值")
        col2.bar_chart(pd.Series(p_values, index=keys, name="P值"), use_container_width=True)
        
        scatter_chart = alt.Chart(df_results).mark_circle(size=60).encode(
            x='卡方值',
            y='P值',
            tooltip=list(df.columns[:2]) + ['卡方值', 'P值']
        ).properties(
            width=600,
            height=400,
            title="卡方值 vs P值" 
        )
        st.altair_chart(scatter_chart, use_container_width=True)
        
    except Exception as e:
        st.write("转换数据时出错，请确保您粘贴的数据格式正确。")
        st.write(str(e))

def perform_event_impact_analysis(df, significance_level=0.05):
    # 适应不同的列名
    category_col = df.columns[0]
    event_col = df.columns[1]
    value_col = df.columns[2]
    
    categories = df[category_col].unique()
    events = df[event_col].unique()
    
    results = {}
    
    for category in categories:
        data_before_event = df[(df[category_col] == category) & (df[event_col] == events[0])][value_col].values
        data_after_event = df[(df[category_col] == category) & (df[event_col] == events[1])][value_col].values
        
        # If length of data is less than 3, use Mann-Whitney U by default
        if len(data_before_event) < 3 or len(data_after_event) < 3:
            u_stat, p_value = mannwhitneyu(data_before_event, data_after_event)
            t_stat = u_stat
            test_name = "Mann-Whitney U"
            reason = "样本数量小于3"
        else:
            # Check for normality using Shapiro-Wilk Test
            _, p_before = shapiro(data_before_event)
            _, p_after = shapiro(data_after_event)

            # If both data are normally distributed, perform t-test, otherwise Mann-Whitney U Test
            if p_before > significance_level and p_after > significance_level:
                t_stat, p_value = ttest_ind(data_before_event, data_after_event)
                test_name = "t-test"
                reason = ""
            else:
                u_stat, p_value = mannwhitneyu(data_before_event, data_after_event)
                t_stat = u_stat
                test_name = "Mann-Whitney U"
                non_normal_event = events[0] if p_before <= significance_level else events[1]
                reason = f"由于{non_normal_event}数据不属于正态分布"

        results[category] = {
            "测试方法": test_name,
            "统计量": t_stat,
            "P值": p_value,
            "原因": reason
        }

        # Display the results for each category
        st.write(f"{category} 使用 {test_name} (原因: {reason}), 统计量 = {t_stat}, p值 = {p_value}")
        conclusion = f"{category} 在两个事件之间的{value_col}存在显著差异。" if p_value < significance_level else f"{category} 在两个事件之间的{value_col}没有显著差异。"
        st.write(conclusion)




def highlight_significant_rows(s, significance_level):
    return ['background-color: yellow' if v < significance_level else '' for v in s]