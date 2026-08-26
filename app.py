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

if "form_reset" not in st.session_state:
    st.session_state.form_reset = 0

if "submission_confirmation" not in st.session_state:
    st.session_state.submission_confirmation = None

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "confirm_delete_selected" not in st.session_state:
    st.session_state.confirm_delete_selected = False

if "confirm_reset_app" not in st.session_state:
    st.session_state.confirm_reset_app = False


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
        padding-top: 3rem !important;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }

    .main-title {
        text-align: center;
        font-size: 2.3rem;
        font-weight: 800;
        color: #5b4b8a;
        margin-top: 0.3rem;
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

    .footer {
        text-align: center;
        color: #999999;
        margin-top: 40px;
        padding-bottom: 15px;
        font-size: 0.85rem;
    }

    .danger-box {
        padding: 12px;
        border-radius: 10px;
        background: #fff1f1;
        border: 1px solid #ffcccc;
        margin-bottom: 12px;
    }

    @media (max-width: 600px) {

        .block-container {
            padding-top: 2.5rem !important;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .main-title {
            font-size: 1.9rem;
        }

        .subtitle {
            font-size: 0.85rem;
        }

        .small-heading {
            font-size: 1.2rem;
        }

        .prediction-label {
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
# INITIALIZE DATABASE
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
# GET PREDICTIONS
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
# DELETE SELECTED ROWS
# ============================================================

def delete_selected_rows(selected_ids):

    if not selected_ids:
        return False

    connection = get_connection()

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

    connection.commit()

    deleted_count = cursor.rowcount

    connection.close()

    return deleted_count


# ============================================================
# RESET ENTIRE DATABASE
# ============================================================

def reset_entire_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM predictions"
    )

    cursor.execute(
        """
        DELETE FROM sqlite_sequence
        WHERE name = 'predictions'
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# CREATE EXCEL FILE
# ============================================================

def create_excel_file(dataframe):

    output = BytesIO()

    export_columns = [
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
        export_columns
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
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">👶 Baby Shower 🎀</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Make your prediction and join the fun! 💕'
    '</div>',
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

    st.markdown(
        '<div class="small-heading">'
        '🎊 Make Your Prediction'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Fill in your prediction below."
    )

    current_form_key = (
        f"baby_prediction_form_"
        f"{st.session_state.form_reset}"
    )

    with st.form(
        current_form_key
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
            placeholder=(
                "Write your wishes for the parents "
                "and baby..."
            )
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

            gender_value = (
                "Boy"
                if gender_vote.startswith("Boy")
                else "Girl"
            )

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


            # =================================================
            # SUCCESS
            # =================================================

            if result.get("success"):

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

                st.cache_data.clear()

                # New form key = empty form
                st.session_state.form_reset += 1

                # Rerun immediately
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


    # ========================================================
    # SUBMISSION CONFIRMATION
    # ========================================================

    if st.session_state.get(
        "submission_confirmation"
    ):

        submission = st.session_state[
            "submission_confirmation"
        ]

        st.divider()

        st.markdown(
            '<div class="small-heading">'
            '💝 Your Submitted Details'
            '</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Your prediction has been submitted successfully."
        )

        st.info(
            f"👤 **Guest Name:** "
            f"{submission['guest_name']}"
        )

        st.write(
            f"✅ **Attending:** "
            f"{submission['attending']}"
        )

        if submission["gender"] == "Boy":

            st.write(
                "🔮 **Gender Prediction:** "
                "💙 Boy 👦"
            )

        else:

            st.write(
                "🔮 **Gender Prediction:** "
                "💗 Girl 👧"
            )

        st.write(
            f"📅 **Predicted Arrival Date:** "
            f"{submission['guessed_date']}"
        )

        if submission["boy_name"]:

            st.write(
                f"👦 **Baby Boy Name:** "
                f"{submission['boy_name']}"
            )

        if submission["girl_name"]:

            st.write(
                f"👧 **Baby Girl Name:** "
                f"{submission['girl_name']}"
            )

        if submission["message"]:

            st.write(
                "💌 **Message:**"
            )

            st.info(
                submission["message"]
            )

        st.success(
            "💕 Thank you for being part of our Baby Shower!"
        )


# ============================================================
# TAB 2 — GENDER PREDICTION
# ============================================================

with gender_tab:

    st.markdown(
        '<div class="small-heading">'
        '🔮 Baby Gender Predictions'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "What is everyone guessing? 💙💗"
    )


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

    col1, col2 = st.columns(2)

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

    st.metric(
        "🍼 Total Predictions",
        total_votes
    )


    st.divider()


    # ========================================================
    # BOY BAR
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

        <div class="prediction-bar-container boy-bar-background">
            <div
                class="prediction-bar boy-bar"
                style="width:{boy_percentage:.1f}%;">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # GIRL BAR
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

        <div class="prediction-bar-container girl-bar-background">
            <div
                class="prediction-bar girl-bar"
                style="width:{girl_percentage:.1f}%;">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    st.divider()


    # ========================================================
    # DONUT
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


    if st.button(
        "🔄 Refresh Predictions",
        key="refresh_gender",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()


# ============================================================
# TAB 3 — PRIVATE ADMIN
# ============================================================

with admin_tab:

    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.admin_authenticated:

        st.markdown(
            '<div class="small-heading">'
            '🔐 Private Dashboard'
            '</div>',
            unsafe_allow_html=True
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

        st.markdown(
            '<div class="small-heading">'
            '🔐 Private Dashboard'
            '</div>',
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
                "👥 Total Guests",
                len(df)
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


        st.divider()


        # ====================================================
        # NAME SUGGESTIONS
        # ====================================================

        st.subheader(
            "👶 Name Suggestions"
        )

        name_col1, name_col2 = st.columns(2)

        with name_col1:

            st.markdown(
                "### 👦 Baby Boy"
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


        with name_col2:

            st.markdown(
                "### 👧 Baby Girl"
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
        # GUEST RESPONSES
        # ====================================================

        st.subheader(
            "👨‍👩‍👧 Guest Responses"
        )


        if not df.empty:

            st.caption(
                "☑️ Select one or more guests to delete."
            )


            # ------------------------------------------------
            # CREATE EDITABLE SELECTION TABLE
            # ------------------------------------------------

            selection_df = df[
                [
                    "id",
                    "Guest Name",
                    "Attending",
                    "Gender Vote",
                    "Date",
                    "Baby Boy Name",
                    "Baby Girl Name",
                    "Message"
                ]
            ].copy()


            selection_df.insert(
                0,
                "Delete",
                False
            )


            edited_df = st.data_editor(

                selection_df,

                use_container_width=True,

                hide_index=True,

                disabled=[
                    "id",
                    "Guest Name",
                    "Attending",
                    "Gender Vote",
                    "Date",
                    "Baby Boy Name",
                    "Baby Girl Name",
                    "Message"
                ],

                column_config={

                    "Delete":
                        st.column_config.CheckboxColumn(
                            "☑️ Delete",
                            help=(
                                "Select this guest "
                                "for deletion."
                            ),
                            default=False
                        ),

                    "id":
                        st.column_config.NumberColumn(
                            "ID",
                            width="small"
                        ),

                    "Guest Name":
                        st.column_config.TextColumn(
                            "Guest Name"
                        ),

                    "Attending":
                        st.column_config.TextColumn(
                            "Attending"
                        ),

                    "Gender Vote":
                        st.column_config.TextColumn(
                            "Gender Vote"
                        ),

                    "Date":
                        st.column_config.TextColumn(
                            "Date"
                        ),

                    "Baby Boy Name":
                        st.column_config.TextColumn(
                            "Baby Boy Name"
                        ),

                    "Baby Girl Name":
                        st.column_config.TextColumn(
                            "Baby Girl Name"
                        ),

                    "Message":
                        st.column_config.TextColumn(
                            "Message"
                        )
                },

                key="guest_delete_editor"
            )


            selected_rows = edited_df[
                edited_df["Delete"] == True
            ]


            selected_ids = selected_rows[
                "id"
            ].tolist()


            # ------------------------------------------------
            # DELETE SELECTED
            # ------------------------------------------------

            if selected_ids:

                st.warning(
                    f"⚠️ {len(selected_ids)} "
                    f"entry/entries selected."
                )

                if st.button(
                    "🗑️ Delete Selected Entries",
                    key="delete_selected",
                    use_container_width=True
                ):

                    st.session_state[
                        "confirm_delete_selected"
                    ] = True

                    st.rerun()


            # ------------------------------------------------
            # CONFIRM DELETE
            # ------------------------------------------------

            if st.session_state[
                "confirm_delete_selected"
            ]:

                st.error(
                    f"⚠️ You are about to permanently "
                    f"delete {len(selected_ids)} "
                    f"selected entry/entries."
                )

                delete_col1, delete_col2 = st.columns(2)


                with delete_col1:

                    if st.button(
                        "❌ Cancel",
                        key="cancel_delete_selected",
                        use_container_width=True
                    ):

                        st.session_state[
                            "confirm_delete_selected"
                        ] = False

                        st.rerun()


                with delete_col2:

                    if st.button(
                        "🗑️ YES, DELETE",
                        key="confirm_delete_selected",
                        use_container_width=True
                    ):

                        if selected_ids:

                            deleted_count = (
                                delete_selected_rows(
                                    selected_ids
                                )
                            )

                            st.cache_data.clear()

                            st.session_state[
                                "confirm_delete_selected"
                            ] = False

                            st.session_state[
                                "submission_confirmation"
                            ] = None

                            st.success(
                                f"✅ {deleted_count} "
                                f"entry/entries deleted."
                            )

                            st.rerun()


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


        if not st.session_state[
            "confirm_reset_app"
        ]:

            if st.button(
                "🧹 Reset Entire App",
                key="reset_entire_app",
                use_container_width=True
            ):

                st.session_state[
                    "confirm_reset_app"
                ] = True

                st.rerun()


        else:

            st.error(
                "⚠️ THIS WILL DELETE EVERYTHING."
            )

            st.write(
                "All guest responses will be permanently removed."
            )


            reset_col1, reset_col2 = st.columns(2)


            with reset_col1:

                if st.button(
                    "❌ Cancel",
                    key="cancel_reset_app",
                    use_container_width=True
                ):

                    st.session_state[
                        "confirm_reset_app"
                    ] = False

                    st.rerun()


            with reset_col2:

                if st.button(
                    "🧹 YES, RESET EVERYTHING",
                    key="confirm_reset_app",
                    use_container_width=True
                ):

                    reset_entire_database()

                    st.cache_data.clear()

                    st.session_state[
                        "submission_confirmation"
                    ] = None

                    st.session_state[
                        "form_reset"
                    ] += 1

                    st.session_state[
                        "confirm_reset_app"
                    ] = False

                    st.session_state[
                        "confirm_delete_selected"
                    ] = False

                    st.success(
                        "✅ App has been completely reset."
                    )

                    st.rerun()


        # ====================================================
        # REFRESH
        # ====================================================

        st.divider()

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