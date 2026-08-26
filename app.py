import streamlit as st
import requests
import pandas as pd
from datetime import date
from collections import Counter
import plotly.graph_objects as go


# ============================================================
# CONFIGURATION
# ============================================================

APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwVnky82VMOehoM5AohJUzTqd7nS1T2_m--yq1yXfywczEV9XMsy1dLbbXAC191Ut7N"
    "/exec"
)


# ============================================================
# ADMIN PASSWORD
# ============================================================
# Streamlit Cloud:
# Settings -> Secrets
#
# ADMIN_PASSWORD = "YOUR_PASSWORD"
#
# Never put the real password directly in this file.

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
# MOBILE-FRIENDLY CSS
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
# GOOGLE APPS SCRIPT - GET
# ============================================================
# Cached for 10 seconds.
#
# This is the main performance improvement.
# It prevents every Streamlit rerun from calling Google Sheets.

@st.cache_data(
    ttl=10,
    show_spinner=False
)
def get_predictions():

    try:

        response = requests.get(
            APPS_SCRIPT_URL,
            timeout=10
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
            "error": "Invalid response from Google Apps Script."
        }


# ============================================================
# GOOGLE APPS SCRIPT - POST
# ============================================================
# POST is NOT cached because every submission must reach
# Google Apps Script immediately.

def submit_prediction(data):

    try:

        response = requests.post(
            APPS_SCRIPT_URL,
            json=data,
            timeout=15
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
            "error": "Invalid response from Google Apps Script."
        }


# ============================================================
# LOAD DATA
# ============================================================

result = get_predictions()

if result.get("success"):

    records = result.get(
        "data",
        []
    )

else:

    records = []


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
# TAB 1 - PREDICTION FORM
# ============================================================

with form_tab:

    st.title("🎊 Make Your Prediction")

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


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

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

                "guest_name":
                    clean_guest_name,

                "attending_yes_no":
                    attending,

                "gender_vote":
                    gender_value,

                "guessed_date":
                    guessed_date.strftime(
                        "%Y-%m-%d"
                    ),

                "baby_boy_name":
                    clean_boy_name,

                "baby_girl_name":
                    clean_girl_name,

                "message":
                    clean_message
            }


            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            with st.spinner(
                "Saving your prediction..."
            ):

                save_result = submit_prediction(
                    prediction
                )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if save_result.get(
                "success"
            ):

                # Clear cached Google Sheet data
                # so the new vote appears immediately.

                st.cache_data.clear()

                st.balloons()

                st.success(
                    "🎉 Your prediction has been submitted!"
                )

                st.info(
                    "Thank you for participating! 👶💕"
                )

                st.rerun()


            # ------------------------------------------------
            # DUPLICATE
            # ------------------------------------------------

            elif save_result.get(
                "duplicate"
            ):

                st.error(
                    "⚠️ This guest name has already submitted."
                )

                st.info(
                    "Each guest can submit only once."
                )


            # ------------------------------------------------
            # ERROR
            # ------------------------------------------------

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
# TAB 2 - GENDER PREDICTION
# ============================================================

with gender_tab:

    st.title(
        "🔮 Baby Gender Predictions"
    )

    st.caption(
        "What is everyone guessing? 💙💗"
    )


    # ========================================================
    # VOTES
    # ========================================================

    total_votes = len(
        records
    )


    gender_counter = Counter(
        str(
            row.get(
                "Gender Vote",
                ""
            )
        ).strip()
        for row in records
    )


    boy_votes = gender_counter.get(
        "Boy",
        0
    )


    girl_votes = gender_counter.get(
        "Girl",
        0
    )


    # ========================================================
    # PERCENTAGES
    # ========================================================

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

    col1, col2 = st.columns(
        2
    )


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

                x=0.5,

                font=dict(
                    size=13
                )
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
# TAB 3 - PRIVATE DASHBOARD
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

        st.caption(
            "Admin access only."
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


        st.metric(
            "👥 Total Guests",
            len(records)
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


        boy_names = []


        for row in records:

            boy_name = str(
                row.get(
                    "Baby Boy Name",
                    ""
                )
            ).strip()


            if boy_name:

                boy_names.append(
                    boy_name
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


        # ====================================================
        # GIRL NAMES
        # ====================================================

        st.subheader(
            "👧 Baby Girl Name Suggestions"
        )


        girl_names = []


        for row in records:

            girl_name = str(
                row.get(
                    "Baby Girl Name",
                    ""
                )
            ).strip()


            if girl_name:

                girl_names.append(
                    girl_name
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


        st.divider()


        # ====================================================
        # ALL RESPONSES
        # ====================================================

        st.subheader(
            "👨‍👩‍👧 Guest Responses"
        )


        admin_data = []


        for row in records:

            admin_data.append(
                {
                    "Timestamp":
                        row.get(
                            "Timestamp",
                            ""
                        ),

                    "Guest Name":
                        row.get(
                            "Guest Name",
                            ""
                        ),

                    "Attending":
                        row.get(
                            "Attending_yes_no",
                            ""
                        ),

                    "Gender":
                        row.get(
                            "Gender Vote",
                            ""
                        ),

                    "Date":
                        row.get(
                            "Date",
                            ""
                        ),

                    "Baby Boy Name":
                        row.get(
                            "Baby Boy Name",
                            ""
                        ),

                    "Baby Girl Name":
                        row.get(
                            "Baby Girl Name",
                            ""
                        ),

                    "Message":
                        row.get(
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


        st.divider()


        # ====================================================
        # REFRESH ADMIN
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