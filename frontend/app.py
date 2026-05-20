import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="ИИ-КОНСУЛЬТАНТ ПО ПОДБОРУ ФУНДАМЕНТА ДЛЯ ИЖС",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.markdown("""
<style>
    header {
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
    [data-testid="stThemeToggle"] {
        display: none !important;
    }
    #MainMenu {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .main .block-container {
        padding-top: 1rem !important;
    }
    .stApp {
        background-color: #0e1117 !important;
    }
    html, body, [class*="css"] {
        color: #e0e0e0 !important;
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
        color: #ffffff !important;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #2a2c3a !important;
        border: 1px solid #4a4e6e !important;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .stButton > button {
        background-color: #4c9aff !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background-color: #2a6eb0 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1c2e;
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2a2c3a;
        border-radius: 8px;
        color: #bbbbbb;
        padding: 6px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4c9aff !important;
        color: #ffffff !important;
    }
    .streamlit-expanderHeader {
        background-color: #1a1c2e;
        border: 1px solid #2d2d44;
        border-radius: 12px;
        color: #ffffff;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background-color: #1a1c2e;
        border-radius: 12px;
        border: 1px solid #2d2d44;
        margin-top: 5px;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"] {
        color: #bbbbbb !important;
    }
    .dataframe {
        background-color: #1a1c2e !important;
    }
    .dataframe th {
        background-color: #2a2c3a !important;
        color: #ffffff !important;
    }
    .dataframe td {
        color: #cccccc !important;
    }
    .stAlert {
        background-color: #2a2c3a !important;
        border-left: 4px solid #4c9aff !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

if "history" not in st.session_state:
    st.session_state.history = []

st.title("ИИ-КОНСУЛЬТАНТ ПО ПОДБОРУ ФУНДАМЕНТА ДЛЯ ИЖС")
st.markdown("Опишите ваш дом и участок, и ИИ подберёт оптимальный фундамент с расчётом стоимости и учётом погоды")

col1, col2 = st.columns(2)
with col1:
    city = st.text_input("Город", placeholder="Москва, Сургут, Краснодар")
with col2:
    address = st.text_input("Улица и дом (желательно)", placeholder="ул. Тверская 15")

user_input = st.text_area(
    "Описание дома и участка",
    placeholder="Пример: Дом из газобетона, 2 этажа, размер 10 на 8 метров, грунт — суглинок",
    height=120
)

with st.expander("НАСТРОЙКИ"):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        uploaded_file = st.file_uploader("Загрузить отчёт по геологии (PDF)", type=["pdf"])
        budget = st.select_slider(
            "Ваш бюджет (тыс. руб)",
            options=["до 300", "300-500", "500-800", "800-1200", "1200+"],
            value="500-800"
        )
        self_build = st.checkbox("Буду строить своими руками")
    with col_s2:
        months = ["январь", "февраль", "март", "апрель", "май", "июнь",
                  "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
        desired_month = st.selectbox(
            "Желаемый месяц начала работ", ["не важно"] + months
        )
        
        st.markdown("---")
        st.markdown("**История запросов**")
        if st.session_state.history:
            for item in reversed(st.session_state.history[-5:]):
                st.markdown(f"- {item['timestamp']} – {item['city']} – {item['foundation']}")
                st.caption(f"{item['query']}...")
        else:
            st.caption("Пока нет истории")

col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    submit = st.button("ПОДОБРАТЬ ФУНДАМЕНТ", use_container_width=True)

if submit:
    if not user_input:
        st.warning("Пожалуйста, опишите ваш дом и участок")
    elif not city:
        st.warning("Пожалуйста, укажите город")
    else:
        with st.spinner("Анализируем данные, ищем в СНиПах, считаем стоимость..."):
            payload = {
                "user_input": user_input,
                "city": city,
                "address": address if address else None,
                "desired_month": desired_month if desired_month != "не важно" else None,
                "budget": budget,
                "self_build": self_build
            }
            try:
                response = requests.post(f"{API_URL}/consult", json=payload, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    
                    st.session_state.history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "query": user_input[:80],
                        "city": city,
                        "foundation": result.get("foundation_type", "Не определён")
                    })
                    
                    tab1, tab2, tab3, tab4 = st.tabs(
                        ["РЕКОМЕНДАЦИЯ", "СМЕТА", "ПОГОДА И КАЛЕНДАРЬ", "МАГАЗИНЫ"]
                    )
                    
                    with tab1:
                        st.markdown(result.get("answer", "Нет данных"))
                        if result.get("sources"):
                            st.divider()
                            st.markdown("Источники")
                            for src in result["sources"]:
                                st.markdown(f"- {src}")
                    
                    with tab2:
                        ce = result.get("cost_estimate", {})
                        st.subheader(f"Тип: {result.get('foundation_type', 'Не определён')}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Материалы", f"{ce.get('materials', 0):,.0f} руб")
                        c2.metric("Работа", f"{ce.get('work', 0):,.0f} руб")
                        c3.metric("Доставка", f"{ce.get('delivery', 0):,.0f} руб")
                        st.divider()
                        st.metric("ИТОГО", f"{ce.get('total', 0):,.0f} руб")
                        if ce.get("self_build"):
                            st.success("Строительство своими руками — работа исключена")
                        if ce.get("pile_count"):
                            st.caption(f"Количество свай: {ce['pile_count']} шт")
                    
                    with tab3:
                        w = result.get("weather_recommendation", {})
                        st.subheader(f"Регион: {w.get('region', city).title()}")
                        st.write(f"Оптимальный сезон: {w.get('optimal_season', 'май-сентябрь')}")
                        st.write(f"Оценка выбранного месяца: {w.get('current_month_optimal', 'не выбрано')}")
                        if w.get("warning"):
                            st.warning(w["warning"])
                        if w.get("monthly_calendar"):
                            st.dataframe(pd.DataFrame(w["monthly_calendar"]), use_container_width=True)
                        if w.get("future_forecast"):
                            future_3 = w["future_forecast"].get("3_months")
                            future_6 = w["future_forecast"].get("6_months")
                            if future_3 or future_6:
                                col_f1, col_f2 = st.columns(2)
                                if future_3:
                                    with col_f1:
                                        st.markdown(f"**Через 3 месяца ({future_3['month']}):**")
                                        st.write(f"Температура: {future_3['temp']}C")
                                        st.write(f"Статус: {future_3['status']}")
                                if future_6:
                                    with col_f2:
                                        st.markdown(f"**Через 6 месяцев ({future_6['month']}):**")
                                        st.write(f"Температура: {future_6['temp']}C")
                                        st.write(f"Статус: {future_6['status']}")
                        if w.get("daily_forecast"):
                            st.subheader("Прогноз на ближайшие дни")
                            for day in w["daily_forecast"][:5]:
                                st.write(f"{day['date']}: {day['temp']}°C, {day['condition']} → {'✅' if day['can_pour'] else '❌'}")
                        st.info(w.get("concrete_rules", "Правила бетонирования не заданы"))
                    
                    with tab4:
                        stores = result.get("stores", [])
                        if stores:
                            for s in stores:
                                with st.expander(s.get("store_name", "Магазин")):
                                    if s.get("address"):
                                        st.write(f"Адрес: {s['address']}")
                                    if s.get("distance_km"):
                                        st.write(f"Расстояние: {s['distance_km']} км")
                                    if s.get("search_url"):
                                        st.markdown(f"[Перейти к товарам]({s['search_url']})")
                        else:
                            st.info("Магазины не найдены")
                else:
                    st.error(f"Ошибка сервера: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Сервер не доступен. Запустите бэкенд на порту 8000")
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")