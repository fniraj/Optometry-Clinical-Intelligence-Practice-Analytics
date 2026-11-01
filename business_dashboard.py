import streamlit as st
import mysql.connector
import pandas as pd

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Optometry Business Analytics",
    layout="wide"
)

st.title("Optometry Business Analytics Dashboard")

st.warning(
    "Preliminary data: Financial figures require validation. "
    "Activity records do not necessarily represent unique patients."
)

# --------------------------------------------------
# MYSQL CONNECTION
# --------------------------------------------------

password = st.text_input(
    "Enter MySQL Password",
    type="password"
)

if password:

    try:

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database="optometry_practice_intelligence"
        )

        def load_table(table_name):

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                f"SELECT * FROM `{table_name}`"
            )

            df = pd.DataFrame(cursor.fetchall())

            cursor.close()

            return df

        monthly = load_table("practice_monthly_preliminary")
        daily = load_table("practice_daily_preliminary")

        connection.close()

        st.success("Connected to MySQL successfully!")

        if monthly.empty:
            st.error("No monthly data available.")
            st.stop()

        # --------------------------------------------------
        # PREPARE MONTHLY DATA
        # --------------------------------------------------

        monthly["reporting_year"] = pd.to_numeric(
            monthly["reporting_year"],
            errors="coerce"
        )

        monthly["reporting_month"] = pd.to_numeric(
            monthly["reporting_month"],
            errors="coerce"
        )

        monthly = monthly.dropna(
            subset=["reporting_year", "reporting_month"]
        ).copy()

        monthly["month"] = pd.to_datetime(
            dict(
                year=monthly["reporting_year"].astype(int),
                month=monthly["reporting_month"].astype(int),
                day=1
            ),
            errors="coerce"
        )

        monthly = monthly.dropna(subset=["month"])

        monthly["invoice_total_amount"] = pd.to_numeric(
            monthly["invoice_total_amount"],
            errors="coerce"
        )

        monthly["activity_rows"] = pd.to_numeric(
            monthly["activity_rows"],
            errors="coerce"
        )

        monthly = monthly.sort_values("month")

        # --------------------------------------------------
        # YEAR FILTER
        # --------------------------------------------------

        st.sidebar.header("Filters")

        available_years = sorted(
            monthly["reporting_year"].dropna().astype(int).unique()
        )

        selected_years = st.sidebar.multiselect(
            "Select Year",
            available_years,
            default=available_years
        )

        filtered = monthly[
            monthly["reporting_year"].isin(selected_years)
        ].copy()

        if filtered.empty:
            st.warning("No data available for selected years.")
            st.stop()

        filtered = filtered.sort_values("month")

        filtered["month_label"] = (
            filtered["month"].dt.strftime("%b %Y")
        )

        # --------------------------------------------------
        # BUSINESS KPIs
        # --------------------------------------------------

        st.header("Business Performance KPIs")

        highest = filtered.loc[
            filtered["invoice_total_amount"].idxmax()
        ]

        busiest = filtered.loc[
            filtered["activity_rows"].idxmax()
        ]

        total_activity = filtered["activity_rows"].sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Highest Monthly Invoice Total (Preliminary)",
                f"{highest['invoice_total_amount']:,.0f}",
                highest["month"].strftime("%b %Y")
            )

        with col2:
            st.metric(
                "Busiest Month",
                f"{int(busiest['activity_rows']):,} records",
                busiest["month"].strftime("%b %Y")
            )

        with col3:
            st.metric(
                "Total Activity Records",
                f"{int(total_activity):,}"
            )

        # --------------------------------------------------
        # MONTHLY REVENUE TREND
        # --------------------------------------------------

        st.header("Monthly Revenue Trend (Preliminary)")

        st.line_chart(
            filtered.set_index("month_label")[
                "invoice_total_amount"
            ],
            x_label="Month",
            y_label="Invoice Total (Preliminary)"
        )

        # --------------------------------------------------
        # MONTHLY ACTIVITY
        # --------------------------------------------------

        st.header("Monthly Practice Activity")

        st.bar_chart(
            filtered.set_index("month_label")[
                "activity_rows"
            ],
            x_label="Month",
            y_label="Activity Records"
        )

        # --------------------------------------------------
        # REVENUE BREAKDOWN BY SERVICE
        # --------------------------------------------------

        st.header("Revenue Breakdown by Service (Preliminary)")

        service_columns = {
            "Lenses": "lens_amount",
            "Frames": "frame_amount",
            "Consultations": "consultation_amount",
            "Contact Lenses": "contact_lens_amount",
            "Other Services": "other_services_amount"
        }

        service_totals = {}

        for service, column in service_columns.items():

            if column in filtered.columns:

                values = pd.to_numeric(
                    filtered[column],
                    errors="coerce"
                )

                service_totals[service] = values.sum()

        if service_totals:

            service_df = pd.DataFrame(
                {
                    "Service": list(service_totals.keys()),
                    "Invoice Amount": list(service_totals.values())
                }
            )

            st.bar_chart(
                service_df.set_index("Service")
            )

            st.dataframe(
                service_df,
                hide_index=True,
                width="stretch"
            )

        else:
            st.warning(
                "No recognized service revenue columns found."
            )

        # --------------------------------------------------
        # DAILY OPERATIONS ANALYTICS
        # --------------------------------------------------

        st.header("Daily Operations Analytics")

        if daily.empty:

            st.warning("No daily data available.")

        else:

            # Identify date column safely
            if "activity_date" in daily.columns:
                date_col = "activity_date"

            elif "reporting_date" in daily.columns:
                date_col = "reporting_date"

            elif "date" in daily.columns:
                date_col = "date"

            else:
                date_col = None

            if date_col is None:

                st.warning(
                    "Daily date column not recognized. "
                    "Daily analytics cannot be calculated."
                )

                st.write(
                    "Available daily columns:",
                    daily.columns.tolist()
                )

            else:

                daily[date_col] = pd.to_datetime(
                    daily[date_col],
                    errors="coerce"
                )

                daily = daily.dropna(
                    subset=[date_col]
                ).copy()

                daily = daily[
                    daily[date_col].dt.year.isin(selected_years)
                ].copy()

                daily = daily.sort_values(date_col)

                if daily.empty:

                    st.info(
                        "No daily records for the selected years."
                    )

                else:

                    st.subheader("Daily Practice Records")

                    st.dataframe(
                        daily,
                        width="stretch"
                    )

                    daily["weekday"] = (
                        daily[date_col].dt.day_name()
                    )

                    weekday_order = [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday"
                    ]

                    # --------------------------------------
                    # ACTIVITY BY WEEKDAY
                    # --------------------------------------

                    st.subheader("Activity by Weekday")

                    if "activity_rows" in daily.columns:

                        daily["activity_rows"] = pd.to_numeric(
                            daily["activity_rows"],
                            errors="coerce"
                        )

                        valid_activity = daily.dropna(
                            subset=["activity_rows"]
                        ).copy()

                        valid_activity = valid_activity[
                            valid_activity["activity_rows"] >= 0
                        ]

                        if valid_activity.empty:

                            st.warning(
                                "No valid daily activity counts found."
                            )

                        else:

                            weekday_activity = (
                                valid_activity.groupby("weekday")[
                                    "activity_rows"
                                ]
                                .sum()
                                .reindex(
                                    weekday_order,
                                    fill_value=0
                                )
                            )

                            st.bar_chart(
                                weekday_activity,
                                x_label="Weekday",
                                y_label="Activity Records"
                            )

                            st.metric(
                                "Busiest Weekday",
                                weekday_activity.idxmax()
                            )

                            st.caption(
                                "Based on recorded daily activity. "
                                "Zero does not prove the practice was closed."
                            )

                    else:

                        st.warning(
                            "The daily table does not contain "
                            "'activity_rows'. Weekday activity "
                            "cannot be calculated reliably."
                        )

                        st.write(
                            "Daily table columns:",
                            daily.columns.tolist()
                        )

                    # --------------------------------------
                    # DAILY INVOICE TREND
                    # --------------------------------------

                    st.subheader(
                        "Daily Invoice Trend (Preliminary)"
                    )

                    if "invoice_total_amount" in daily.columns:

                        daily["invoice_total_amount"] = pd.to_numeric(
                            daily["invoice_total_amount"],
                            errors="coerce"
                        )

                        valid_revenue = daily.dropna(
                            subset=["invoice_total_amount"]
                        )

                        if not valid_revenue.empty:

                            daily_revenue = (
                                valid_revenue.groupby(date_col)[
                                    "invoice_total_amount"
                                ]
                                .sum()
                                .sort_index()
                            )

                            st.line_chart(
                                daily_revenue,
                                x_label="Date",
                                y_label="Invoice Total (Preliminary)"
                            )

                        else:

                            st.info(
                                "No valid daily invoice amounts found."
                            )

                    else:

                        st.warning(
                            "Daily invoice total column not found."
                        )

        # --------------------------------------------------
        # DATA QUALITY
        # --------------------------------------------------

        st.header("Data Quality Notes")

        st.info(
            "1. Financial amounts are preliminary and unvalidated.\n\n"
            "2. Invoice totals are not confirmed cash collections.\n\n"
            "3. Activity records are not necessarily unique patients.\n\n"
            "4. Missing months are not automatically treated as zero.\n\n"
            "5. Weekday activity depends on the correctness of "
            "the original daily records."
        )

    except mysql.connector.Error as error:

        st.error(
            f"MySQL connection error: {error}"
        )

    except Exception as error:

        st.error(
            f"Dashboard error: {error}"
        )