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
        f'<div class="prediction-label">'
        f'<span class="boy-label">💙 Baby Boy</span>'
        f'<span>{boy_percentage:.1f}%</span>'
        f'</div>'
        f'<div class="prediction-bar-container boy-bar-background">'
        f'<div class="prediction-bar boy-bar" '
        f'style="width:{boy_percentage:.1f}%;"></div>'
        f'</div>',
        unsafe_allow_html=True
    )
# ========================================================
    # GIRL PROGRESS
    # ========================================================
    st.markdown(
        f'<div class="prediction-label">'
        f'<span class="girl-label">💗 Baby Girl</span>'
        f'<span>{girl_percentage:.1f}%</span>'
        f'</div>'
        f'<div class="prediction-bar-container girl-bar-background">'
        f'<div class="prediction-bar girl-bar" '
        f'style="width:{girl_percentage:.1f}%;"></div>'
        f'</div>',
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
