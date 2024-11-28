import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # 經緯度轉為弧度制
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    diff_lat = lat1 - lat2
    diff_lon = lon1 - lon2

    a = (
        math.sin(diff_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(diff_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 地球半徑
    R = 6371.0
    # 單位公里換算成公尺
    distance = R * c * 1000
    return distance


def get_lat_lng_bounds(lat: float, lng: float, distance_km: float):
    # 緯度和經度的增量計算
    delta_lat = distance_km / 111  # 緯度固定一度約為 111 公里
    delta_lng = distance_km / (111 * math.cos(math.radians(lat)))  # 經度與緯度相關

    # 計算邊界
    min_lat = lat - delta_lat
    max_lat = lat + delta_lat
    min_lng = lng - delta_lng
    max_lng = lng + delta_lng

    return min_lat, max_lat, min_lng, max_lng
