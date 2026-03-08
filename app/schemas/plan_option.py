from pydantic import BaseModel


class ConfirmPlanRequest(BaseModel):
    option_id: str
