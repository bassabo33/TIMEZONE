
import streamlit as st
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# ============================================================
#                    基本設定
# ============================================================

st.set_page_config(
    page_title="全球時間比較器",
    page_icon="🌏",
    layout="wide"
)

TAIPEI_TZ = ZoneInfo("Asia/Taipei")

CITIES = {
    "紐西蘭威靈頓": "Pacific/Auckland",
    "澳洲雪梨": "Australia/Sydney",
    "西班牙札拉哥沙": "Europe/Madrid",
    "英國倫敦": "Europe/London",
    "美國紐約": "America/New_York",
    "巴西聖保羅": "America/Sao_Paulo",
    "墨西哥墨西哥市": "America/Mexico_City",
    "美國舊金山": "America/Los_Angeles",
    "美國夏威夷": "Pacific/Honolulu",
}

DEFAULT_CITIES = [
    "澳洲雪梨",
    "西班牙札拉哥沙",
    "巴西聖保羅",
    "美國舊金山",
    "美國夏威夷",
]

TIME_OPTIONS = [
    "即時",
    "10:00",
    "11:00",
    "14:00",
    "17:00",
    "18:00",
    "20:00",
]

# ============================================================
#                    CSS 樣式
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F4F6F8;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .main-title {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 28px;
        font-weight: bold;
        color: #222222;
        margin-bottom: 4px;
    }

    .subtitle {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 14px;
        color: #666666;
        margin-bottom: 24px;
    }

    .column-header {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 14px;
        font-weight: bold;
        color: #555555;
        padding: 0 8px 8px 8px;
    }

    .result-time {
        font-family: Consolas, monospace;
        font-size: 20px;
        font-weight: bold;
        color: #222222;
    }

    .result-detail {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 12px;
        color: #777777;
    }

    .timezone-note {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 12px;
        color: #555555;
        line-height: 1.5;
    }

    .timezone-offset {
        font-family: Consolas, monospace;
        font-size: 12px;
        color: #777777;
    }

    .footer-note {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 12px;
        color: #777777;
        margin-top: 18px;
    }

    div[data-testid="stSelectbox"] {
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
#                    Session State
# ============================================================

if "cities" not in st.session_state:
    st.session_state.cities = DEFAULT_CITIES.copy()

if "selected_time" not in st.session_state:
    st.session_state.selected_time = "即時"

for i in range(5):
    if f"time_{i}" not in st.session_state:
        st.session_state[f"time_{i}"] = "即時"


# ============================================================
#                    時間計算
# ============================================================

def get_city_datetime(city_name):
    """取得指定城市的當地時間。"""

    timezone_obj = ZoneInfo(CITIES[city_name])
    city_now = datetime.now(timezone_obj)

    if st.session_state.selected_time == "即時":
        return city_now

    hour, minute = map(
        int,
        st.session_state.selected_time.split(":")
    )

    return city_now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )


def get_taiwan_datetime(city_datetime):
    """將城市時間換算成台灣時間。"""

    return city_datetime.astimezone(TAIPEI_TZ)


def get_day_difference(city_datetime, taiwan_datetime):
    """計算兩地日期差異。"""

    return (
        taiwan_datetime.date() - city_datetime.date()
    ).days


def format_day_difference(diff):
    if diff == 0:
        return "同一天"
    elif diff > 0:
        return f"台灣 +{diff} 天"
    else:
        return f"台灣 {diff} 天"


# ============================================================
#                    時區備註
# ============================================================

def get_timezone_info(city_name, city_datetime):
    """
    根據城市當地時間判斷：
    1. 是否使用夏令時間
    2. 時區縮寫
    3. UTC 時差
    """

    timezone_obj = ZoneInfo(CITIES[city_name])

    # 取得該日期的 UTC 偏移
    utc_offset = city_datetime.utcoffset()

    if utc_offset is None:
        utc_offset = timedelta(0)

    total_seconds = int(utc_offset.total_seconds())

    sign = "+" if total_seconds >= 0 else "-"
    abs_seconds = abs(total_seconds)

    hours = abs_seconds // 3600
    minutes = (abs_seconds % 3600) // 60

    utc_text = f"UTC{sign}{hours:02d}:{minutes:02d}"

    # 取得時區縮寫
    abbreviation = city_datetime.tzname() or ""

    # 判斷是否為夏令時間
    dst_offset = city_datetime.dst()

    if dst_offset is None:
        dst_offset = timedelta(0)

    if dst_offset != timedelta(0):
        status = "夏令時間"
    else:
        # 判斷該時區是否有其他日期會使用夏令時間
        has_dst = False

        for month in range(1, 13):
            check_date = datetime(
                city_datetime.year,
                month,
                15,
                12,
                0,
                tzinfo=timezone_obj
            )

            if check_date.dst() not in (
                None,
                timedelta(0)
            ):
                has_dst = True
                break

        if has_dst:
            status = "非夏令時間"
        else:
            status = "無夏令時間"

    return status, abbreviation, utc_text


# ============================================================
#                    時間同步
# ============================================================

def sync_time(index):
    """當任意一列時間改變時，同步五列。"""

    new_time = st.session_state[f"time_{index}"]

    st.session_state.selected_time = new_time

    for i in range(5):
        st.session_state[f"time_{i}"] = new_time


# ============================================================
#                    頁面標題
# ============================================================

st.markdown(
    '<div class="main-title">全球時間比較器</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '選擇城市及當地時間，右側自動換算成台灣時間'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
#                    欄位標題
# ============================================================

header1, header2, header3, header4 = st.columns(
    [2.0, 1.5, 2.0, 2.0],
    vertical_alignment="center"
)

with header1:
    st.markdown(
        '<div class="column-header">城市</div>',
        unsafe_allow_html=True
    )

with header2:
    st.markdown(
        '<div class="column-header">當地時間</div>',
        unsafe_allow_html=True
    )

with header3:
    st.markdown(
        '<div class="column-header">台灣對應時間</div>',
        unsafe_allow_html=True
    )

with header4:
    st.markdown(
        '<div class="column-header">時區備註</div>',
        unsafe_allow_html=True
    )


# ============================================================
#                    五個城市時間列
# ============================================================

for i in range(5):

    city_col, time_col, result_col, note_col = st.columns(
        [2.0, 1.5, 2.0, 2.0],
        vertical_alignment="center"
    )

    # --------------------------------------------------------
    # 城市選擇
    # --------------------------------------------------------

    with city_col:

        selected_city = st.selectbox(
            "城市",
            options=list(CITIES.keys()),
            index=list(CITIES.keys()).index(
                st.session_state.cities[i]
            ),
            key=f"city_{i}",
            label_visibility="collapsed"
        )

        st.session_state.cities[i] = selected_city

    # --------------------------------------------------------
    # 時間選擇
    # --------------------------------------------------------

    with time_col:

        st.selectbox(
            "當地時間",
            options=TIME_OPTIONS,
            key=f"time_{i}",
            label_visibility="collapsed",
            on_change=sync_time,
            args=(i,)
        )

    # --------------------------------------------------------
    # 時間換算
    # --------------------------------------------------------

    city_datetime = get_city_datetime(selected_city)

    taiwan_datetime = get_taiwan_datetime(
        city_datetime
    )

    day_diff = get_day_difference(
        city_datetime,
        taiwan_datetime
    )

    if st.session_state.selected_time == "即時":
        taiwan_time_text = taiwan_datetime.strftime(
            "%H:%M:%S"
        )
    else:
        taiwan_time_text = taiwan_datetime.strftime(
            "%H:%M"
        )

    # --------------------------------------------------------
    # 時區備註
    # --------------------------------------------------------

    status, abbreviation, utc_text = get_timezone_info(
        selected_city,
        city_datetime
    )

    # --------------------------------------------------------
    # 顯示台灣對應時間
    # --------------------------------------------------------

    with result_col:

        st.markdown(f"""
        <div>
            <div class="result-time">{taiwan_time_text}</div>
            <div class="result-detail">
                {taiwan_datetime.strftime("%Y-%m-%d")}
                ｜{format_day_difference(day_diff)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # 顯示時區備註
    # --------------------------------------------------------

    with note_col:

        st.markdown(f"""
        <div>
            <div class="timezone-note">
                {status} ({abbreviation})
            </div>
            <div class="timezone-offset">
                {utc_text}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
#                    頁尾說明
# ============================================================

st.markdown("""
<div class="footer-note">
    ※ 修改任一城市的時間，所有城市將同步使用相同的當地時間。
    <br>
    ※ 每個城市依照自身時區與當地日期進行換算，並自動處理夏令時間。
    <br>
    ※ 時區備註會依所選日期自動判斷夏令時間、標準時間及 UTC 偏移。
    <br>
    ※ 即時模式下，各城市顯示頁面最近一次更新時的時間。
</div>
""", unsafe_allow_html=True)
