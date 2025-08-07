from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
 
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
   
class VerifyLoginOtpRequest(LoginRequest):
    otp: str

class VerifySignupOtpRequest(SignUpRequest):
    otp: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyForgotPasswordRequest(ForgotPasswordRequest):
    new_password: str
    token: str