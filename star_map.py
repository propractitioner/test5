import streamlit as st
import matplotlib.pyplot as plt
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
from skyfield.projections import build_stereographic_projection
from datetime import datetime, timezone
import numpy as np

@st.cache_data
def load_star_data():
    with load.open(hipparcos.URL) as f:
        return hipparcos.load_dataframe(f)

def get_observer_location():
    return wgs84.latlon(37.5665, 126.9780)

def plot_sky(time, location):
    try:
        stars = load_star_data()
        
        planets = load('de421.bsp')
        earth = planets['earth']
        observer = earth + location

        t = load.timescale().from_datetime(time)
        star_positions = earth.at(t).observe(Star.from_dataframe(stars))
        alt, az, _ = observer.at(t).altaz()

        # 투영 설정 수정
        center_alt = 90  # 천정
        center_az = 0
        projection = build_stereographic_projection(np.radians(center_alt), np.radians(center_az))
        x, y = projection(az.radians, (90 - alt.degrees) * np.pi / 180)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.scatter(x, y, s=10/stars.magnitude, alpha=0.5)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect('equal')
        ax.axis('off')

        # 방향 표시 수정
        directions = ['N', 'E', 'S', 'W']
        for i, direction in enumerate(directions):
            theta = np.pi/2 - i*np.pi/2
            x = 1.8 * np.cos(theta)
            y = 1.8 * np.sin(theta)
            ax.text(x, y, direction, ha='center', va='center')

        return fig
    except Exception as e:
        st.error(f"An error occurred while plotting the sky: {str(e)}")
        return None

def main():
    st.title('오늘 밤하늘의 별자리')

    now = datetime.now(timezone.utc)
    st.write(f"현재 시간 (UTC): {now}")

    location = get_observer_location()
    st.write(f"관측 위치: 위도 {location.latitude.degrees:.2f}°, 경도 {location.longitude.degrees:.2f}°")

    fig = plot_sky(now, location)
    if fig:
        st.pyplot(fig)

if __name__ == "__main__":
    main()
