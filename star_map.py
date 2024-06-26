import streamlit as st
import matplotlib.pyplot as plt
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
from skyfield.projections import build_stereographic_projection
from datetime import datetime, timezone
import numpy as np

def get_observer_location():
    # 기본값으로 서울의 위도와 경도를 사용
    return wgs84.latlon(37.5665, 126.9780)

def plot_sky(time, location):
    # 천체 데이터 로드
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)

    # 관측자 위치 설정
    planets = load('de421.bsp')
    earth = planets['earth']
    observer = earth + location

    # 별 위치 계산
    t = load.timescale().from_datetime(time)
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    alt, az, _ = observer.at(t).altaz()

    # 투영 설정
    center_alt = 90
    center_az = 0
    projection = build_stereographic_projection(center_alt, center_az)
    x, y = projection(alt.radians, az.radians)

    # 플롯 생성
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(x, y, s=10/stars.magnitude, alpha=0.5)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    # 컴파스 방향 표시
    for direction, angle in [('N', 0), ('E', 90), ('S', 180), ('W', 270)]:
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))
        ax.text(x*1.1, y*1.1, direction, ha='center', va='center')

    return fig

st.title('오늘 밤하늘의 별자리')

# 현재 시간 (UTC)
now = datetime.now(timezone.utc)
st.write(f"현재 시간 (UTC): {now}")

# 관측자 위치
location = get_observer_location()
st.write(f"관측 위치: 위도 {location.latitude.degrees:.2f}°, 경도 {location.longitude.degrees:.2f}°")

# 별자리 플롯 생성 및 표시
fig = plot_sky(now, location)
st.pyplot(fig)
