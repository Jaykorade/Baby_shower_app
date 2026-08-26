import streamlit as st
import requests
import pandas as pd
from datetime import date
from collections import Counter
import plotly.graph_objects as go

# ============================================================
# CONFIGURATION
# ============================================================

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwVnky82VMOehoM5AohJUzTqd7nS1T2_m--yq1yXfywczEV9XMsy1dLbbXAC191Ut7N/exec"

# CHANGE THIS PASSWORD
ADMIN_PASSWORD = "Brookleen99#12"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Baby Shower Prediction",
    page_icon="👶",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 5% 5%,
                rgba(77, 166, 255, 0.12),
                transparent 25%
            ),
            radial-gradient(
                circle at 95% 5%,
                rgba(255, 105, 180, 0.12),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #fff8fb 0%,
                #f7fbff 100%
            );
    }

    .main-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        margin-top: 15px;
        color: #5b4b8a;
    }

    .subtitle {
        text-align: center;
        font-size: 1.15rem;
        color: #666;
        margin-bottom: 30px;
    }

    .section-title {
        text-align: center;
        color: #5b4b8a;
        font-weight: 700;
    }

    .boy-card {
        background: linear-gradient(
            135deg,
            #e8f5ff,
            #cce8ff
        );
        border: 2px solid #4da6ff;
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(77,166,255,0.18);
    }

    .girl-card {
        background: linear-gradient(
            135deg,
            #fff0f7,
            #ffd6e9
        );
        border: 2px solid #ff69b4;
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(255,105,180,0.18);
    }

    .boy-title {
        font-size: 22px;
        font-weight: 700;
        color: #1676d2;
    }

    .girl-title {
        font-size: 22px;
        font-weight: 700;
        color: #e83e91;
    }

    .boy-percent {
        font-size: 48px;
        font-weight: 800;
        color: #1676d2;
    }

    .girl-percent {
        font-size: 48px;
        font-weight: 800;
        color: #e83e91;
    }

    .vote-count {
        color: #555;
        font-size: 16px;
    }

    .success-box {
        padding: 25px;
        border-radius: 20px;
        background: #e9fff1;
        border: 1px solid #9be7b4;
        text-align: center;
    }

    .footer {
        text-align: center;
        color: #999;
        margin-top: 50px;
        padding-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GOOGLE APPS SCRIPT FUNCTIONS
# ============================================================

def submit_prediction(data):
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json=data,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": str(error)
        }

    except ValueError:
        return {
            "success": False,
            "error": "Google Apps Script returned an invalid response."
        }


def get_predictions():
    try:
        response = requests.get(
            APPS_SCRIPT_URL,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": str(error)
        }

    except ValueError:
        return {
            "success": False,
            "error": "Google Apps Script returned an invalid response."
        }


# ============================================================
# LOAD GOOGLE SHEET DATA
# ============================================================

result = get_predictions()

if result.get("success"):
    records = result.get("data", [])
else:
    records = []


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">👶 Baby Shower Prediction Game 🎀</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Make your prediction, guess the arrival date
        and suggest beautiful baby names 💕
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

form_tab, gender_tab, admin_tab = st.tabs(
    [
        "🎉 Make Your Prediction",
        "🔮 Gender Prediction",
        "🔐 Private"
    ]
)


# ============================================================
# TAB 1 — PREDICTION FORM
# ============================================================

with form_tab:

    st.markdown(
        '<h2 class="section-title">🎊 Make Your Prediction</h2>',
        unsafe_allow_html=True
    )

    st.write("")

    with st.form("baby_prediction_form"):

        col1, col2 = st.columns(2)

        # ----------------------------------------------------
        # GUEST INFORMATION
        # ----------------------------------------------------

        with col1:

            guest_name = st.text_input(
                "Guest Name *",
                placeholder="Enter your full name"
            )

            attending = st.radio(
                "Are you attending the Baby Shower? *",
                ["Yes", "No"],
                horizontal=True
            )

            gender_vote = st.radio(
                "What do you predict? *",
                ["Boy 👦", "Girl 👧"],
                horizontal=True
            )

        # ----------------------------------------------------
        # BABY INFORMATION
        # ----------------------------------------------------

        with col2:

            guessed_date = st.date_input(
                "When do you think baby will arrive? *",
                min_value=date.today()
            )

            baby_boy_name = st.text_input(
                "👦 Baby Boy Name Suggestion",
                placeholder="Suggest a boy name"
            )

            baby_girl_name = st.text_input(
                "👧 Baby Girl Name Suggestion",
                placeholder="Suggest a girl name"
            )

        message = st.text_area(
            "💌 Message for the Parents",
            placeholder="Write your wishes for the parents and baby..."
        )

        submitted = st.form_submit_button(
            "🎊 Submit My Prediction 🎊",
            use_container_width=True
        )

    # --------------------------------------------------------
    # PROCESS SUBMISSION
    # --------------------------------------------------------

    if submitted:

        clean_guest_name = guest_name.strip()

        clean_boy_name = baby_boy_name.strip()

        clean_girl_name = baby_girl_name.strip()

        clean_message = message.strip()

        if not clean_guest_name:

            st.error(
                "Please enter your Guest Name."
            )

        elif guessed_date < date.today():

            st.error(
                "Please select a valid arrival date."
            )

        else:

            if gender_vote.startswith("Boy"):
                gender_value = "Boy"
            else:
                gender_value = "Girl"

            prediction = {
                "guest_name": clean_guest_name,
                "attending_yes_no": attending,
                "gender_vote": gender_value,
                "guessed_date": guessed_date.strftime(
                    "%Y-%m-%d"
                ),
                "baby_boy_name": clean_boy_name,
                "baby_girl_name": clean_girl_name,
                "message": clean_message
            }

            with st.spinner(
                "Saving your prediction..."
            ):

                save_result = submit_prediction(
                    prediction
                )

            if save_result.get("success"):

                st.balloons()

                st.markdown(
                    """
                    <div class="success-box">

                        <h2>🎉 Prediction Submitted! 🎉</h2>

                        <p>
                        Thank you for participating
                        in our Baby Shower game! 👶💕
                        </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.success(
                    "Your prediction has been saved successfully."
                )

                st.rerun()

            elif save_result.get("duplicate"):

                st.error(
                    "⚠️ This guest name has already submitted."
                )

                st.info(
                    "Each guest can submit only once."
                )

            else:

                st.error(
                    "❌ Unable to save your prediction."
                )

                st.code(
                    str(
                        save_result.get(
                            "error",
                            "Unknown error"
                        )
                    )
                )

    # ============================================================
# TAB 2 — GENDER PREDICTION
# ============================================================

with gender_tab:

    st.title("🔮 Baby Gender Predictions")

    st.write(
        "What is everyone guessing? 💙💗"
    )

    # --------------------------------------------------------
    # CALCULATE VOTES
    # --------------------------------------------------------

    total_votes = len(records)

    gender_counter = Counter(
        str(row.get("Gender Vote", "")).strip()
        for row in records
    )

    boy_votes = gender_counter.get("Boy", 0)
    girl_votes = gender_counter.get("Girl", 0)

    if total_votes > 0:

        boy_percentage = (
            boy_votes / total_votes
        ) * 100

        girl_percentage = (
            girl_votes / total_votes
        ) * 100

    else:

        boy_percentage = 0
        girl_percentage = 0

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "💙 Baby Boy",
            f"{boy_percentage:.1f}%",
            f"{boy_votes} votes"
        )

    with col2:

        st.metric(
            "💗 Baby Girl",
            f"{girl_percentage:.1f}%",
            f"{girl_votes} votes"
        )

    with col3:

        st.metric(
            "🍼 Total Votes",
            total_votes
        )

    st.write("")

    # --------------------------------------------------------
    # VISUAL PERCENTAGE BARS
    # --------------------------------------------------------

    st.subheader("💙💗 Prediction Split")

    st.write(
        f"💙 Baby Boy — {boy_percentage:.1f}%"
    )

    st.progress(
        int(round(boy_percentage))
    )

    st.write(
        f"💗 Baby Girl — {girl_percentage:.1f}%"
    )

    st.progress(
        int(round(girl_percentage))
    )

    st.write("")

    # --------------------------------------------------------
    # PLOTLY DONUT CHART
    # --------------------------------------------------------

    if total_votes > 0:

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Baby Boy 👦",
                        "Baby Girl 👧"
                    ],
                    values=[
                        boy_votes,
                        girl_votes
                    ],
                    hole=0.60,
                    marker=dict(
                        colors=[
                            "#4DA6FF",
                            "#FF69B4"
                        ],
                        line=dict(
                            color="white",
                            width=5
                        )
                    ),
                    textinfo="percent",
                    textposition="inside",
                    textfont=dict(
                        size=22,
                        color="white"
                    ),
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Votes: %{value}<br>"
                        "Percentage: %{percent}"
                        "<extra></extra>"
                    )
                )
            ]
        )

        fig.update_layout(
            title={
                "text": "💙 Boy vs 💗 Girl",
                "x": 0.5
            },
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.10,
                xanchor="center",
                x=0.5
            ),
            margin=dict(
                l=10,
                r=10,
                t=70,
                b=70
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    else:

        st.info(
            "👶 Waiting for the first prediction..."
        )

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    if st.button(
        "🔄 Refresh Predictions",
        key="refresh_gender"
    ):

        st.rerun()


# ============================================================
# TAB 3 — PRIVATE ADMIN
# ============================================================

with admin_tab:

    if not st.session_state.get(
        "admin_authenticated",
        False
    ):

        st.markdown(
            """
            <div style="
                text-align:center;
                margin-top:80px;
                color:#999;
            ">
                🔐 Private Dashboard
            </div>
            """,
            unsafe_allow_html=True
        )

        password = st.text_input(
            "Admin Password",
            type="password",
            key="admin_password"
        )

        if st.button(
            "Unlock",
            key="admin_unlock"
        ):

            if password == ADMIN_PASSWORD:

                st.session_state[
                    "admin_authenticated"
                ] = True

                st.rerun()

            else:

                st.error(
                    "Incorrect password."
                )

    else:

        st.markdown(
            '<h2 class="section-title">🔐 Private Dashboard</h2>',
            unsafe_allow_html=True
        )

        st.success(
            "Admin access enabled."
        )

        # ----------------------------------------------------
        # ATTENDANCE
        # ----------------------------------------------------

        attendance_counter = Counter(
            str(
                row.get(
                    "Attending_yes_no",
                    ""
                )
            ).strip()
            for row in records
        )

        attending_yes = attendance_counter.get(
            "Yes",
            0
        )

        attending_no = attendance_counter.get(
            "No",
            0
        )

        admin_col1, admin_col2, admin_col3 = st.columns(3)

        with admin_col1:

            st.metric(
                "👥 Total Guests",
                len(records)
            )

        with admin_col2:

            st.metric(
                "✅ Attending",
                attending_yes
            )

        with admin_col3:

            st.metric(
                "❌ Not Attending",
                attending_no
            )

        # ----------------------------------------------------
        # NAME SUGGESTIONS
        # ----------------------------------------------------

        st.markdown(
            "### 👶 Baby Name Suggestions"
        )

        boy_names = []
        girl_names = []

        for row in records:

            boy_name = str(
                row.get(
                    "Baby Boy Name",
                    ""
                )
            ).strip()

            girl_name = str(
                row.get(
                    "Baby Girl Name",
                    ""
                )
            ).strip()

            if boy_name:
                boy_names.append(
                    boy_name
                )

            if girl_name:
                girl_names.append(
                    girl_name
                )

        name_col1, name_col2 = st.columns(2)

        with name_col1:

            st.markdown(
                "#### 👦 Baby Boy Names"
            )

            if boy_names:

                for name in boy_names:

                    st.write(
                        f"• {name}"
                    )

            else:

                st.info(
                    "No boy name suggestions yet."
                )

        with name_col2:

            st.markdown(
                "#### 👧 Baby Girl Names"
            )

            if girl_names:

                for name in girl_names:

                    st.write(
                        f"• {name}"
                    )

            else:

                st.info(
                    "No girl name suggestions yet."
                )

        # ----------------------------------------------------
        # ALL GUEST RESPONSES
        # ----------------------------------------------------

        st.markdown(
            "### 👨‍👩‍👧 Guest Responses"
        )

        admin_data = []

        for row in records:

            admin_data.append(
                {
                    "Timestamp": row.get(
                        "Timestamp",
                        ""
                    ),
                    "Guest Name": row.get(
                        "Guest Name",
                        ""
                    ),
                    "Attending": row.get(
                        "Attending_yes_no",
                        ""
                    ),
                    "Gender": row.get(
                        "Gender Vote",
                        ""
                    ),
                    "Date": row.get(
                        "Date",
                        ""
                    ),
                    "Baby Boy Name": row.get(
                        "Baby Boy Name",
                        ""
                    ),
                    "Baby Girl Name": row.get(
                        "Baby Girl Name",
                        ""
                    ),
                    "Message": row.get(
                        "Message",
                        ""
                    )
                }
            )

        if admin_data:

            admin_df = pd.DataFrame(
                admin_data
            )

            st.dataframe(
                admin_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No guest responses yet."
            )

        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        if st.button(
            "🔒 Lock Private Dashboard",
            key="admin_logout"
        ):

            st.session_state[
                "admin_authenticated"
            ] = False

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        Made with ❤️ for the Baby Shower

        <br><br>

        👶 💙 🎀 💗 🍼

    </div>
    """,
    unsafe_allow_html=True
)