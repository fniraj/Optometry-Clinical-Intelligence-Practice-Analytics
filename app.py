from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Optometry Practice Intelligence', page_icon='👁️', layout='wide')
DATA = Path(__file__).resolve().parent / 'data'

@st.cache_data
def read_data(filename):
    return pd.read_csv(DATA / filename, encoding='utf-8-sig')

st.title('Optometry Clinical Intelligence, Revenue Cycle & Practice Operations')
st.caption('Single-branch analytical prototype • Aggregated data only • Not for clinical diagnosis or financial reporting')
module = st.sidebar.radio('Select module', ['Clinical Intelligence', 'Revenue Cycle Analytics', 'Practice Operations', 'Data Quality & Methodology', 'AI Clinical & Practice Intelligence Assistant'])
st.sidebar.info('Financial and daily activity figures are PRELIMINARY and not validated. Blank or missing reports do not mean zero activity.')

if module == 'Clinical Intelligence':
    st.header('Refractive Prescription Intelligence')
    df = read_data('refractive_grouped_counts.csv')
    total = int(df['Count'].sum())
    c1,c2,c3 = st.columns(3)
    c1.metric('Recorded lens entries', f'{total:,}')
    c2.metric('Single vision', f"{int(df.loc[df['Lens group']=='Single vision','Count'].sum()):,}")
    c3.metric('Bifocal / multifocal', f"{int(df.loc[df['Lens group']=='Bifocal/multifocal','Count'].sum()):,}")
    st.warning('These are aggregated lens entries, not unique patients. SPH-band summaries cannot establish patient-level disease diagnoses or coexisting refractive conditions.')
    st.subheader('Vision correction product utilization')
    st.bar_chart(df.groupby('Lens group', as_index=True)['Count'].sum())
    group = st.selectbox('Lens group', sorted(df['Lens group'].unique()))
    filtered = df[df['Lens group']==group]
    st.subheader('SPH distribution (original source bands)')
    st.bar_chart(filtered.set_index('SPH band (source label)')['Count'])
    with st.expander('View grouped source data'):
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.info('Disease classification requires validated diagnosis labels and suitable clinical predictors. It is not implemented in this prototype.')

elif module == 'Revenue Cycle Analytics':
    st.header('Revenue Cycle Analytics — Preliminary Extracts')
    df = read_data('practice_monthly_aggregates_preliminary.csv')
    st.error('NOT VALIDATED: extracted figures are incomplete and may omit transactions. Currency, gross/net basis, and source reconciliation are unresolved. Do not use as actual practice revenue.')
    years = sorted(df['year'].dropna().unique())
    year = st.selectbox('Year', years, index=len(years)-1)
    subset = df[df['year']==year].sort_values('month').copy()
    subset['period'] = subset['year'].astype(str) + '-' + subset['month'].astype(str).str.zfill(2)
    st.subheader('Extracted invoice-total-like values by month (unverified)')
    st.bar_chart(subset.set_index('period')['invoice_total'])
    st.subheader('Extracted components (unverified; not necessarily additive)')
    fields = ['consultation','lens','frame','contact_lens','other_services']
    st.line_chart(subset.set_index('period')[fields])
    st.dataframe(subset[['period','days_with_activity','activity_rows','invoice_total'] + fields], use_container_width=True, hide_index=True)
    st.caption('October 2025 may contain a misdated record. Missing months and blank templates must not be interpreted as zero. No revenue reconciliation or profit calculations are claimed.')

elif module == 'Practice Operations':
    st.header('Healthcare Practice Operations — Preliminary Extracts')
    df = read_data('practice_daily_aggregates_preliminary.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values('date')
    st.warning('Activity rows are extracted report entries, NOT verified patient visits or unique patients. Incomplete months are not comparable without further validation.')
    st.metric('Dates with extracted activity', df['date'].nunique())
    st.subheader('Extracted report entries by date')
    st.line_chart(df.set_index('date')['activity_rows'])
    st.subheader('Medical-aid-tagged extracted rows')
    st.line_chart(df.set_index('date')['medical_aid_tagged_rows'])
    st.dataframe(df[['date','activity_rows','medical_aid_tagged_rows']], use_container_width=True, hide_index=True)
    st.info('Recall completion rates, patient-level conversion, and turnaround times are not yet validated or implemented.')

elif module == 'Data Quality & Methodology':
    st.header('Data Quality & Methodology')
    issues = read_data('financial_data_quality_issues.csv')
    st.dataframe(issues, use_container_width=True, hide_index=True)
    audit = read_data('daily_report_extraction_audit.csv')
    st.subheader('Daily-report extraction coverage')
    st.dataframe(audit, use_container_width=True, hide_index=True)
    st.markdown('''**Data handling:** Only aggregated working extracts are included in this prototype. Original patient and invoice-level files are intentionally excluded.\n\n**Not yet implemented:** MySQL connection, Power BI report, patient-level analysis, ML disease classification, automatic Optimax data refresh. The AI assistant uses a locally downloaded Qwen language model.\n\n**Before external demonstration:** Validate figures against source reports, obtain authorization for practice data use, and replace confidential financial values with approved or synthetic figures.''')

else:
    # MODULE 5: QWEN WITH PYTHON-CALCULATED, GROUNDED RESULTS
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    st.header("AI Clinical & Practice Intelligence Assistant")
    st.caption("Qwen 2.5 • Local language model • Python-verified dataset figures")

    @st.cache_resource(show_spinner="Loading Qwen LLM...")
    def load_llm():
        model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float32
        )
        model.eval()
        return tokenizer, model

    @st.cache_data
    def clinical_facts():
        df = read_data("refractive_grouped_counts.csv").copy()
        df["Count"] = pd.to_numeric(df["Count"], errors="coerce")
        if df["Count"].isna().any() or (df["Count"] < 0).any():
            raise ValueError("Invalid or missing counts in the lens dataset.")
        totals = df.groupby("Lens group")["Count"].sum()
        single = int(totals.get("Single vision", 0))
        multi = int(totals.get("Bifocal/multifocal", 0))
        total = int(totals.sum())
        other = total - single - multi
        return {"total": total, "single": single, "multi": multi,
                "other": other, "categories": totals.to_dict()}

    facts = clinical_facts()
    total = facts["total"]
    single = facts["single"]
    multi = facts["multi"]
    single_pct = 100 * single / total if total else 0
    multi_pct = 100 * multi / total if total else 0

    # Deterministic, audited arithmetic: the LLM never calculates these figures.
    facts_text = (
        f"Source: refractive_grouped_counts.csv (aggregated lens entries, NOT patients). "
        f"Total entries across all categories: {total:,}. "
        f"Single vision: {single:,} ({single_pct:.1f}% of all entries). "
        f"Bifocal/multifocal: {multi:,} ({multi_pct:.1f}% of all entries). "
        f"Other categories, if any: {facts['other']:,}. "
        f"Single-vision minus bifocal/multifocal: {single - multi:+,} entries. "
        "These descriptive counts do not establish statistical significance, "
        "unique patient counts, diagnoses, or clinical outcomes."
    )

    st.subheader("Calculated facts from the source CSV")
    a, b, c = st.columns(3)
    a.metric("All recorded lens entries", f"{total:,}")
    b.metric("Single vision", f"{single:,}", f"{single_pct:.1f}%")
    c.metric("Bifocal / multifocal", f"{multi:,}", f"{multi_pct:.1f}%")
    st.caption("These numbers are calculated by pandas, not generated by the LLM.")

    if "qwen_grounded_chat" not in st.session_state:
        st.session_state.qwen_grounded_chat = []

    for item in st.session_state.qwen_grounded_chat:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

    question = st.chat_input("Ask about your lens data or any general topic...")
    if question:
        st.session_state.qwen_grounded_chat.append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            q = question.casefold()
            # For numerical questions about this practice, provide only Python's
            # calculations. No model-generated figures or unsupported inference.
            financial_terms = (
                "revenue", "profit", "invoice", "sales", "medical aid",
                "medical-aid", "outstanding", "payment", "turnover"
            )
            numerical_terms = (
                "how many", "number", "count", "total", "percent",
                "percentage", "compare", "comparison", "more common",
                "most common", "utilization", "distribution", "difference",
                "majority", "which lens", "proportion"
            )
            lens_terms = (
                "lens", "lenses", "prescription", "single vision",
                "single-vision", "multifocal", "bifocal", "utilization"
            )
            practice_context = ("our ", "my ", "practice", "clinic", "branch", "optimax", "dataset", "data", "records")
            if any(term in q for term in financial_terms) and any(term in q for term in practice_context):
                answer = (
                    "The available financial and activity extracts have not been "
                    "validated against the source reports. I cannot give reliable "
                    "practice revenue, payment, or medical-aid figures."
                )
            elif any(term in q for term in numerical_terms) and any(
                term in q for term in lens_terms
            ):
                answer = (
                    "**Python-calculated findings**\n\n" + facts_text +
                    "\n\n**Interpretation:** These are descriptive lens-entry "
                    "frequencies only. We cannot infer unique patients, "
                    "disease prevalence, or statistical significance."
                )
            else:
                system_message = (
                    "You are an optometry education and practice analytics assistant. "
                    "Answer general conceptual questions concisely. Do not diagnose "
                    "individual patients or recommend personalized treatment. "
                    "For THIS PRACTICE, do not invent numerical results, counts, "
                    "percentages, rankings, or comparisons: those are handled "
                    "by separate Python calculations. General educational numbers "
                    "and scientific explanations are allowed. "
                    "Never claim financial data are verified. "
                    "State clearly when evidence is insufficient."
                )
                try:
                    with st.spinner("Qwen is generating an explanation..."):
                        tokenizer, model = load_llm()
                        messages = [
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": question},
                        ]
                        prompt = tokenizer.apply_chat_template(
                            messages, tokenize=False, add_generation_prompt=True
                        )
                        encoded = tokenizer(
                            prompt, return_tensors="pt", truncation=True,
                            max_length=1500
                        )
                        with torch.inference_mode():
                            output = model.generate(
                                **encoded, max_new_tokens=220,
                                do_sample=False,
                                pad_token_id=tokenizer.eos_token_id
                            )
                        new_tokens = output[0][encoded["input_ids"].shape[1]:]
                        draft = tokenizer.decode(
                            new_tokens, skip_special_tokens=True
                        ).strip()
                    # General educational answers may legitimately contain numbers
                    # (e.g., qubits, dates, or model versions). Only practice-specific
                    # metrics are answered through the deterministic Python branch.
                    answer = draft or "No response generated. Please try again."
                except Exception as error:
                    answer = f"Could not run the local LLM: {error}"
            st.markdown(answer)
            st.session_state.qwen_grounded_chat.append(
                {"role": "assistant", "content": answer}
            )

    if st.button("Clear Chat History"):
        st.session_state.qwen_grounded_chat = []
        st.rerun()

    st.warning(
        "Numerical practice findings are computed directly from the source CSV. "
        "The local LLM is used for general explanations only; those explanations "
        "can still be incorrect. The financial extracts remain unvalidated."
    )
