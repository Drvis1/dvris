from langchain_core.tools import tool
import requests
from config.settings import settings

hefeng_api_key=settings.HEFENG_API_KEY

@tool
def get_weather(city: str) -> str:
    """
    查询指定地区今天天气与温度
    :param city: 城市名称，如：南京、上海
    """
    try:
        #获取和风天气的密钥
        headers={
            "hefeng_api_key":hefeng_api_key
        }
        #获取用户所查询城市的具体经纬度
        geoapi_url=f"https://k92k5r522w.re.qweatherapi.com/geo/v2/city/lookup?location={city}"
        geoapi=requests.get(
            url=geoapi_url,
            headers=headers
        ).json()
        lat,lon=None,None
        for item in geoapi["location"]:
            if item["name"]==city:
                lat=item["lat"]
                lon=item["lon"]
        #根据所获得的经纬度获取当天城市的天气以及温度
        wea_url=f"https://k92k5r522w.re.qweatherapi.com/weather/v1/daily/{lat}/{lon}?days=1"
        wea=requests.get(
            url=wea_url,
            headers=headers
        ).json()
        tod=wea["days"][0]["daytime"]
        weather=tod["condition"]["text"]
        max_tem=tod["temperatureMax"]["value"]
        min_tem=tod["temperatureMin"]["value"]
        return f"你所查询的城市{city}，当天的天气为{weather},温度在{min_tem}~{max_tem}之间"
    except Exception:
        raise ValueError("天气查询失败")