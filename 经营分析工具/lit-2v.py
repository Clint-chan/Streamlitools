import io
import base64
import numpy as np
from scipy.stats import shapiro, ttest_ind
from descriptive_stats import *
from alth import *
hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
def get_file_content_as_string(file_path):
    with open(file_path, 'rb') as f:
        binary_content = f.read()
    return base64.b64encode(binary_content).decode('utf-8')

def app():
    st.set_page_config(page_title="经营分析统计工具", layout="wide",page_icon="logo_LBX.png")
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    st.title("经营分析统计工具")

    st.write("""
    欢迎使用经营分析统计工具！本工具旨在提供卡方检验、事件分析（T检验和U检验）以及描述性统计，帮助您更好地理解数据并做出明智的决策。"""
    )

    col1, col2 = st.columns([1, 3])
    significance_level = col1.number_input("显著性水平", min_value=0.01, max_value=0.99, value=0.05, step=0.01)
    analysis_method = col1.selectbox("分析方法", ["卡方检验", "描述性统计", "事件影响"])

    # 检查用户是否已经提供了数据
    if 'data' in st.session_state:
        data = st.session_state.data
    else:
        data = col2.text_area("请在此处粘贴Excel数据：", height=200, key="data_input")
    if 'edited_df' not in st.session_state and data:
        data_io = io.StringIO(data)
        try:
            df = pd.read_csv(data_io, sep='\t')
            st.session_state.edited_df = df
            st.dataframe(df)

            if st.button("确认数据"):
                st.session_state.data = data

        except Exception as e:
            st.write("转换数据时出错，请确保您粘贴的数据格式正确。")
            st.write(str(e))
    if 'edited_df' in st.session_state:
        edited_df = st.session_state.edited_df
        if st.button(f"执行{analysis_method}"):
            if analysis_method == "卡方检验":
                 perform_chi_square_analysis(st.session_state.edited_df, significance_level)

            if analysis_method == "描述性统计":
                perform_descriptive_stats(edited_df)
                
            elif analysis_method == "事件影响":
                perform_event_impact_analysis(edited_df, significance_level)
    st.sidebar.header("用户文档")
    b64_content = get_file_content_as_string('chi_square_template.xlsx')
    st.sidebar.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_content}' download='chi_square_template.xlsx'>下载模板文件</a>", unsafe_allow_html=True)                
    st.sidebar.write("""
    **1. 使用方法：**
    - 下载模板文件，导入数据后在下面的文本框中粘贴Excel数据。
    - 选择分析方法并点击对应的执行按钮。
    
    **2. 注意事项：**
    - 请确保数据的格式正确，且没有缺失或异常值，具体请参考附件-模板文件
    - 如果遇到任何问题或错误，请联系**经营分析部**。
    ## 帮助
    ### 二维卡方检验

    二维卡方检验是一种用于检验两个分类变量之间是否相关的统计方法。具体来说：
    - 每一组（如学历与年龄的组合）都与其自己的期望值进行比较。
    - 该方法适用于确定哪些特定的组合或子集与期望值有显著差异。
    - 结果可以帮助我们识别那些异常的组合或子集，即那些与总体或其他组不同的子集。
    - 例如，如果我们发现“小学 26-35”组的购买行为与期望值有显著差异，那么我们可以针对该特定组合制定特定的市场策略或进一步研究。

    ### 描述性统计

    描述性统计是用于描述、展示或汇总数据集特性的统计方法。这可以提供数据集的简单概览，包括中心趋势、分散和形状的度量。常见的描述性统计方法包括均值、中位数、众数、标准差等。

    ### 事件影响分析

    事件影响分析是用于评估单一事件或多个事件对特定变量的影响的统计方法。这种分析可以帮助我们理解事件发生后的短期和长期效应。常见的方法包括T检验和U检验。

    使用此工具进行分析时，请确保您提供的数据格式正确，以便获得准确的结果。
    """)
if __name__ == "__main__":
    app()
#streamlit run lit-2v.py