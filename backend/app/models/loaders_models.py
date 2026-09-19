from typing import Optional, List, TypedDict, Literal
from pydantic import BaseModel, Field

class Question(BaseModel):
    number: str
    section: Optional[str] =None
    text: str 
    marks: Optional[int]=None
    type: Literal['numerical', 'mcq', 'short', 'long'] = 'short'
    options: Optional[list[str]] = None
    has_figure: bool = False
    page: Optional[int]= None
    choice_group: Optional[str] = None
    
class Paper(BaseModel):
    paper_id: str
    fingerprint: str
    status: Literal['parsing', 'solving', 'ready', 'failed']
    questions: List[Question] = Field(default_factory=list)
    total_questions: Optional[int]= None
    total_marks: Optional[int]=None
    sections: List[str] = Field(default_factory=list)