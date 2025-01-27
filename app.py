import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO

# Установка глобальных параметров для визуализаций
def configure_visualizations():
    sns.set(style="whitegrid", palette="muted")
    plt.rcParams.update({
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 16
    })

# Установка фона для шапки с картинкой
def set_header_background(image_url):
    header_style = f"""
    <style>
    .reportview-container .main .block-container {{
        padding-top: 3rem;
    }}
    .css-1v3fvcr {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        color: white;
        padding: 2rem;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        height: 200px;  /* Установите высоту шапки */
    }}
    </style>
    """
    st.markdown(header_style, unsafe_allow_html=True)

# Загрузка и предобработка данных
def load_and_preprocess_data(uploaded_file):
    data = pd.read_excel(uploaded_file)
    data['service_date'] = pd.to_datetime(data['service_date'])
    data.drop_duplicates(inplace=True)
    
    data['year'] = data['service_date'].dt.year
    data['month'] = data['service_date'].dt.to_period("M")
    
    bins = [0, 18, 35, 50, 65, 80, 100]
    labels = ["0-18", "19-35", "36-50", "51-65", "66-80", "81-100"]
    data["age_group"] = pd.cut(data["age_for_service_date"], bins=bins, labels=labels)
    
    return data

# Расчёт ключевых метрик
def calculate_metrics(data):
    metrics = {
        "unique_patients": data["insured"].nunique(),
        "unique_services": data["service_name"].nunique(),
        "unique_visits": data.groupby(["insured", "service_date"]).ngroups,
        "gender_distribution": data["sex_id"].value_counts(),
        "age_distribution": data["age_group"].value_counts().sort_index(),
        "monthly_distribution": data["month"].value_counts().sort_index(),
        "top_services": data["service_name"].value_counts().head(10)
    }
    return metrics

# Графики
def plot_gender_distribution(data):
    gender_yearly = data.groupby(["year", "sex_id"]).size().reset_index(name="count")
    gender_yearly["sex_id"] = gender_yearly["sex_id"].map({1: "Мужчины", 2: "Женщины"})
    
    plt.figure(figsize=(5, 3))  # Значительно уменьшенный размер графика
    sns.barplot(
        x="sex_id", y="count", hue="year", data=gender_yearly,
        palette=["#6495ED", "#FFB6C1"], edgecolor="black", alpha=0.85
    )
    plt.title("Распределение пациентов по полу (2021 vs 2022)")
    plt.xlabel("Пол")
    plt.ylabel("Количество пациентов")
    plt.legend(title="Год")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()  # Подгонка графика для уменьшения лишнего пространства
    st.pyplot(plt)

def plot_age_distribution(data):
    age_yearly = data.groupby(["year", "age_group"]).size().reset_index(name="count")
    
    plt.figure(figsize=(6, 3))  # Уменьшенный размер графика
    sns.barplot(
        x="age_group", y="count", hue="year", data=age_yearly,
        palette=["#90EE90", "#FFCCCB"], edgecolor="black", alpha=0.85
    )
    plt.title("Распределение пациентов по возрастным группам (2021 vs 2022)")
    plt.xlabel("Возрастная группа")
    plt.ylabel("Количество пациентов")
    plt.legend(title="Год")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()  # Подгонка графика для уменьшения лишнего пространства
    st.pyplot(plt)

def plot_monthly_distribution(metrics):
    monthly_distribution = metrics["monthly_distribution"]
    
    plt.figure(figsize=(6, 3))  # Уменьшенный размер графика
    sns.barplot(
        x=monthly_distribution.index.astype(str), y=monthly_distribution.values,
        color="#FFCCCB", edgecolor="black", alpha=0.85
    )
    plt.title("Распределение визитов по месяцам")
    plt.xlabel("Месяц")
    plt.ylabel("Количество визитов")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()  # Подгонка графика для уменьшения лишнего пространства
    st.pyplot(plt)

def plot_top_services(metrics):
    top_services = metrics["top_services"]
    
    plt.figure(figsize=(6, 3))  # Уменьшенный размер графика
    sns.barplot(
        x=top_services.values, y=top_services.index, palette="magma",
        edgecolor="black", alpha=0.85
    )
    plt.title("Топ-10 самых популярных услуг")
    plt.xlabel("Количество оказанных услуг")
    plt.ylabel("Название услуги")
    plt.tight_layout()  # Подгонка графика для уменьшения лишнего пространства
    st.pyplot(plt)

# Основная функция для анализа данных
def analyze_medical_data(uploaded_file):
    # Оформление страницы
    st.set_page_config(
        page_title="Тестовое задание Иванова Виктория",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Заголовок страницы
    st.title("Тестовое задание Иванова Виктория")
    st.write("""
    В приложении представлен анализ данных об обращениях в медицинскую клинику за 2021 и 2022 годы.
    """)

    # Укажите путь к картинке
    image_url = '/Users/viktoriasmeleva/Desktop/Meditsina-innovatsii.jpeg'  # Замените на путь к вашему изображению

    # Установка фона с картинкой
    set_header_background(image_url)

    configure_visualizations()
    data = load_and_preprocess_data(uploaded_file)
    metrics = calculate_metrics(data)
    
    # Вывод метрик в Streamlit
    st.write(f"Уникальных пациентов: {metrics['unique_patients']}")
    st.write(f"Уникальных услуг: {metrics['unique_services']}")
    st.write(f"Уникальных визитов: {metrics['unique_visits']}")
    
    # Построение графиков
    plot_gender_distribution(data)
    plot_age_distribution(data)
    plot_monthly_distribution(metrics)
    plot_top_services(metrics)
    
    # Выводы по анализу
    st.subheader("Основные выводы")
    st.write("""
    1. **Распределение по полу:**  
       Женщины составляют большую часть пациентов, их доля значительно выросла в 2022 году.
    
    2. **Распределение по возрасту:**  
       Основную часть пациентов составляют группы 19-35 и 36-50 лет.  
       Значительный рост отмечается среди пациентов 19-35 лет.
    
    3. **Динамика визитов:**  
       Наибольшее число визитов приходится на апрель и июль.  
       В 2022 году общее число визитов значительно выше, чем в 2021.
    
    4. **Популярность услуг:**  
       Первичный прием — самая востребованная услуга среди пациентов.
    """)

# Загружаем файл через Streamlit
uploaded_file = st.file_uploader("Выберите Excel файл", type=["xlsx"])

if uploaded_file is not None:
    analyze_medical_data(uploaded_file)
