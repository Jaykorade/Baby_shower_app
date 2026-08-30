import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from pathlib import Path
from io import BytesIO
import plotly.graph_objects as go


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
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "form_reset": 0,
    "submission_confirmation": None,
    "admin_authenticated": False,
    "confirm_delete_selected": False,
    "confirm_reset_app": False,
    "delete_selector_version": 0,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
        padding-top: 2.5rem !important;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }

    .main-title {
        text-align: center;
        font-size: 2.25rem;
        font-weight: 800;
        color: #5b4b8a;
        margin-bottom: 4px;
        line-height: 1.2;
    }

    .subtitle {
        text-align: center;
        color: #666666;
        font-size: 0.95rem;
        margin-bottom: 18px;
    }

    .small-heading {
        font-size: 1.3rem;
        font-weight: 700;
        color: #5b4b8a;
        margin-top: 0.2rem;
        margin-bottom: 0.4rem;
    }

    .prediction-label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .prediction-bar-container {
        width: 100%;
        height: 14px;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 18px;
    }

    .prediction-bar {
        height: 100%;
        border-radius: 20px;
        transition: width 0.5s ease;
    }

    .boy-bar-background {
        background: #e5f2ff;
    }

    .boy-bar {
        background: #4DA6FF;
    }

    .girl-bar-background {
        background: #ffe8f2;
    }

    .girl-bar {
        background: #FF69B4;
    }

    .boy-label {
        color: #1676d2;
    }

    .girl-label {
        color: #e7549b;
    }

    .success-card {
        padding: 14px;
        border-radius: 12px;
        background: #f4fff7;
        border: 1px solid #b7e8c3;
        margin-top: 10px;
    }

    .danger-card {
        padding: 14px;
        border-radius: 12px;
        background: #fff5f5;
        border: 1px solid #ffcaca;
    }

    .footer {
        text-align: center;
        color: #999999;
        margin-top: 40px;
        padding-bottom: 15px;
        font-size: 0.85rem;
    }

    @media (max-width: 600px) {

        .block-container {
            padding-top: 2.3rem !important;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        .main-title {
            font-size: 1.85rem;
        }

        .subtitle {
            font-size: 0.85rem;
        }

        .small-heading {
            font-size: 1.15rem;
        }

        .prediction-label {
            font-size: 0.88rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


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
# READ DATA
# ============================================================

@st.cache_data(
    ttl=3,
    show_spinner=False
)
def get_predictions():

    connection = get_connection()

    try:

        df = pd.read_sql_query(
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

    finally:

        connection.close()

    return df


# ============================================================
# SUBMIT PREDICTION
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

    try:

        cursor = connection.cursor()

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

        return {
            "success": True
        }

    except sqlite3.IntegrityError:

        return {
            "success": False,
            "duplicate": True
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }

    finally:

        connection.close()


# ============================================================
# DELETE SELECTED
# ============================================================

def delete_selected_rows(selected_ids):

    if not selected_ids:
        return 0

    connection = get_connection()

    try:

        cursor = connection.cursor()

        placeholders = ",".join(
            ["?"] * len(selected_ids)
        )

        cursor.execute(
            f"""
            DELETE FROM predictions
            WHERE id IN ({placeholders})
            """,
            selected_ids
        )

        deleted_count = cursor.rowcount

        connection.commit()

        return deleted_count

    finally:

        connection.close()


# ============================================================
# RESET ENTIRE APP
# ============================================================

def reset_entire_database():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM predictions"
        )

        # Reset SQLite ID counter
        try:

            cursor.execute(
                """
                DELETE FROM sqlite_sequence
                WHERE name = 'predictions'
                """
            )

        except sqlite3.OperationalError:
            pass

        connection.commit()

    finally:

        connection.close()


# ============================================================
# EXCEL EXPORT
# ============================================================

def create_excel_file(dataframe):

    output = BytesIO()

    columns = [
        "Timestamp",
        "Guest Name",
        "Attending",
        "Gender Vote",
        "Date",
        "Baby Boy Name",
        "Baby Girl Name",
        "Message"
    ]

    export_df = dataframe[
        columns
    ].copy()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        export_df.to_excel(
            writer,
            index=False,
            sheet_name="Baby Shower"
        )

    output.seek(0)

    return output.getvalue()


# ============================================================
# LOAD DATA
# ============================================================

df = get_predictions()



# ============================================================
# LANGUAGE SELECTION
# ============================================================

LANGUAGE_OPTIONS = {
    "English": "English",
    "मराठी": "मराठी"
}

selected_language = st.radio(
    "🌐 Language / भाषा",
    list(LANGUAGE_OPTIONS.keys()),
    horizontal=True,
    key="language_selector"
)

IS_MARATHI = selected_language == "मराठी"

def tr(english, marathi):
    """Return UI text in the selected language."""
    return marathi if IS_MARATHI else english


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f'<div class="main-title">👶 {tr("Baby Shower 🎀", "डोहाळे जेवण 🎀")}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="subtitle">
        {tr("Make your prediction and join the fun! 💕",
            "तुमचा अंदाज नोंदवा आणि या आनंदात सहभागी व्हा! 💕")}
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

form_tab, gender_tab, admin_tab = st.tabs(
    [
        tr("🎉 Predict", "🎉 अंदाज"),
        tr("🔮 Gender", "🔮 लिंग अंदाज"),
        tr("🔐 Private", "🔐 खासगी")
    ]
)


# ============================================================
# TAB 1 — PREDICTION FORM
# ============================================================

with form_tab:

    st.markdown(
        f"""
        <div class="small-heading">
            🎊 {tr("Make Your Prediction", "तुमचा अंदाज नोंदवा")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        tr("One submission per guest.", "प्रत्येक पाहुण्याला एकदाच अंदाज नोंदवता येईल.")
    )


    # ========================================================
    # DYNAMIC FORM KEY
    # ========================================================

    form_key = (
        "baby_prediction_form_"
        + str(st.session_state.form_reset)
    )


    with st.form(form_key):

        guest_name = st.text_input(
            tr("Guest Name *", "पाहुण्याचे नाव *"),
            placeholder=tr("Enter your full name", "तुमचे पूर्ण नाव लिहा")
        )

        attending = st.radio(
            tr("Are you attending the Baby Shower? *", "तुम्ही डोहाळे जेवणाला उपस्थित राहणार आहात का? *"),
            [
                tr("Yes", "होय"),
                tr("No", "नाही")
            ],
            horizontal=True
        )

        gender_vote = st.radio(
            tr("What do you predict? *", "तुमचा अंदाज काय आहे? *"),
            [
                tr("Boy 👦", "मुलगा 👦"),
                tr("Girl 👧", "मुलगी 👧")
            ],
            horizontal=True
        )

        guessed_date = st.date_input(
            tr("When do you think baby will arrive? *", "बाळाचा जन्म कधी होईल असे तुम्हाला वाटते? *"),
            min_value=date.today()
        )

        baby_boy_name = st.text_input(
            tr("👦 Baby Boy Name Suggestion", "👦 मुलासाठी नावाची सूचना"),
            placeholder=tr("Suggest a baby boy name", "मुलासाठी नाव सुचवा")
        )

        baby_girl_name = st.text_input(
            tr("👧 Baby Girl Name Suggestion", "👧 मुलीसाठी नावाची सूचना"),
            placeholder=tr("Suggest a baby girl name", "मुलीसाठी नाव सुचवा")
        )

        message = st.text_area(
            tr("💌 Message for the Parents", "💌 आई-बाबांसाठी संदेश"),
            placeholder=tr("Write your wishes...", "तुमच्या शुभेच्छा लिहा...")
        )

        submitted = st.form_submit_button(
            tr("🎊 Submit My Prediction", "🎊 माझा अंदाज सबमिट करा"),
            use_container_width=True
        )


    # ========================================================
    # SUBMISSION
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
                tr("Please enter your Guest Name.", "कृपया तुमचे पाहुण्याचे नाव लिहा.")
            )

        else:

            gender_value = (
                "Boy"
                if gender_vote.startswith(("Boy", "मुलगा"))
                else "Girl"
            )


            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            result = submit_prediction(

                guest_name=clean_guest_name,

                attending=("Yes" if attending in ("Yes", "होय") else "No"),

                gender=gender_value,

                guessed_date=guessed_date.strftime(
                    "%Y-%m-%d"
                ),

                boy_name=clean_boy_name,

                girl_name=clean_girl_name,

                message=clean_message
            )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if result["success"]:

                st.session_state[
                    "submission_confirmation"
                ] = {

                    "guest_name":
                        clean_guest_name,

                    "attending":
                        attending,

                    "gender":
                        gender_value,

                    "guessed_date":
                        guessed_date.strftime(
                            "%d %B %Y"
                        ),

                    "boy_name":
                        clean_boy_name,

                    "girl_name":
                        clean_girl_name,

                    "message":
                        clean_message
                }


                # Clear database cache
                st.cache_data.clear()


                # IMPORTANT:
                # New form key creates completely
                # empty widgets after rerun.

                st.session_state.form_reset += 1


                st.balloons()

                st.rerun()


            # ------------------------------------------------
            # DUPLICATE
            # ------------------------------------------------

            elif result.get("duplicate"):

                st.error(
                    tr("⚠️ This guest name has already submitted.",
                       "⚠️ या पाहुण्याने आधीच अंदाज नोंदवला आहे.")
                )

                st.info(
                    tr("Each guest can submit only once.",
                       "प्रत्येक पाहुण्याला फक्त एकदाच अंदाज नोंदवता येईल.")
                )


            # ------------------------------------------------
            # OTHER ERROR
            # ------------------------------------------------

            else:

                st.error(
                    tr("❌ Unable to save your prediction.",
                       "❌ तुमचा अंदाज जतन करता आला नाही.")
                )

                if result.get("error"):

                    st.caption(
                        str(result["error"])
                    )


    # ========================================================
    # CONFIRMATION
    # ========================================================

    submission = st.session_state.get(
        "submission_confirmation"
    )


    if submission:

        st.divider()

        st.markdown(
            """
            <div class="small-heading">
                💝 {tr("Your Submitted Details", "तुम्ही नोंदवलेली माहिती")}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.success(
            tr("🎉 Your prediction has been submitted successfully!",
               "🎉 तुमचा अंदाज यशस्वीपणे नोंदवला गेला!")
        )

        st.info(
            f"👤 **{tr('Guest Name', 'पाहुण्याचे नाव')}:** "
            f"{submission['guest_name']}"
        )

        st.write(
            f"✅ **{tr('Attending', 'उपस्थिती')}:** "
            f"{tr('Yes', 'होय') if submission['attending'] == 'Yes' else tr('No', 'नाही')}"
        )


        if submission["gender"] == "Boy":

            st.write(
                f"🔮 **{tr('Gender Prediction', 'लिंगाचा अंदाज')}:** 💙 {tr('Boy', 'मुलगा')} 👦"
            )

        else:

            st.write(
                f"🔮 **{tr('Gender Prediction', 'लिंगाचा अंदाज')}:** 💗 {tr('Girl', 'मुलगी')} 👧"
            )


        st.write(
            f"📅 **{tr('Predicted Arrival Date', 'अंदाजित जन्मतारीख')}:** "
            f"{submission['guessed_date']}"
        )


        if submission["boy_name"]:

            st.write(
                f"👦 **{tr('Baby Boy Name', 'मुलाचे नाव')}:** "
                f"{submission['boy_name']}"
            )


        if submission["girl_name"]:

            st.write(
                f"👧 **{tr('Baby Girl Name', 'मुलीचे नाव')}:** "
                f"{submission['girl_name']}"
            )


        if submission["message"]:

            st.write(
                f"💌 **{tr('Message', 'संदेश')}:**"
            )

            st.info(
                submission["message"]
            )


        st.success(
            tr("💕 Thank you for being part of our Baby Shower!",
               "💕 आमच्या डोहाळे जेवणाचा भाग झाल्याबद्दल धन्यवाद!")
        )


# ============================================================
# TAB 2 — PUBLIC GENDER PREDICTION
# ============================================================

with gender_tab:

    st.markdown(
        """
        <div class="small-heading">
            🔮 Baby Gender Predictions
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "What is everyone guessing? 💙💗"
    )


    # ========================================================
    # VOTE COUNTS
    # ========================================================

    total_votes = len(df)


    if total_votes:

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


    # ========================================================
    # PERCENTAGES
    # ========================================================

    if total_votes:

        boy_percentage = (
            boy_votes / total_votes
        ) * 100

        girl_percentage = (
            girl_votes / total_votes
        ) * 100

    else:

        boy_percentage = 0
        girl_percentage = 0


    # ========================================================
    # METRICS
    # ========================================================

    metric1, metric2 = st.columns(2)


    with metric1:

        st.metric(
            "💙 Baby Boy",
            f"{boy_percentage:.1f}%",
            f"{boy_votes} votes"
        )


    with metric2:

        st.metric(
            "💗 Baby Girl",
            f"{girl_percentage:.1f}%",
            f"{girl_votes} votes"
        )


    st.metric(
        "🍼 Total Predictions",
        total_votes
    )


    st.divider()


    # ========================================================
    # BOY PROGRESS
    # ========================================================

    st.markdown(
        f"""
        <div class="prediction-label">

            <span class="boy-label">
                💙 Baby Boy
            </span>

            <span>
                {boy_percentage:.1f}%
            </span>

        </div>

        <div class="prediction-bar-container
                    boy-bar-background">

            <div
                class="prediction-bar boy-bar"
                style="width: {boy_percentage:.1f}%;">
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # GIRL PROGRESS
    # ========================================================

    st.markdown(
        f"""
        <div class="prediction-label">

            <span class="girl-label">
                💗 Baby Girl
            </span>

            <span>
                {girl_percentage:.1f}%
            </span>

        </div>

        <div class="prediction-bar-container
                    girl-bar-background">

            <div
                class="prediction-bar girl-bar"
                style="width: {girl_percentage:.1f}%;">
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # DONUT CHART
    # ========================================================

    if total_votes:

        st.divider()

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

                    hole=0.62,

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

            height=390,

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
                t=15,
                b=70
            ),

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)"
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
        key="public_refresh",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()


# ============================================================
# TAB 3 — PRIVATE ADMIN
# ============================================================

with admin_tab:


    # ========================================================
    # ADMIN LOGIN
    # ========================================================

    if not st.session_state.admin_authenticated:

        st.markdown(
            """
            <div class="small-heading">
                🔐 Private Dashboard
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Admin access only."
        )


        password = st.text_input(
            "Admin Password",
            type="password",
            key="admin_password_input"
        )


        if st.button(
            "🔓 Unlock Dashboard",
            key="admin_login_button",
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

        st.markdown(
            """
            <div class="small-heading">
                🔐 Private Dashboard
            </div>
            """,
            unsafe_allow_html=True
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


        total_guests = len(df)


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


        c1, c2, c3 = st.columns(3)


        with c1:

            st.metric(
                "👥 Total",
                total_guests
            )


        with c2:

            st.metric(
                "✅ Attending",
                attending_yes
            )


        with c3:

            st.metric(
                "❌ Not Attending",
                attending_no
            )


        # ====================================================
        # NAME SUGGESTIONS
        # ====================================================

        st.divider()

        st.subheader(
            "👶 Name Suggestions"
        )


        name_col1, name_col2 = st.columns(2)


        with name_col1:

            st.markdown(
                "### 👦 Baby Boy"
            )


            boy_names = []

            if not df.empty:

                for value in df[
                    "Baby Boy Name"
                ].dropna():

                    value = str(value).strip()

                    if value:

                        boy_names.append(value)


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
                "### 👧 Baby Girl"
            )


            girl_names = []

            if not df.empty:

                for value in df[
                    "Baby Girl Name"
                ].dropna():

                    value = str(value).strip()

                    if value:

                        girl_names.append(value)


            if girl_names:

                for name in girl_names:

                    st.write(
                        f"• {name}"
                    )

            else:

                st.info(
                    "No girl name suggestions yet."
                )


        # ====================================================
        # GUEST RESPONSES
        # ====================================================

        st.divider()

        st.subheader(
            "👨‍👩‍👧 Guest Responses"
        )


        if not df.empty:

            st.caption(
                "Select one or more guests to delete."
            )


            # ------------------------------------------------
            # CREATE UNIQUE LABELS
            # ------------------------------------------------

            guest_options = {}

            for _, row in df.iterrows():

                guest_id = int(
                    row["id"]
                )

                guest_name = str(
                    row["Guest Name"]
                )

                gender = str(
                    row["Gender Vote"]
                )

                attending = str(
                    row["Attending"]
                )

                label = (
                    f"{guest_name} "
                    f"• {gender} "
                    f"• {attending} "
                    f"• ID {guest_id}"
                )

                guest_options[
                    label
                ] = guest_id


            # ------------------------------------------------
            # DYNAMIC MULTISELECT KEY
            # ------------------------------------------------
            #
            # IMPORTANT:
            # We DO NOT assign to the widget's session-state
            # key after the widget has been created.
            #
            # Instead, after deletion we increase the version.
            # This creates a brand-new multiselect widget and
            # therefore clears its selections safely.

            selector_key = (
                "delete_guest_selector_"
                + str(
                    st.session_state.delete_selector_version
                )
            )


            selected_guest_labels = st.multiselect(

                "☑️ Select entries",

                options=list(
                    guest_options.keys()
                ),

                key=selector_key,

                placeholder=(
                    "Choose one or more guests..."
                )
            )


            # ------------------------------------------------
            # SELECTED IDS
            # ------------------------------------------------

            selected_ids = [
                guest_options[label]
                for label in selected_guest_labels
            ]


            # ------------------------------------------------
            # DELETE BUTTON
            # ------------------------------------------------

            if selected_ids:

                st.warning(
                    f"⚠️ {len(selected_ids)} "
                    f"entry/entries selected."
                )


                if not st.session_state[
                    "confirm_delete_selected"
                ]:

                    if st.button(
                        "🗑️ Delete Selected Entries",
                        key="delete_selected_button",
                        use_container_width=True
                    ):

                        # Store IDs separately so the
                        # selection survives confirmation.
                        st.session_state[
                            "pending_delete_ids"
                        ] = selected_ids

                        st.session_state[
                            "confirm_delete_selected"
                        ] = True

                        st.rerun()


            # ------------------------------------------------
            # DELETE CONFIRMATION
            # ------------------------------------------------

            if st.session_state[
                "confirm_delete_selected"
            ]:

                pending_ids = st.session_state.get(
                    "pending_delete_ids",
                    []
                )


                st.error(
                    f"⚠️ You are about to permanently "
                    f"delete {len(pending_ids)} "
                    f"entry/entries."
                )


                delete_col1, delete_col2 = (
                    st.columns(2)
                )


                with delete_col1:

                    if st.button(
                        "❌ Cancel",
                        key="cancel_delete_button",
                        use_container_width=True
                    ):

                        st.session_state[
                            "confirm_delete_selected"
                        ] = False

                        st.session_state[
                            "pending_delete_ids"
                        ] = []

                        # Change selector key to clear
                        # previous selections.

                        st.session_state[
                            "delete_selector_version"
                        ] += 1

                        st.rerun()


                with delete_col2:

                    if st.button(
                        "🗑️ YES, DELETE",
                        key="confirm_delete_button",
                        use_container_width=True
                    ):

                        deleted_count = (
                            delete_selected_rows(
                                pending_ids
                            )
                        )


                        st.cache_data.clear()


                        st.session_state[
                            "confirm_delete_selected"
                        ] = False


                        st.session_state[
                            "pending_delete_ids"
                        ] = []


                        st.session_state[
                            "delete_selector_version"
                        ] += 1


                        st.success(
                            f"✅ {deleted_count} "
                            f"entry/entries deleted."
                        )


                        st.rerun()


            # ------------------------------------------------
            # DISPLAY DATA
            # ------------------------------------------------

            st.divider()

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
            ].copy()


            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "No guest responses yet."
            )


        # ====================================================
        # EXCEL DOWNLOAD
        # ====================================================

        st.divider()

        st.subheader(
            "📥 Download Guest Data"
        )


        if not df.empty:

            excel_file = create_excel_file(
                df
            )


            st.download_button(
                label="📊 Download Excel",
                data=excel_file,
                file_name=(
                    "Baby_Shower_Guest_Responses.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

        else:

            st.info(
                "No data available to download."
            )


        # ====================================================
        # DANGER ZONE
        # ====================================================

        st.divider()

        st.subheader(
            "⚠️ Danger Zone"
        )


        st.warning(
            "Reset Entire App permanently deletes "
            "ALL guest predictions, attendance, "
            "gender votes, name suggestions and messages."
        )


        # ----------------------------------------------------
        # RESET BUTTON
        # ----------------------------------------------------

        if not st.session_state[
            "confirm_reset_app"
        ]:

            if st.button(
                "🧹 Reset Entire App",
                key="reset_entire_app_button",
                use_container_width=True
            ):

                st.session_state[
                    "confirm_reset_app"
                ] = True

                st.rerun()


        # ----------------------------------------------------
        # RESET CONFIRMATION
        # ----------------------------------------------------

        else:

            st.error(
                "⚠️ THIS WILL DELETE EVERYTHING."
            )

            st.write(
                "All guest responses will be permanently removed."
            )


            reset_col1, reset_col2 = (
                st.columns(2)
            )


            with reset_col1:

                if st.button(
                    "❌ Cancel",
                    key="cancel_reset_button",
                    use_container_width=True
                ):

                    st.session_state[
                        "confirm_reset_app"
                    ] = False

                    st.rerun()


            with reset_col2:

                if st.button(
                    "🧹 YES, RESET EVERYTHING",
                    key="confirm_reset_button",
                    use_container_width=True
                ):

                    reset_entire_database()


                    st.cache_data.clear()


                    # Clear previous submission
                    st.session_state[
                        "submission_confirmation"
                    ] = None


                    # Force new empty form
                    st.session_state[
                        "form_reset"
                    ] += 1


                    # Clear delete state
                    st.session_state[
                        "confirm_delete_selected"
                    ] = False


                    st.session_state[
                        "confirm_reset_app"
                    ] = False


                    st.session_state[
                        "pending_delete_ids"
                    ] = []


                    st.session_state[
                        "delete_selector_version"
                    ] += 1


                    st.rerun()


        # ====================================================
        # REFRESH
        # ====================================================

        st.divider()


        if st.button(
            "🔄 Refresh Dashboard",
            key="admin_refresh_button",
            use_container_width=True
        ):

            st.cache_data.clear()

            st.rerun()


        # ====================================================
        # LOGOUT
        # ====================================================

        if st.button(
            "🔒 Lock Private Dashboard",
            key="admin_logout_button",
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
