import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import requests
import time
from app.config import Config


class WeatherAdvisor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.climate_norms = self._load_climate_norms()

    def _load_climate_norms(self) -> Dict:
        climate_path = Path(Config.PROCESSED_DATA_DIR) / "climate_norms.json"
        if climate_path.exists():
            with open(climate_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_weather_forecast(self, lat: float, lon: float, days: int = 7) -> Optional[Dict]:
        if not lat or not lon:
            return None

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": "temperature_2m,precipitation",
            "forecast_days": days,
            "timezone": "auto"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Weather: ошибка Open-Meteo Forecast: {e}")
            return None

    def check_concrete_conditions(self, temp: float, rain: float) -> Tuple[bool, str]:
        if temp is None:
            return False, "Нет данных о температуре"
        
        if temp < 5:
            return False, f"Слишком холодно (+{temp}C). Нужны противоморозные добавки"
        elif temp > 30:
            return False, f"Слишком жарко (+{temp}C). Требуется постоянное увлажнение"
        elif rain > 0:
            return False, "Ожидаются дожди. Нужно укрывать бетон плёнкой"
        else:
            return True, "Условия благоприятные"

    def _normalize_city_name(self, city: str) -> str:
        return city.lower().strip()

    def get_climate_norms_from_api(self, lat: float, lon: float) -> Optional[List[Dict]]:
        """
        Получает климатические нормы (среднемесячные температуры и осадки)
        для ЛЮБОГО города через Open-Meteo Climate API.
        Использует ERA5/Land ре-анализ данных за последние 10 лет.
        """
        if not lat or not lon:
            return None

        current_year = datetime.now().year
        end_year = current_year - 1
        start_year = end_year - 10

        if start_year > end_year:
            start_year = end_year - 1

        print(f"Запрос климатических норм для {lat}, {lon} за {start_year}-{end_year}")

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": f"{start_year}-01-01",
            "end_date": f"{end_year}-12-31",
            "daily": "temperature_2m_mean,precipitation_sum",
            "timezone": "auto"
        }

        for attempt in range(3):
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                if "daily" not in data:
                    print(f"Climate: нет данных для координат {lat}, {lon}")
                    return None

                daily_data = data["daily"]
                times = daily_data.get("time", [])
                temps = daily_data.get("temperature_2m_mean", [])
                precip = daily_data.get("precipitation_sum", [])

                if not times:
                    return None

                monthly_data = {}
                for i, date in enumerate(times):
                    month = int(date[5:7])
                    if month not in monthly_data:
                        monthly_data[month] = {"temps": [], "precips": []}
                    if i < len(temps):
                        monthly_data[month]["temps"].append(temps[i])
                    if i < len(precip):
                        monthly_data[month]["precips"].append(precip[i])

                month_names_ru = {
                    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
                    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
                    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
                }

                result = []
                for month in range(1, 13):
                    if month in monthly_data and monthly_data[month]["temps"]:
                        avg_temp = sum(monthly_data[month]["temps"]) / len(monthly_data[month]["temps"])
                        avg_precip = sum(monthly_data[month]["precips"]) / len(monthly_data[month]["precips"]) if monthly_data[month]["precips"] else 0
                        
                        if avg_temp < 5:
                            can_pour = "Нет"
                        elif 5 <= avg_temp <= 30:
                            can_pour = "Да"
                        else:
                            can_pour = "С добавками"
                        
                        result.append({
                            "month": month_names_ru[month],
                            "temp": round(avg_temp, 1),
                            "rain_mm": round(avg_precip, 1),
                            "can_pour": can_pour
                        })
                    else:
                        result.append({
                            "month": month_names_ru[month],
                            "temp": None,
                            "rain_mm": None,
                            "can_pour": "Нет данных"
                        })

                print(f"Climate: получены нормы для {lat}, {lon}")
                return result

            except requests.exceptions.RequestException as e:
                print(f"Попытка {attempt+1} не удалась для {lat}, {lon}: {e}")
                if attempt == 2:
                    return None
                time.sleep(2)

        return None

    def get_climate_projections_from_api(self, lat: float, lon: float, months_ahead: int) -> Optional[Dict]:
        """Прогноз на будущие месяцы на основе климатических норм из API"""
        norms = self.get_climate_norms_from_api(lat, lon)
        if not norms:
            return None

        target_date = datetime.now() + timedelta(days=months_ahead * 30)
        target_month = target_date.month

        month_names_ru = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        for month_data in norms:
            if month_data["month"] == month_names_ru[target_month]:
                temp = month_data["temp"]
                precip = month_data["rain_mm"]
                
                if temp is None:
                    return None
                
                if temp < 5:
                    status = "Невозможно"
                    advice = "Слишком холодно, нужны противоморозные добавки"
                elif temp > 30:
                    status = "Опасно"
                    advice = "Слишком жарко, требуется постоянное увлажнение"
                else:
                    status = "Возможно"
                    advice = "Условия благоприятные"
                
                return {
                    "month": month_names_ru[target_month],
                    "temp": temp,
                    "rain_mm": precip if precip is not None else 0,
                    "status": status,
                    "advice": advice
                }

        return None

    def get_monthly_calendar(self, region: str, lat: float = None, lon: float = None) -> List[Dict]:
        """Возвращает климатический календарь для ЛЮБОГО города через API"""
        if lat and lon:
            norms = self.get_climate_norms_from_api(lat, lon)
            if norms:
                return norms
        
        # Fallback: если API не дал данных, пробуем из локального JSON
        norms = self.climate_norms.get(self._normalize_city_name(region), {})
        months_data = norms.get("months", {})

        calendar = []
        month_names_ru = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        for month_num in range(1, 13):
            month_str = str(month_num)
            if month_str in months_data:
                data = months_data[month_str]
                temp = data.get("temp", 0)
                rain = data.get("rain_mm", 0)

                if temp < 5:
                    can_pour = "Нет"
                elif 5 <= temp <= 30:
                    can_pour = "Да"
                else:
                    can_pour = "С добавками"

                calendar.append({
                    "month": month_names_ru[month_num],
                    "temp": temp,
                    "rain_mm": rain,
                    "can_pour": can_pour
                })
            else:
                calendar.append({
                    "month": month_names_ru[month_num],
                    "temp": None,
                    "rain_mm": None,
                    "can_pour": "Нет данных"
                })

        return calendar

    def get_future_forecast(self, region: str, current_month_num: int, months_ahead: int, lat: float = None, lon: float = None) -> Optional[Dict]:
        """Прогноз на будущие месяцы через API или локальный JSON"""
        if lat and lon:
            future = self.get_climate_projections_from_api(lat, lon, months_ahead)
            if future:
                return future

        # Fallback: локальный JSON
        norms = self.climate_norms.get(self._normalize_city_name(region), {})
        months_data = norms.get("months", {})

        if not months_data:
            return None

        target_month_num = ((current_month_num - 1) + months_ahead) % 12 + 1
        target_month_str = str(target_month_num)

        month_names_ru = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        if target_month_str in months_data:
            data = months_data[target_month_str]
            temp = data.get("temp", 0)

            if temp < 5:
                status = "Невозможно"
                advice = "Ждите тёплого сезона"
            elif 5 <= temp <= 30:
                status = "Возможно"
                advice = "Условия благоприятные"
            else:
                status = "С добавками"
                advice = "Требуются противоморозные добавки"

            return {
                "month": month_names_ru[target_month_num],
                "temp": temp,
                "rain_mm": data.get("rain_mm", 0),
                "status": status,
                "advice": advice
            }

        return None

    def get_daily_forecast(self, lat: float, lon: float) -> List[Dict]:
        forecast_data = self.get_weather_forecast(lat, lon, 7)
        if not forecast_data:
            return []

        daily = []
        
        current = forecast_data.get("current_weather", {})
        temp = current.get("temperature")
        
        can_pour, message = self.check_concrete_conditions(temp, 0)
        daily.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "temp": temp if temp is not None else 0,
            "condition": "без осадков",
            "can_pour": can_pour,
            "recommendation": message
        })

        hourly = forecast_data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        precipitation = hourly.get("precipitation", [])
        
        days_data = {}
        for i, time in enumerate(times):
            date = time[:10]
            if date not in days_data:
                days_data[date] = {"temps": [], "rains": []}
            if i < len(temps):
                days_data[date]["temps"].append(temps[i])
            if i < len(precipitation):
                days_data[date]["rains"].append(precipitation[i])
        
        for date, data in list(days_data.items())[1:6]:
            avg_temp = sum(data["temps"]) / len(data["temps"]) if data["temps"] else 0
            max_rain = sum(data["rains"]) / len(data["rains"]) if data["rains"] else 0
            condition = "дождь" if max_rain > 0 else "без осадков"
            can_pour, message = self.check_concrete_conditions(avg_temp, max_rain)
            
            daily.append({
                "date": date,
                "temp": round(avg_temp, 1),
                "condition": condition,
                "can_pour": can_pour,
                "recommendation": message
            })
        
        return daily

    def get_recommendation(self, region: str, desired_month: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None) -> Dict:
        if not lat or not lon:
            return {
                "region": region,
                "selected_month": desired_month or "",
                "optimal_season": "координаты не определены",
                "current_month_optimal": "не определено",
                "warning": "Не удалось определить местоположение",
                "concrete_rules": "Бетонирование при +5C до +30C, без дождя",
                "monthly_calendar": [],
                "future_forecast": {"3_months": None, "6_months": None},
                "daily_forecast": [],
                "best_day": None
            }
        
        daily_forecast = self.get_daily_forecast(lat, lon)
        
        # Климатический календарь через API (для любого города)
        monthly_calendar = self.get_monthly_calendar(region, lat, lon)
        
        current_month_num = datetime.now().month
        future_3 = self.get_future_forecast(region, current_month_num, 3, lat, lon)
        future_6 = self.get_future_forecast(region, current_month_num, 6, lat, lon)
        
        best_day = None
        for day in daily_forecast:
            if day["can_pour"]:
                best_day = day["date"]
                break
        
        return {
            "region": region,
            "selected_month": desired_month or "",
            "optimal_season": "по данным Open-Meteo",
            "current_month_optimal": "прогноз получен",
            "warning": "",
            "concrete_rules": "Бетонирование при +5C до +30C, без дождя",
            "monthly_calendar": monthly_calendar,
            "future_forecast": {"3_months": future_3, "6_months": future_6},
            "daily_forecast": daily_forecast,
            "best_day": best_day
        }