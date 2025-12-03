from .models import Challenges, MarketingActivities, StuckDetections, WeeklyAttendance, WeeklyGoals
from .templates import GET_ATTENDANCE, GET_GOALS, GET_MARKETING_ACTIVITY_OUTCOME_PROMPT,GET_CHALLENGES_PROMPT, GET_RISK_RATING, GET_STUCK_DETECTIONS
from langchain_google_genai import ChatGoogleGenerativeAI



llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    json_mode=True
)


def get_marketing_activities(transcript) -> MarketingActivities :

    """
    Get the marketing activities each client posted out
    """

    chain = GET_MARKETING_ACTIVITY_OUTCOME_PROMPT | llm 



    res = chain.invoke(transcript)

    res = MarketingActivities.parser.parse(res.content)

    return res

    


def get_challenges(transcript) -> Challenges:
    """

    Get challenges experienced by the CTOs
    """

    chain = GET_CHALLENGES_PROMPT | llm 

    res = chain.invoke(transcript)

    res = Challenges.parser.parse(res.content)

    return res


def get_stuck_detections(transcript) -> StuckDetections:
    """
    Get Stuck detections

    """

    chain = GET_STUCK_DETECTIONS | llm 

    res = chain.invoke(transcript)
    res =  StuckDetections.parser.parse(res.content)

    return res

def get_attendance(attendance, transcript) -> WeeklyAttendance:

    chain = GET_ATTENDANCE | llm 

    res =  chain.invoke(
        {
            "attendance": attendance,
            "transcript": transcript
        }
    )

    res=  WeeklyAttendance.parser.parse(res.content)

    return res

def get_goals(transcript) -> WeeklyGoals:

    chain = GET_GOALS | llm 

    res =  chain.invoke(transcript)

    res = WeeklyGoals.parser.parse(res.content)

    return res


def get_risk_rating(attendance, goals, marketing_activity):

    """
    Gets the risk ratings of the individuals as per the attendance, preferrably should be against a 2 week rolling window.
    """

    chain = GET_RISK_RATING | llm | WeeklyGoals.parser.parse()

    return chain.invoke(
        {
            "attendance": attendance,
            "goals": goals,
            "marketing_activity": marketing_activity
        }
    )

