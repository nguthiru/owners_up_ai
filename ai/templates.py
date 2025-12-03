from langchain_core.prompts import PromptTemplate

from .models import Challenges, MarketingActivities, Challenge, RiskRatings, StuckDetections, WeeklyAttendance, WeeklyGoals


GET_MARKETING_ACTIVITY_OUTCOME_PROMPT = PromptTemplate(
    input_variables= ["transcript"],
    template = """
    You are an expert transcript analyst for entrepreneur peer groups.
    Your task is to extract all marketing activities mentioned by each participant, and classify them according to Peer Progress categories.
    For outcomes, here is your guide:
    Meetings booked / held (discovery calls, networking, etc.)
    Proposals sent / planned
    Clients closed / signed.

    Here is the transcript: {transcript}.

    Format Instructions: {format_instructions}
    """,

    partial_variables= {"format_instructions": MarketingActivities.parser.get_format_instructions()}
)

GET_CHALLENGES_PROMPT = PromptTemplate(
    input_variables=["transcript"],
    template="""
    You are an expert analyst for mastermind group transcripts.
    Your job is to extract participants’ challenges and the strategies or tips shared during the call, and tag each challenge with the most relevant category.
    Common Challenge Categories: 
    1. Clarity: Unclear goals, positioning, or priorities (e.g., “I’m not sure what offer to focus on.”
    2. Lead Generation: Not enough qualified leads, inconsistent pipeline
    3. Sales & Conversion: Trouble converting leads, pricing issues, follow-up gaps
    4. Systems & Operations: Lacking processes, delegation gaps, tool confusion
    5. Time & Focus: Overwhelm, poor prioritization, no protected strategy time
    6. Team & Delegation: Hiring, training, or management issues
    7. Mindset / Emotional: Fear, perfectionism, overthinking, burnout
    8. Scaling & Offers: Bottlenecks moving from solo to leveraged model, unclear scalable offer
    9. Other: Use when it doesn’t fit anywhere else (you can later create a new category if you see repeats
    If the challenge doesn’t fit any of the above, propose a new one in brackets like:
    [NEW CATEGORY: Partnerships]


    RULES
    A “challenge” can be explicit (“I’m stuck on lead generation”) or implicit (e.g., they talk about chaos without labeling it). If implicit, summarize the real issue.
    “Strategies/Tips” can come from anyone (facilitator, peers, or themselves). Include tips even if they’re broadly useful, not just addressed to the speaker.
    Ignore casual chatter, vague venting, or repeated filler.
    Be concise and actionable — this should be reviewable at a glance.

    . Here is the transcript: {transcript}. {format_instructions}
    """,
    partial_variables= {"format_instructions": Challenges.parser.get_format_instructions()}

)


GET_STUCK_DETECTIONS = PromptTemplate(
    input_variables=["transcript"],
    template="""
    You are an expert mastermind transcript analyst. Your job is to identify when a participant expresses being stuck, stalled, or not making progress during a mastermind call.
    This includes signs of low momentum, overwhelm, confusion, procrastination, emotional blockers, or repeating the same goals without progress.
     Critical Instructions
        Look for self-reported stuckness — explicit statements like “I’m stuck,” “I haven’t done anything,” “I don’t know why,” “I can’t seem to move forward.”
        Also catch implied stuckness — repeating the same goal for multiple weeks, talking about “spinning wheels,” “lapses,” or “feeling off.”
        Capture exact quotes that show this clearly.
        Summarize why they’re stuck (if they give context).
        Classify the stuck type to make follow-up easier.
        Include timestamps.
        Process the entire transcript systematically.
    Classification Definitions
    Momentum Drop: They've lost rhythm or progress temporarily (“I haven’t done anything for two weeks”).
    Emotional Block: Frustration, shame, fear, perfectionism loops (“I don’t know why, I just can’t get started”).
    Overwhelm: Too many things, unclear priorities, capacity issues.
    Decision Paralysis: Stuck because they’re unsure which path to take.
    Repeating Goal: They’re still on the same goal after multiple weeks without movement.
    Other: If none of the above fits.

    Here is the transcript: {transcript}. {format_instructions}
    """,
    partial_variables= {"format_instructions": StuckDetections.parser.get_format_instructions()}

)


GET_ATTENDANCE = PromptTemplate(
    input_variables=["attendance", "transcript"],
    template="""
    From the attendance record and transcript, verify and show if a member is on the call.

    Please be careful, ensure all speakers are catered for

    Here is the attendance {attendance}.

    Here is the transcript {transcript}
    
    {format_instructions}
    """,

    partial_variables= {"format_instructions": WeeklyAttendance.parser.get_format_instructions()}

)

GET_GOALS = PromptTemplate(

    input_variables=["transcript"],
    template="""
    
    You are an expert transcript analyst, from this transcript, I want you to extract the goals of each participant in the provided format.

    Here is the transcript: {transcript}.

    {format_instructions}
    """,
    partial_variables= {"format_instructions": WeeklyGoals.parser.get_format_instructions()}


)

GET_RISK_RATING = PromptTemplate(

    input_variables=["attendance", "goals","marketing_activity"],
    template="""
    You are an expert transcript analyst. You are required to detect which members are doing well given their attendance and goals set. Use the marketing activity to be able to tell whether they are crushing or not.
    Here are the signals to guide your output:
    Output: 
        1. High-Risk
        Definition: Member is disengaged and unresponsive.
        Triggers (any of these = High-Risk):
        Missed 2 consecutive calls within a 2-week span AND did not communicate why.
        Did not update goals for 2 weeks in a row.
        No communication on attendance or participation for 2+ weeks.

        2. Medium-Risk
        Definition: Member shows inconsistent engagement or missing goals.
        Triggers (any of these = Medium-Risk):
        Missed 1 call without communicating.
        Did not set goals for 1 week.
        Did not complete their goal for 1 week.
        No meetings scheduled in the week.

        3. On-Track
        Definition: Member is engaged and participating as expected.
        Signals:
        Goals are set and updated weekly.
        Meetings are scheduled.
        Accountability updates are consistent.

        ⚠ Special Notification Rule:
        If a member has 4+ meetings scheduled but 0 proposals, flag for intervention (they may need coaching to convert meetings → proposals).
        4. Crushing It
        Definition: Member is excelling and driving outcomes.
        Signals:
        Has proposals out.
        Has clients closed (wins).
    Here is everything you might need: {attendance}. {goals}. {marketing_activity}.

    Format instructions. {format_instructions}
    """,

    partial_variables= {"format_instructions": RiskRatings.parser.get_format_instructions()}
    
)