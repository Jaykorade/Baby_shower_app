import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from collections import Counter
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = Path("baby_shower.db")


# ============================================================
# ADMIN PASSWORD
# ============================================================

try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except Exception:
    ADMIN_PASSWORD = ""


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Baby Shower Prediction",
    page_icon="👶",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# MOBILE FRIENDLY CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #fff8fb 0%,
            #f7fbff 100%
        );
    }

    .block-container {
        max-width: 900px;
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }

    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: #5b4b8a;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        color: #999;
        margin-top: 40px;
        padding-bottom: 15px;
    }

    @media (max-width: 600px) {

        .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
            padding-top: 0.5rem;
        }

        .main-title {
            font-size: 2rem;
        }

        .subtitle {
            font-size: 0.9rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

            guest_name TEXT NOT NULL UNIQUE,

            attending_yes_no TEXT NOT NULL,

            gender_vote TEXT NOT NULL,

            guessed_date TEXT NOT NULL,

            baby_boy_name TEXT,

            baby_girl_name TEXT,

            message TEXT

        )
        """
    )

    connection.commit()

    connection.close()


initialize_database()


# ============================================================
# GET ALL PREDICTIONS
# ============================================================

@st.cache_data(
    ttl=5,
    show_spinner=False
)
def get_predictions():

    connection = get_connection()

    dataframe = pd.read_sql_query(
        """
        SELECT
            id,
            timestamp AS Timestamp,
            guest_name AS "Guest Name",
            attending_yes_no AS Attending,
            gender_vote AS "Gender Vote",
            guessed_date AS Date,
            baby_boy_name AS "Baby Boy Name",
            baby_girl_name AS "Baby Girl Name",
            message AS Message
        FROM predictions
        ORDER BY id ASC
        """,
        connection
    )

    connection.close()

    return dataframe


# ============================================================
# INSERT PREDICTION
# ============================================================

def submit_prediction(
    guest_name,
    attending,
    gender,
    guessed_date,
    boy_name,
    girl_name,
    message
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO predictions (
                guest_name,
                attending_yes_no,
                gender_vote,
                guessed_date,
                baby_boy_name,
                baby_girl_name,
                message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                guest_name,
                attending,
                gender,
                guessed_date,
                boy_name,
                girl_name,
                message
            )
        )

        connection.commit()

        connection.close()

        return {
            "success": True
        }

    except sqlite3.IntegrityError:

        connection.close()

        return {
            "success": False,
            "duplicate": True
        }

    except Exception as error:

        connection.close()

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# LOAD DATA
# ============================================================

df = get_predictions()

records = df.to_dict(
    orient="records"
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">👶 Baby Shower 🎀</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Make your prediction and join the fun! 💕</div>',
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

form_tab, gender_tab, admin_tab = st.tabs(
    [
        "🎉 Predict",
        "🔮 Gender",
        "🔐 Private"
    ]
)


# ============================================================
# TAB 1 — PREDICTION FORM
# ============================================================

with form_tab:

    st.title(
        "🎊 Make Your Prediction"
    )

    st.write(
        "Fill in your prediction below."
    )

    with st.form(
        "baby_prediction_form"
    ):

        guest_name = st.text_input(
            "Guest Name *",
            placeholder="Enter your full name"
        )

        attending = st.radio(
            "Are you attending the Baby Shower? *",
            [
                "Yes",
                "No"
            ],
            horizontal=True
        )

        gender_vote = st.radio(
            "What do you predict? *",
            [
                "Boy 👦",
                "Girl 👧"
            ],
            horizontal=True
        )

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
            "🎊 Submit My Prediction",
            use_container_width=True
        )


    # ========================================================
    # PROCESS SUBMISSION
    # ========================================================

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


            result = submit_prediction(

                guest_name=clean_guest_name,

                attending=attending,

                gender=gender_value,

                guessed_date=guessed_date.strftime(
                    "%Y-%m-%d"
                ),

                boy_name=clean_boy_name,

                girl_name=clean_girl_name,

                message=clean_message
            )


            if result.get("success"):

                st.cache_data.clear()

                st.balloons()

                st.success(
                    "🎉 Your prediction has been submitted!"
                )

                st.info(
                    "Thank you for participating! 👶💕"
                )

                st.rerun()


            elif result.get("duplicate"):

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
                        result.get(
                            "error",
                            "Unknown error"
                        )
                    )
                )


# ============================================================
# TAB 2 — GENDER PREDICTION
# ============================================================

with gender_tab:

    st.title(
        "🔮 Baby Gender Predictions"
    )

    st.caption(
        "What is everyone guessing? 💙💗"
    )


    # ========================================================
    # CALCULATE VOTES
    # ========================================================

    total_votes = len(df)


    if total_votes > 0:

        boy_votes = int(
            (
                df["Gender Vote"] == "Boy"
            ).sum()
        )

        girl_votes = int(
            (
                df["Gender Vote"] == "Girl"
            ).sum()
        )

    else:

        boy_votes = 0

        girl_votes = 0


    if total_votes > 0:

        boy_percentage = (
            boy_votes /
            total_votes
        ) * 100

        girl_percentage = (
            girl_votes /
            total_votes
        ) * 100

    else:

        boy_percentage = 0

        girl_percentage = 0


    # ========================================================
    # SUMMARY
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            label="💙 Baby Boy",
            value=f"{boy_percentage:.1f}%",
            delta=f"{boy_votes} votes"
        )


    with col2:

        st.metric(
            label="💗 Baby Girl",
            value=f"{girl_percentage:.1f}%",
            delta=f"{girl_votes} votes"
        )


    st.metric(
        label="🍼 Total Predictions",
        value=total_votes
    )


    st.divider()


    # ========================================================
    # PROGRESS BARS
    # ========================================================

    st.subheader(
        "💙💗 Prediction Split"
    )


    st.write(
        f"💙 Baby Boy — {boy_percentage:.1f}%"
    )

    st.progress(
        int(
            round(
                boy_percentage
            )
        )
    )


    st.write(
        f"💗 Baby Girl — {girl_percentage:.1f}%"
    )

    st.progress(
        int(
            round(
                girl_percentage
            )
        )
    )


    st.divider()


    # ========================================================
    # DONUT CHART
    # ========================================================

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
                            width=4
                        )
                    ),

                    textinfo="percent",

                    textposition="inside",

                    textfont=dict(
                        size=18,
                        color="white"
                    ),

                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Votes: %{value}<br>"
                        "Share: %{percent}"
                        "<extra></extra>"
                    )
                )
            ]
        )


        fig.update_layout(

            height=400,

            autosize=True,

            showlegend=True,

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=-0.15,

                xanchor="center",

                x=0.5
            ),

            margin=dict(
                l=5,
                r=5,
                t=20,
                b=70
            ),

            paper_bgcolor=(
                "rgba(0,0,0,0)"
            ),

            plot_bgcolor=(
                "rgba(0,0,0,0)"
            )
        )


        st.plotly_chart(

            fig,

            use_container_width=True,

            config={
                "displayModeBar": False,
                "responsive": True
            }
        )


    else:

        st.info(
            "👶 Waiting for the first prediction..."
        )


    # ========================================================
    # REFRESH
    # ========================================================

    if st.button(
        "🔄 Refresh Predictions",
        key="refresh_gender",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()


# ============================================================
# TAB 3 — PRIVATE DASHBOARD
# ============================================================

with admin_tab:

    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.get(
        "admin_authenticated",
        False
    ):

        st.title(
            "🔐 Private Dashboard"
        )

        password = st.text_input(
            "Admin Password",
            type="password",
            key="admin_password"
        )


        if st.button(
            "🔓 Unlock Dashboard",
            key="admin_unlock",
            use_container_width=True
        ):

            if (
                ADMIN_PASSWORD
                and password == ADMIN_PASSWORD
            ):

                st.session_state[
                    "admin_authenticated"
                ] = True

                st.rerun()

            else:

                st.error(
                    "Incorrect password."
                )


    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    else:

        st.title(
            "🔐 Private Dashboard"
        )

        st.success(
            "Admin access enabled."
        )


        # ====================================================
        # ATTENDANCE
        # ====================================================

        st.subheader(
            "👥 Attendance"
        )


        attending_yes = int(
            (
                df["Attending"] == "Yes"
            ).sum()
        )


        attending_no = int(
            (
                df["Attending"] == "No"
            ).sum()
        )


        st.metric(
            "👥 Total Guests",
            len(df)
        )

        st.metric(
            "✅ Attending",
            attending_yes
        )

        st.metric(
            "❌ Not Attending",
            attending_no
        )


        st.divider()


        # ====================================================
        # BOY NAMES
        # ====================================================

        st.subheader(
            "👦 Baby Boy Name Suggestions"
        )


        boy_names = df[
            "Baby Boy Name"
        ].dropna()


        boy_names = [
            str(name).strip()
            for name in boy_names
            if str(name).strip()
        ]


        if boy_names:

            for name in boy_names:

                st.write(
                    f"• {name}"
                )

        else:

            st.info(
                "No boy name suggestions yet."
            )


        # ====================================================
        # GIRL NAMES
        # ====================================================

        st.subheader(
            "👧 Baby Girl Name Suggestions"
        )


        girl_names = df[
            "Baby Girl Name"
        ].dropna()


        girl_names = [
            str(name).strip()
            for name in girl_names
            if str(name).strip()
        ]


        if girl_names:

            for name in girl_names:

                st.write(
                    f"• {name}"
                )

        else:

            st.info(
                "No girl name suggestions yet."
            )


        st.divider()


        # ====================================================
        # ALL RESPONSES
        # ====================================================

        st.subheader(
            "👨‍👩‍👧 Guest Responses"
        )


        if not df.empty:

            display_df = df[
                [
                    "Timestamp",
                    "Guest Name",
                    "Attending",
                    "Gender Vote",
                    "Date",
                    "Baby Boy Name",
                    "Baby Girl Name",
                    "Message"
                ]
            ]


            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No guest responses yet."
            )


        st.divider()


        # ====================================================
        # REFRESH
        # ====================================================

        if st.button(
            "🔄 Refresh Dashboard",
            key="refresh_admin",
            use_container_width=True
        ):

            st.cache_data.clear()

            st.rerun()


        # ====================================================
        # LOGOUT
        # ====================================================

        if st.button(
            "🔒 Lock Private Dashboard",
            key="admin_logout",
            use_container_width=True
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
        <br>
        👶 💙 🎀 💗 🍼
    </div>
    """,
    unsafe_allow_html=True
)