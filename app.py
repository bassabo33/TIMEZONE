import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ============================================================
# 基本設定
# ============================================================

st.set_page_config(
    page_title="全球時間比較器",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TIME_OPTIONS = ["即時", "10:00", "11:00", "14:00", "18:00", "20:00"]

CITY_OPTIONS = [
    ("紐西蘭威靈頓", "Pacific/Auckland"),
    ("澳洲雪梨", "Australia/Sydney"),
    ("西班牙札拉哥沙", "Europe/Madrid"),
    ("英國倫敦", "Europe/London"),
    ("美國紐約", "America/New_York"),
    ("巴西聖保羅", "America/Sao_Paulo"),
    ("墨西哥墨西哥市", "America/Mexico_City"),
    ("美國舊金山", "America/Los_Angeles"),
    ("美國夏威夷", "Pacific/Honolulu"),
]

DEFAULT_CITIES = [
    "澳洲雪梨",
    "西班牙札拉哥沙",
    "巴西聖保羅",
    "美國舊金山",
    "美國夏威夷",
]

TAIPEI_ZONE = ZoneInfo("Asia/Taipei")
CITY_ZONE_MAP = {name: ZoneInfo(zone) for name, zone in CITY_OPTIONS}
ROW_COUNT = 5
WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def format_date(dt):
    return f"{dt:%Y/%m/%d}（{WEEKDAYS[dt.weekday()]}）"


def format_offset(dt):
    offset = dt.utcoffset()
    if offset is None:
        return "UTC?"
    minutes = int(offset.total_seconds() // 60)
    sign = "+" if minutes >= 0 else "-"
    hours, mins = divmod(abs(minutes), 60)
    return f"UTC{sign}{hours:02d}:{mins:02d}"


def is_dst(dt):
    dst = dt.dst()
    return dst is not None and dst.total_seconds() != 0


def initialize_state():
    if "reference_utc" not in st.session_state:
        st.session_state.reference_utc = datetime.now(timezone.utc)
    if "live_mode" not in st.session_state:
        st.session_state.live_mode = True
    for i in range(ROW_COUNT):
        city_key = f"city_{i}"
        if city_key not in st.session_state:
            st.session_state[city_key] = DEFAULT_CITIES[i]


def on_time_changed(index):
    """任一列修改時間，就以該列城市時間更新共同 UTC 基準。"""
    city_name = st.session_state[f"city_{index}"]
    selected_time = st.session_state[f"time_{index}"]

    if selected_time == "即時":
        st.session_state.live_mode = True
        st.session_state.reference_utc = datetime.now(timezone.utc)
        return

    st.session_state.live_mode = False
    city_zone = CITY_ZONE_MAP[city_name]
    city_now = datetime.now(timezone.utc).astimezone(city_zone)
    hour, minute = map(int, selected_time.split(":"))
    target_city_dt = city_now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )
    st.session_state.reference_utc = target_city_dt.astimezone(timezone.utc)


# ============================================================
# 網頁介面
# ============================================================

st.markdown(
    """
    <style>
    .stApp { background-color: #F4F6F8; }
    .block-container { max-width: 1120px; padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #172B4D; font-size: 2rem !important; }
    .subtitle { color: #667085; font-size: 0.95rem; margin-top: -0.4rem; margin-bottom: 1.2rem; }
    .taiwan-card {
        background: #EAF2FF;
        border: 1px solid #C7D7F5;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 0.5rem 0 1.2rem 0;
    }
    .taiwan-caption { color: #174EA6; font-size: 0.9rem; font-weight: 700; }
    .taiwan-time { color: #102A56; font-family: Consolas, monospace; font-size: 1.35rem; font-weight: 700; }
    .column-heading { color: #667085; font-size: 0.85rem; font-weight: 700; padding: 0 0.3rem 0.35rem 0.3rem; }
    .result-time { color: #174EA6; font-family: Consolas, monospace; font-size: 1.1rem; font-weight: 700; padding-top: 0.25rem; }
    .detail-text { color: #667085; font-size: 0.76rem; margin-top: 0.15rem; }
    .help-text { color: #667085; font-size: 0.82rem; margin-top: 0.8rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF; border-color: #EAECF0; border-radius: 9px; }
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_state()


@st.fragment(run_every="1s")
def render_clock():
    # 即時模式下，共同基準時間每秒跟隨現在時間。
    if st.session_state.live_mode:
        st.session_state.reference_utc = datetime.now(timezone.utc)

    now_taiwan = datetime.now(TAIPEI_ZONE)
    taiwan_dt = st.session_state.reference_utc.astimezone(TAIPEI_ZONE)

    st.title("全球時間比較器")
    st.markdown(
        '<div class="subtitle">選擇城市及當地時間，右側自動換算成台灣時間</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'''<div class="taiwan-card">
            <div class="taiwan-caption">台灣目前時間</div>
            <div class="taiwan-time">{format_date(now_taiwan)}　{now_taiwan:%H:%M:%S}　({format_offset(now_taiwan)})</div>
        </div>''',
        unsafe_allow_html=True,
    )

    header_cols = st.columns([2.0, 1.25, 2.6], gap="medium")
    for col, label in zip(header_cols, ["城市", "當地時間", "台灣對應時間"]):
        with col:
            st.markdown(f'<div class="column-heading">{label}</div>', unsafe_allow_html=True)

    for index in range(ROW_COUNT):
        city_key = f"city_{index}"
        time_key = f"time_{index}"
        city_name = st.session_state[city_key]
        city_dt = st.session_state.reference_utc.astimezone(CITY_ZONE_MAP[city_name])
        local_time_text = city_dt.strftime("%H:%M")

        # 顯示換算後的當地時間；同時保留可供選擇的固定時間與「即時」。
        # 在建立 widget 前更新 session state，讓五列始終同步顯示。
        st.session_state[time_key] = local_time_text
        time_values = list(TIME_OPTIONS)
        if local_time_text not in time_values:
            time_values.append(local_time_text)

        with st.container(border=True):
            city_col, time_col, result_col = st.columns([2.0, 1.25, 2.6], gap="medium", vertical_alignment="center")

            with city_col:
                st.selectbox(
                    "城市",
                    options=[name for name, _ in CITY_OPTIONS],
                    key=city_key,
                    label_visibility="collapsed",
                )

            with time_col:
                st.selectbox(
                    "當地時間",
                    options=time_values,
                    key=time_key,
                    label_visibility="collapsed",
                    on_change=on_time_changed,
                    args=(index,),
                )

            # 城市下拉選單若剛被更改，使用最新城市重新計算顯示內容。
            city_name = st.session_state[city_key]
            city_dt = st.session_state.reference_utc.astimezone(CITY_ZONE_MAP[city_name])
            with result_col:
                st.markdown(
                    f'<div class="result-time">{taiwan_dt:%H:%M:%S}　({format_offset(taiwan_dt)})</div>',
                    unsafe_allow_html=True,
                )
                detail = (
                    f"{format_date(taiwan_dt)}　｜　{city_name}：{city_dt:%H:%M}"
                    f"（{format_offset(city_dt)}）"
                )
                if is_dst(city_dt):
                    detail += "　｜　當地夏令時間"
                st.markdown(f'<div class="detail-text">{detail}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="help-text">任一列修改時間，其他城市會同步換算；更換城市則保留共同基準時間。換算會自動考慮夏令時間及跨日。</div>',
        unsafe_allow_html=True,
    )


try:
    render_clock()
except ZoneInfoNotFoundError as exc:
    st.error("找不到時區資料。請確認 requirements.txt 已包含 tzdata。")
    st.exception(exc)
