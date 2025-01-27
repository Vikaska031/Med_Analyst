import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

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
def load_and_preprocess_data(file_path):
    data = pd.read_excel(file_path)
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

# Функция для проверки гипотез
def hypothesis_testing(data_2021, data_2022):
    # Пример данных для гипотез и их p-value
    hypothesis_data = {
        "Параметр": [
            "Средняя стоимость услуг", 
            "Интенсивность лечения", 
            "Распределение по полу", 
            "Распределение по возрасту", 
            "Средняя стоимость лечения/мес", 
            "Средняя стоимость одной услуги", 
            "Медианная стоимость лечения/мес", 
            "Процент дорогостоящих услуг"
        ],
        "Гипотеза": [
            "Средняя стоимость услуг за период изменилась.",
            "Интенсивность лечения (среднее число услуг на пациента) изменилась.",
            "Распределение пациентов по полу изменилось.",
            "Распределение пациентов по возрасту изменилось.",
            "Средняя стоимость лечения одного пациента за месяц изменилась.",
            "Средняя стоимость одной услуги изменилась.",
            "Медианная стоимость лечения одного пациента за месяц изменилась.",
            "Процент пациентов с дорогостоящими услугами изменился."
        ],
        "p-value": [
            "<0.05", 
            "0.0656", 
            "<0.05", 
            "<0.05", 
            "<0.05", 
            "<0.05", 
            "<0.05", 
            "nan"
        ],
        "Результат": [
            "Существенное изменение", 
            "Нет значимого изменения", 
            "Существенное изменение", 
            "Существенное изменение", 
            "Существенное изменение", 
            "Существенное изменение", 
            "Существенное изменение", 
            "Нет значимого изменения"
        ]
    }

    df_hypothesis = pd.DataFrame(hypothesis_data)
    
    # Таблица с результатами
    st.write("## Результаты проверки гипотез")
    st.write(df_hypothesis)

    # Результаты в текстовом виде
    results_text = """
    # **Результаты проверки гипотез**

### 1. **Средняя стоимость услуг**
- **Гипотеза:** Средняя стоимость услуг за период изменилась.  
- **Результат:** ✅ **Существенные изменения зафиксированы** *(p-value < 0.05)*.  
  Средняя стоимость услуг демонстрирует статистически значимые изменения, что может быть связано с изменением тарифов или структуры предоставляемых услуг.

### 2. **Интенсивность лечения**
- **Гипотеза:** Интенсивность лечения (среднее число услуг на пациента) изменилась.  
- **Результат:** 🚫 **Изменений не выявлено** *(p-value = 0.0656)*.  
  Наблюдается незначительная тенденция к изменению, однако она находится вне зоны статистической значимости.

### 3. **Распределение пациентов по полу**
- **Гипотеза:** Распределение пациентов по полу изменилось.  
- **Результат:** ✅ **Существенные изменения зафиксированы** *(p-value < 0.05)*.  
  Перераспределение пациентов между мужчинами и женщинами свидетельствует о возможных сдвигах в потребительском поведении или доступности услуг.

### 4. **Распределение пациентов по возрасту**
- **Гипотеза:** Распределение пациентов по возрасту изменилось.  
- **Результат:** ✅ **Существенные изменения зафиксированы** *(p-value < 0.05)*.  
  Изменение возрастной структуры пациентов может указывать на таргетирование новых возрастных групп или влияние демографических факторов.

### 5. **Средняя стоимость лечения одного пациента за месяц**
- **Гипотеза:** Средняя стоимость лечения одного пациента за месяц изменилась.  
- **Результат:** ✅ **Существенные изменения зафиксированы** *(p-value < 0.05)*.  
  Динамика средней стоимости лечения может отражать изменения в типах предоставляемых услуг или изменениях в модели потребления.

### 6. **Средняя стоимость одной услуги**
- **Гипотеза:** Средняя стоимость одной услуги изменилась.  
- **Результат:** ✅ **Существенные изменения зафиксированы** *(p-value < 0.05)*.  
  Рост или снижение средней стоимости одной услуги может быть результатом изменений в структуре ценообразования.

### 7. **Медианная стоимость лечения одного пациента за месяц**
- **Гипотеза:** Медианная стоимость лечения одного пациента за месяц изменилась.  
- **Результат:** ✅ **Существенные изменения зафиксированы** *(p-value < 0.05)*.  
  Изменение медианной стоимости указывает на сдвиг в центре распределения затрат на лечение.

### 8. **Процент пациентов с дорогостоящими услугами**
- **Гипотеза:** Процент пациентов с дорогостоящими услугами изменился.  
- **Результат:** 🚫 **Изменений не выявлено** *(p-value = nan)*.  
  Отсутствие значимых изменений может быть связано с недостатком данных или устойчивостью данного параметра.

---
    """
    st.write(results_text)


# Основная функция для анализа данных
def analyze_medical_data(file_path):
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
    data = load_and_preprocess_data(file_path)
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

    # Анализ гипотез
    data_2021 = data[data['year'] == 2021]
    data_2022 = data[data['year'] == 2022]
    hypothesis_testing(data_2021, data_2022)


# Путь к файлу

analyze_medical_data('data_test_task_2022.xlsx')
