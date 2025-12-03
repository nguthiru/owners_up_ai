from pydantic import BaseModel, Field
from typing import List,Any,Callable,Literal,Optional
from langchain_core.output_parsers import PydanticOutputParser
from typing_extensions import Annotated
from pydantic import SkipValidation,WrapValidator,ValidationError
from enum import Enum
def create_parser(model: BaseModel) -> PydanticOutputParser:
    parser = PydanticOutputParser(pydantic_object=model)
    return parser

def invalid_to_none(v: Any, handler: Callable[[Any], Any]) -> Any:
    try:
        return handler(v)
    except ValidationError:
        return None
class CustomModel(BaseModel):
    model_config = {"use_enum_values": True}

    @classmethod
    @property
    def parser(cls) -> PydanticOutputParser:
        return create_parser(cls)

class MarketingActivityStage(Enum):
        closed = "closed"
        proposal = "proposals"
        meetings = "meetings"


class MarketingActivityType(Enum):
    network_activation = "Network Activation"
    linkedin = "linkedin"
    cold_outreach = "cold_outreach"
    none = "none_mentioned"

class MarketingActivityContractType(Enum):
    monthly = "monthly"
    one_time = "one_time"
    hybrid = "hybrid"


class MarketingOutcome(CustomModel):
    no_of_meetings : int = Field(description="No of meetings, 0 if not mentioned or not positive e.g if its lost have -values")
    no_of_proposals : int = Field(description="No of proposals, 0 if not mentioned, or not positive. e.g if its lost have -values")
    no_of_clients : int = Field(description="No of clients. 0 if not mentioned, or not positive. e.g if its lost have -values")
    notes : str = Field(description="Brief notes of what they say")

class MarketingActivity(CustomModel):
    stage : MarketingActivityStage = Field(description="Stage their are in given the transcript")
    activity : MarketingActivityType = Field(description="Type of marketing activity they conducted")
    quanitity: int = Field(description="Quantifiable outcome, if none put 0, if lost you can have it as -ve")
    outcome : MarketingOutcome = Field(description="outcome of the marketing activity")
    is_win : bool = Field(description="Whether the outcome is a win ")
    contract_type : Optional[MarketingActivityContractType] = Field(description="If a contract is awarded the type")
    revenue : Optional[float] = Field(description="Revenue from the specified activity if available")
    client_involved :bool = Field(description="Whether a client has been involved or mentioned")


class IndividualMarketingActivities(CustomModel):
    activities : List[MarketingActivity] = Field(description="List of marketing activities for each participant")
    name: Optional[str] = Field(description="Name of CTO, if you cannot determine it just have it as null, do not hallucinate")

class MarketingActivities(CustomModel):
    activities : List[IndividualMarketingActivities] = Field(description="List of activities by every participant")

class WeeklyGoalStatus(Enum):
    yes = "yes"
    no = "no"
    partial = "partial"


class WeeklyGoal(CustomModel):
    name : Optional[str] = Field(description="Name of CTO, if you cannot determine it just have it as null, do not hallucinate")
    quantifiable_goal :Optional[str] = Field(description="Quantifiable goal from the meeting in about 10-ish words ")
    is_vague :bool = Field(description="Whether goal is vague or not")
    # goal_status  :Optional[WeeklyGoalStatus] = Field(description="Whether the goal is achieved from the weekly meeting. If ambigous leave as null, if in progress partial")


class WeeklyGoals(CustomModel):
    goals : List[WeeklyGoal] = Field(description="Weekly goals of members")


class WeeklyAttendanceStatus(Enum):
    absent_without_update = "Absent without updates"
    travelling = "travelling"
    family_time = "family time"
    present = "present"
    work_business = "work/business"
    wellness = "wellness"

class WeeklyIndividualAttendance(CustomModel):
    name : str = Field(description="Name of the CTO")
    status : WeeklyAttendanceStatus = Field(description="Whether the person is present and status.")
    notes : Optional[str] = Field(description="Reason or what they said if available")

class WeeklyAttendance(CustomModel):
    attendance :List[WeeklyIndividualAttendance] = Field("whole attendance of the team")
    date : Optional[str] = Field("date of the meeting in YYYY-MM-dd")

# CHALLENGE EXTRACTION
class ChallengeStrategyTag(Enum):
    mindset_reframe = "Mindset Reframe"
    tactical_process = "A step by step action or method"
    resource_suggestion = "Resource or tool Suggestion"
    connection = "Connection/referral"
    framework = "A structure, model, or named methodology"

class ChallengeStrategy(CustomModel):
    name :Optional[str] = Field(description="Who suggestied it")
    summary :str = Field(description="Short actionable summary")
    tag :ChallengeStrategyTag = Field(description="Tag of the strategy")

class Challenge(CustomModel):
    challenge : str = Field(description="Summarize their core challenge in 1–2 sentences. If they didn’t explicitly say it but implied it, infer it clearly.")
    category :str = Field(description="Pick a category from the provided list or propose a new category if none fit")
    strategies :List[ChallengeStrategy] = Field(description="Strategies suggested in regards to the challenge")


class IndividualChallenges(CustomModel):
    name :str = Field(description="Name of the CTO")
    challenges :List[Challenge] = Field(description="Challenges faced during the discussion")

class Challenges(CustomModel):
    challenges : List[IndividualChallenges] = Field(description="Challenges got from the transcript")



class StuckDetection(CustomModel):
    name :str = Field(description="Name of the participant")
    classification: str = Field(description="Classification of the emotion they are feeling")
    stuck_summary :str = Field(description="Briefly explain what kind of stuckness they’re experiencing and why — e.g., motivation lapse, repeating old goals, feeling overwhelmed, unclear next steps, emotional stuckness.")
    exact_quotes : List[str] = Field(description="List 1–3 of the most revealing quotes verbatim")
    potential_next_step :str = Field(description="Suggest 1 light-touch nudge, e.g., “Book a quick momentum-reset session,” “Break down into micro-goals,” “Pair up for co-working,” “Identify root cause in next call.”")


class StuckDetections(CustomModel):
    detections : List[StuckDetection] = Field(description="Problems identified")


class RiskRating(Enum):
    high_risk="high_risk"
    medium_risk="medium_risk"
    on_track="on_track"
    intervention="intervention"
    crushing_it="crushing_it"

# RISK RATING
class IndividualRiskRating(CustomModel):
    rating :RiskRating = Field(description="Risk rating of the participant")
    signal :str = Field(description="Reason to justify the rating")
    name :str = Field(description="Name of the participant")

class RiskRatings(CustomModel):
    ratings : List[IndividualRiskRating] = Field(description="Risk ratings")
 