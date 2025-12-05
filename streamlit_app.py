import streamlit as st
import json
from ai.functions import (
    get_marketing_activities,
    get_challenges,
    get_stuck_detections,
    get_goals,
    get_attendance,
    get_call_sentiment
)
from pydantic import ValidationError

# Page configuration
st.set_page_config(
    page_title="OwnersUp AI Analytics",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Notion-like styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .main {
        padding: 2rem 3rem;
        background-color: #ffffff;
    }

    .stAlert {
        margin-top: 1rem;
        border-radius: 8px;
    }

    /* Notion-style cards */
    .notion-card {
        background: #f7f6f3;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e9e7e3;
        transition: all 0.2s ease;
    }

    .notion-card:hover {
        background: #f1f0ed;
        border-color: #d3d1cb;
    }

    .notion-card h3 {
        margin-top: 0;
        color: #37352f;
        font-weight: 600;
        font-size: 1.25rem;
    }

    .notion-card p {
        color: #787774;
        line-height: 1.6;
        margin-bottom: 0;
    }

    /* Headers */
    h1 {
        color: #37352f;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    h2 {
        color: #37352f;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
    }

    h3 {
        color: #37352f;
        font-weight: 600;
        font-size: 1.25rem;
    }

    /* Subtle emphasis blocks */
    .callout {
        background: #f7f6f3;
        border-left: 3px solid #37352f;
        padding: 1rem 1.25rem;
        border-radius: 6px;
        margin: 1rem 0;
    }

    .callout-blue {
        background: #e7f3ff;
        border-left: 3px solid #0061fe;
    }

    .callout-green {
        background: #e8f5e9;
        border-left: 3px solid #4caf50;
    }

    .callout-orange {
        background: #fff4e5;
        border-left: 3px solid #ff9800;
    }

    /* Clean dividers */
    hr {
        border: none;
        border-top: 1px solid #e9e7e3;
        margin: 2rem 0;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f7f6f3;
    }

    /* Button styling */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid #e9e7e3;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        border-color: #37352f;
    }

    /* Text area styling */
    .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #e9e7e3;
        font-family: 'Inter', sans-serif;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #37352f;
        font-weight: 600;
    }

    /* JSON output */
    .json-output {
        background-color: #f7f6f3;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e9e7e3;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.875rem;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f7f6f3;
        border-radius: 6px;
        font-weight: 500;
    }

    /* Tag-like labels */
    .tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
    }

    .tag-blue {
        background: #e7f3ff;
        color: #0061fe;
    }

    .tag-green {
        background: #e8f5e9;
        color: #2e7d32;
    }

    .tag-orange {
        background: #fff4e5;
        color: #e65100;
    }

    .tag-purple {
        background: #f3e5f5;
        color: #7b1fa2;
    }

    .tag-gray {
        background: #f5f5f5;
        color: #616161;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("OwnersUp Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Marketing Activities",
        "Challenges",
        "Stuck Detections",
        "Weekly Goals",
        "Attendance",
        "Call Sentiment"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown(
    "AI-powered transcript analysis for entrepreneur peer groups and mastermind sessions.",
    unsafe_allow_html=True
)

# Helper function to display JSON nicely
def display_json(data):
    st.markdown('<div class="json-output">', unsafe_allow_html=True)
    st.json(data)
    st.markdown('</div>', unsafe_allow_html=True)

# HOME PAGE
if page == "Home":
    st.title("OwnersUp AI Analytics")
    st.markdown("### Transform mastermind transcripts into actionable insights")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="notion-card">
            <h3>Marketing Analytics</h3>
            <p>Extract and analyze marketing activities, track outcomes, and identify wins from peer group discussions.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="notion-card">
            <h3>Challenge Tracking</h3>
            <p>Identify challenges faced by participants and strategies suggested during sessions.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="notion-card">
            <h3>Stuck Detection</h3>
            <p>Detect when participants are stuck or stalled, with actionable next steps.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col4, col5 = st.columns(2)

    with col4:
        st.markdown("""
        <div class="notion-card">
            <h3>Call Sentiment</h3>
            <p>Analyze emotional tone and group morale to track group health and detect shifts in energy.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="notion-card">
            <h3>Goal Management</h3>
            <p>Extract weekly goals, detect vagueness, and generate Slack-ready accountability messages.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### Key Features")

    feature_col1, feature_col2 = st.columns(2)

    with feature_col1:
        st.markdown("""
        #### Analytics & Insights
        - **Marketing Activity Tracking**: Monitor meetings, proposals, and client acquisition
        - **Outcome Analysis**: Track wins, revenue, and contract types
        - **Progress Monitoring**: Identify momentum and stagnation
        """)

        st.markdown("""
        #### Goal Management
        - **Weekly Goal Extraction**: Automatically capture participant goals
        - **Vagueness Detection**: Identify unclear or non-actionable goals
        - **Accountability Tracking**: Monitor goal setting consistency
        """)

    with feature_col2:
        st.markdown("""
        #### Engagement Tracking
        - **Attendance Monitoring**: Track presence and participation
        - **Status Classification**: Categorize absences (travel, wellness, work)
        - **Engagement Signals**: Detect disengagement early
        """)

        st.markdown("""
        #### AI-Powered Analysis
        - **Natural Language Processing**: Advanced transcript analysis
        - **Pattern Recognition**: Identify trends and insights
        - **Automated Extraction**: Save hours of manual review
        """)

    st.markdown("---")
    st.markdown('<div class="callout-blue">Select a demo from the sidebar to explore each feature</div>', unsafe_allow_html=True)

# MARKETING ACTIVITIES PAGE
elif page == "Marketing Activities":
    st.title("Marketing Activities Extraction")
    st.markdown("Extract marketing activities, outcomes, and wins from mastermind transcripts.")

    st.markdown("---")

    # Sample transcript
    with st.expander("View Sample Transcript"):
        st.text("""
Sample: "This week I did a lot of LinkedIn outreach, sent about 50 connection requests.
From that I got 3 meetings scheduled and sent 2 proposals. One of them signed for a
monthly retainer at $5,000 per month! I'm also working on cold outreach to my network,
reached out to 10 people and have 2 coffee meetings set up for next week."
        """)

    transcript = st.text_area(
        "Enter Transcript",
        height=200,
        placeholder="Paste the mastermind transcript here..."
    )

    if st.button("Analyze Marketing Activities", type="primary"):
        if transcript.strip():
            with st.spinner("Analyzing transcript..."):
                try:
                    result = get_marketing_activities(transcript)

                    st.success("Analysis complete")

                    # Display results
                    st.markdown("### Results")

                    result_dict = result.model_dump(mode='json')

                    # Show summary metrics
                    total_activities = len(result_dict.get('activities', []))
                    st.metric("Total Participants Analyzed", total_activities)

                    # Display each participant's activities
                    for idx, individual in enumerate(result_dict.get('activities', [])):
                        with st.expander(f"{individual.get('name', 'Unknown')} — {len(individual.get('activities', []))} Activities", expanded=True):

                            for activity in individual.get('activities', []):
                                col1, col2, col3 = st.columns([2, 1, 1])

                                with col1:
                                    st.markdown(f"**Activity Type:** {activity.get('activity', 'N/A')}")
                                    st.markdown(f"**Stage:** {activity.get('stage', 'N/A')}")
                                    st.markdown(f"**Notes:** {activity.get('outcome', {}).get('notes', 'N/A')}")

                                with col2:
                                    st.metric("Quantity", activity.get('quanitity', 0))
                                    st.metric("Meetings", activity.get('outcome', {}).get('no_of_meetings', 0))
                                    st.metric("Proposals", activity.get('outcome', {}).get('no_of_proposals', 0))

                                with col3:
                                    is_win = activity.get('is_win', False)
                                    if is_win:
                                        st.markdown('<span class="tag tag-green">WIN</span>', unsafe_allow_html=True)
                                    else:
                                        st.markdown('<span class="tag tag-blue">In Progress</span>', unsafe_allow_html=True)

                                    revenue = activity.get('revenue')
                                    if revenue:
                                        st.metric("Revenue", f"${revenue:,.2f}")

                                    contract = activity.get('contract_type')
                                    if contract:
                                        st.markdown(f"**Contract:** {contract}")

                                st.markdown("---")

                    # Show raw JSON
                    with st.expander("View Raw JSON Output"):
                        display_json(result_dict)

                except ValidationError as e:
                    st.error("Validation Error")
                    st.json(e.errors())
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a transcript to analyze.")

# CHALLENGES PAGE
elif page == "Challenges":
    st.title("Challenges Extraction")
    st.markdown("Identify challenges faced by participants and strategies shared during sessions.")

    st.markdown("---")

    with st.expander("View Sample Transcript"):
        st.text("""
Sample: "I'm really struggling with lead generation. I've been trying different things
but nothing seems to stick. John suggested I focus on LinkedIn content and engage with
prospects' posts before reaching out. Sarah mentioned using a specific framework - the
'Value First' approach where you provide insights before asking for a meeting. That
actually sounds really helpful. I think my main issue is I'm not clear on who my ideal
client is, so my messaging is all over the place."
        """)

    transcript = st.text_area(
        "Enter Transcript",
        height=200,
        placeholder="Paste the mastermind transcript here..."
    )

    if st.button("Extract Challenges", type="primary"):
        if transcript.strip():
            with st.spinner("Analyzing challenges..."):
                try:
                    result = get_challenges(transcript)

                    st.success("Analysis complete")

                    result_dict = result.model_dump(mode='json')

                    # Summary metrics
                    total_challenges = sum(len(ind.get('challenges', [])) for ind in result_dict.get('challenges', []))
                    st.metric("Total Challenges Identified", total_challenges)

                    # Display challenges by participant
                    for individual in result_dict.get('challenges', []):
                        st.markdown(f"### {individual.get('name', 'Unknown')}")

                        for idx, challenge in enumerate(individual.get('challenges', []), 1):
                            with st.expander(f"Challenge {idx} — {challenge.get('category', 'N/A')}", expanded=True):
                                st.markdown(f"**Category:** `{challenge.get('category', 'N/A')}`")
                                st.markdown(f"**Challenge Description:**")
                                st.info(challenge.get('challenge', 'N/A'))

                                st.markdown("**Strategies Suggested:**")
                                for strategy in challenge.get('strategies', []):
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.markdown(f"- **{strategy.get('summary', 'N/A')}**")
                                        if strategy.get('name'):
                                            st.caption(f"Suggested by: {strategy.get('name')}")
                                    with col2:
                                        tag = strategy.get('tag', 'N/A')
                                        if 'Mindset' in tag:
                                            st.markdown(f'<span class="tag tag-purple">{tag}</span>', unsafe_allow_html=True)
                                        elif 'Tactical' in tag:
                                            st.markdown(f'<span class="tag tag-blue">{tag}</span>', unsafe_allow_html=True)
                                        elif 'Resource' in tag:
                                            st.markdown(f'<span class="tag tag-orange">{tag}</span>', unsafe_allow_html=True)
                                        elif 'Connection' in tag:
                                            st.markdown(f'<span class="tag tag-green">{tag}</span>', unsafe_allow_html=True)
                                        elif 'Framework' in tag:
                                            st.markdown(f'<span class="tag tag-blue">{tag}</span>', unsafe_allow_html=True)
                                        else:
                                            st.text(tag)

                                st.markdown("---")

                    # Show raw JSON
                    with st.expander("View Raw JSON Output"):
                        display_json(result_dict)

                except ValidationError as e:
                    st.error("Validation Error")
                    st.json(e.errors())
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a transcript to analyze.")

# STUCK DETECTIONS PAGE
elif page == "Stuck Detections":
    st.title("Stuck Detections")
    st.markdown("Identify when participants are stuck, stalled, or not making progress.")

    st.markdown("---")

    with st.expander("View Sample Transcript"):
        st.text("""
Sample: "I haven't done anything for the past two weeks. I don't know why, I just
can't seem to get started. I'm still on the same goal from last month. I feel like
I'm spinning my wheels and not making any real progress. Maybe I'm overthinking it?"
        """)

    transcript = st.text_area(
        "Enter Transcript",
        height=200,
        placeholder="Paste the mastermind transcript here..."
    )

    if st.button("Detect Stuck Signals", type="primary"):
        if transcript.strip():
            with st.spinner("Analyzing for stuck signals..."):
                try:
                    result = get_stuck_detections(transcript)

                    st.success("Analysis complete")

                    result_dict = result.model_dump(mode='json')

                    # Summary
                    total_detections = len(result_dict.get('detections', []))

                    if total_detections == 0:
                        st.success("No stuck signals detected. All participants seem to be making progress.")
                    else:
                        st.warning(f"{total_detections} stuck signal(s) detected")

                        # Display each detection
                        for idx, detection in enumerate(result_dict.get('detections', []), 1):
                            with st.expander(f"{detection.get('name', 'Unknown')} — {detection.get('classification', 'N/A')}", expanded=True):

                                col1, col2 = st.columns([2, 1])

                                with col1:
                                    st.markdown(f"**Classification:** `{detection.get('classification', 'N/A')}`")
                                    st.markdown("**Stuck Summary:**")
                                    st.warning(detection.get('stuck_summary', 'N/A'))

                                    st.markdown("**Exact Quotes:**")
                                    for quote in detection.get('exact_quotes', []):
                                        st.info(f"\"{quote}\"")

                                with col2:
                                    st.markdown("**Suggested Next Step:**")
                                    st.success(detection.get('potential_next_step', 'N/A'))

                                st.markdown("---")

                    # Show raw JSON
                    with st.expander("View Raw JSON Output"):
                        display_json(result_dict)

                except ValidationError as e:
                    st.error("Validation Error")
                    st.json(e.errors())
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a transcript to analyze.")

# WEEKLY GOALS PAGE
elif page == "Weekly Goals":
    st.title("Weekly Goals Extraction")
    st.markdown("Extract and analyze weekly goals set by participants.")

    st.markdown("---")

    with st.expander("View Sample Transcript"):
        st.text("""
Sample: "This week my goal is to send out 20 LinkedIn connection requests and follow
up with 5 warm leads. I also want to finish the proposal for that enterprise client
by Wednesday."
        """)

    transcript = st.text_area(
        "Enter Transcript",
        height=200,
        placeholder="Paste the mastermind transcript here..."
    )

    if st.button("Extract Goals", type="primary"):
        if transcript.strip():
            with st.spinner("Extracting goals..."):
                try:
                    result = get_goals(transcript)

                    st.success("Analysis complete")

                    result_dict = result.model_dump(mode='json')

                    # Summary
                    total_goals = len(result_dict.get('goals', []))
                    vague_goals = sum(1 for g in result_dict.get('goals', []) if g.get('is_vague', False))

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Goals", total_goals)
                    with col2:
                        st.metric("Vague Goals", vague_goals)

                    # Display goals
                    st.markdown("### Goals by Participant")

                    for idx, goal in enumerate(result_dict.get('goals', []), 1):
                        name = goal.get('name', 'Unknown')
                        goal_text = goal.get('quantifiable_goal', 'N/A')
                        is_vague = goal.get('is_vague', False)

                        with st.expander(f"{name}", expanded=True):
                            if is_vague:
                                st.warning(f"**Goal:** {goal_text}")
                                st.caption("This goal is vague and may need clarification")
                            else:
                                st.success(f"**Goal:** {goal_text}")
                                st.caption("This goal is specific and actionable")

                    # Display summary message
                    summary_message = result_dict.get('summary_message')
                    if summary_message:
                        st.markdown("---")
                        st.markdown("### Summary Message for Slack")
                        st.text_area(
                            "Copy this message to post in your Slack group:",
                            value=summary_message,
                            height=150,
                            key="summary_message_box"
                        )

                    # Show raw JSON
                    with st.expander("View Raw JSON Output"):
                        display_json(result_dict)

                except ValidationError as e:
                    st.error("Validation Error")
                    st.json(e.errors())
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a transcript to analyze.")

# ATTENDANCE PAGE
elif page == "Attendance":
    st.title("Attendance Tracking")
    st.markdown("Track and analyze participant attendance and engagement.")

    st.markdown("---")

    with st.expander("View Sample Inputs"):
        st.text("""
Attendance Record Example:
"John Smith, Jane Doe, Mike Johnson"

Transcript Example:
"Hi everyone! John here. Jane, I see you're joining from the airport - safe travels!
I don't see Mike on the call today."
        """)

    col1, col2 = st.columns(2)

    with col1:
        attendance = st.text_area(
            "Attendance Record",
            height=100,
            placeholder="Enter expected attendees (comma-separated names)..."
        )

    with col2:
        transcript = st.text_area(
            "Transcript",
            height=100,
            placeholder="Paste the transcript here..."
        )

    if st.button("Analyze Attendance", type="primary"):
        if attendance.strip() and transcript.strip():
            with st.spinner("Analyzing attendance..."):
                try:
                    result = get_attendance(attendance, transcript)

                    st.success("Analysis complete")

                    result_dict = result.model_dump(mode='json')

                    # Summary metrics
                    attendees = result_dict.get('attendance', [])
                    present = sum(1 for a in attendees if a.get('status') == 'present')
                    absent = len(attendees) - present

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Participants", len(attendees))
                    with col2:
                        st.metric("Present", present, delta=f"{(present/len(attendees)*100):.0f}%")
                    with col3:
                        st.metric("Absent", absent)

                    st.markdown("---")

                    # Display attendance details
                    st.markdown("### Detailed Attendance")

                    for attendee in attendees:
                        name = attendee.get('name', 'Unknown')
                        status = attendee.get('status', 'unknown')
                        notes = attendee.get('notes', '')

                        col1, col2 = st.columns([1, 3])

                        with col1:
                            if status == 'present':
                                st.success(f"{name}")
                            elif status == 'travelling':
                                st.info(f"{name} (Travelling)")
                            elif status == 'family time':
                                st.info(f"{name} (Family Time)")
                            elif status == 'work/business':
                                st.warning(f"{name} (Work/Business)")
                            elif status == 'wellness':
                                st.info(f"{name} (Wellness)")
                            else:
                                st.error(f"{name} (Absent)")

                        with col2:
                            st.markdown(f"**Status:** {status}")
                            if notes:
                                st.caption(f"Notes: {notes}")

                        st.markdown("---")

                    # Show raw JSON
                    with st.expander("View Raw JSON Output"):
                        display_json(result_dict)

                except ValidationError as e:
                    st.error("Validation Error")
                    st.json(e.errors())
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter both attendance record and transcript.")

# CALL SENTIMENT PAGE
elif page == "Call Sentiment":
    st.title("Call Sentiment Analysis")
    st.markdown("Analyze the emotional tone of weekly group conversations to detect morale shifts and group health.")

    st.markdown("---")

    with st.expander("View Sample Transcript"):
        st.text("""
Sample: "I'm pumped about this week! Just closed a huge client and feeling really good
about the direction things are going. Mark said something earlier that really resonated
with me about staying focused. On the flip side, I've been feeling a bit overwhelmed
with all the new projects coming in, but I know it's a good problem to have."
        """)

    transcript = st.text_area(
        "Enter Transcript",
        height=200,
        placeholder="Paste the mastermind transcript here..."
    )

    if st.button("Analyze Sentiment", type="primary"):
        if transcript.strip():
            with st.spinner("Analyzing sentiment..."):
                try:
                    result = get_call_sentiment(transcript)

                    st.success("Analysis complete")

                    result_dict = result.model_dump(mode='json')

                    # Display sentiment score with visual indicator
                    st.markdown("### Overall Sentiment")

                    sentiment_score = result_dict.get('sentiment_score', 3)
                    confidence_score = result_dict.get('confidence_score', 0)

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Color code based on sentiment
                        if sentiment_score >= 4:
                            st.metric("Sentiment Score", f"{sentiment_score}/5", delta="Positive")
                        elif sentiment_score >= 3:
                            st.metric("Sentiment Score", f"{sentiment_score}/5", delta="Neutral")
                        else:
                            st.metric("Sentiment Score", f"{sentiment_score}/5", delta="Negative")

                    with col2:
                        st.metric("Confidence", f"{confidence_score:.0%}")

                    with col3:
                        dominant_emotion = result_dict.get('dominant_emotion', 'N/A')
                        st.markdown(f"**Dominant Emotion**")
                        st.markdown(f'<span class="tag tag-blue">{dominant_emotion}</span>', unsafe_allow_html=True)

                    st.markdown("---")

                    # Rationale
                    st.markdown("### Analysis Rationale")
                    st.info(result_dict.get('rationale', 'N/A'))

                    # Representative quotes
                    st.markdown("### Participant Emotions & Quotes")
                    quotes = result_dict.get('representative_quotes', [])

                    if quotes:
                        for quote_obj in quotes:
                            name = quote_obj.get('name', 'Unknown')
                            emotions = quote_obj.get('emotion', [])
                            exact_quotes = quote_obj.get('exact_quotes', [])
                            is_negative = quote_obj.get('is_negative', False)

                            with st.container():
                                col_a, col_b = st.columns([3, 1])

                                with col_a:
                                    st.markdown(f"**{name}**")

                                with col_b:
                                    if is_negative:
                                        st.markdown('<span class="tag tag-orange">Negative</span>', unsafe_allow_html=True)
                                    else:
                                        st.markdown('<span class="tag tag-green">Positive</span>', unsafe_allow_html=True)

                                # Display emotions as tags
                                if emotions:
                                    emotion_html = " ".join([f'<span class="tag tag-gray">{emotion}</span>' for emotion in emotions])
                                    st.markdown(f"**Emotions:** {emotion_html}", unsafe_allow_html=True)

                                # Display quotes
                                if exact_quotes:
                                    st.markdown("**Quotes:**")
                                    for quote in exact_quotes:
                                        st.markdown(f'> "{quote}"')

                                st.markdown("---")
                    else:
                        st.warning("No representative quotes found")

                    # Show raw JSON
                    with st.expander("View Raw JSON Output"):
                        display_json(result_dict)

                except ValidationError as e:
                    st.error("Validation Error")
                    st.json(e.errors())
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a transcript to analyze.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #787774; font-size: 0.875rem; padding: 2rem 0;'>"
    "OwnersUp AI Analytics · Powered by Gemini 2.5 Flash"
    "</div>",
    unsafe_allow_html=True
)
