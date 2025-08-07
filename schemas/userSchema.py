from pydantic import BaseModel, EmailStr
import datetime

class UserResponse(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime.datetime
    updated_at : datetime.datetime
    is_active: bool
    
    class Config:
        from_attributes = True
