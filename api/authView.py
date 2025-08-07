from fastapi import APIRouter, HTTPException, Depends, status
from services.authService import create_access_token, create_reset_token
from fastapi.responses import JSONResponse
from schemas.authSchema import LoginRequest,  SignUpRequest, ChangePasswordRequest, VerifyLoginOtpRequest, VerifySignupOtpRequest, ForgotPasswordRequest, VerifyForgotPasswordRequest
from services import userService, emailService, otpService, authService
from schemas import userSchema
from database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
import random
import settings

auth_router = APIRouter()

@auth_router.post("/auth/login")
async def login(data: LoginRequest, session = Depends(get_async_session)):
    otp = str(random.randint(100000, 999999))
    user = await userService.get_user_by_email(session= session, email= data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not await userService.check_password(user, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    
    token = create_access_token({"sub": str(user.id)})
    return {
        "status": True,
        "message": "OTP verified successfully",
        "access_token": token,
        "token_type": "bearer",
        "data": userSchema.UserResponse.model_validate(user)

    }

@auth_router.post("/auth/signup")
async def signup(data: LoginRequest, session = Depends(get_async_session)):
    otp = str(random.randint(100000, 999999))

    if await userService.get_user_by_email(session= session, email= data.email):
        raise HTTPException(status_code= 400, detail= "User already exists")
        
    try:
        await otpService.store_otp(email= data.email, otp=otp)
        await emailService.send_otp_email(email= data.email, otp = otp)

    except Exception as e:
        return JSONResponse(content={"status": False, "message": f"Error occurred while sending otp: {e}"}, status_code= 400)
    
    return {"status": True, "message": "Otp sent succesfully"}

    

@auth_router.post("/auth/signup/verify-otp")
async def signup_otp(data: VerifySignupOtpRequest, session: AsyncSession = Depends(get_async_session)):

    # User should NOT exist yet
    if await userService.get_user_by_email(session=session, email=data.email):
        raise HTTPException(status_code=400, detail="User already exists")

    stored_otp = await otpService.get_otp(email=data.email)

    if not stored_otp or data.otp != stored_otp:
        raise HTTPException(status_code=401, detail="OTP verification failed")

    try:
        await otpService.delete_otp(email=data.email)
    except Exception as e:
        return JSONResponse(
            content={"status": False, "message": f"Error deleting OTP: {e}"},
            status_code=400
        )

    user = await userService.create_user(
        session=session,
        email=data.email,
        raw_password=data.password
    )

    token = create_access_token({"sub": user.id})
    return {
        "status": True,
        "message": "OTP verified successfully",
        "access_token": token,
        "token_type": "bearer",
        "data": userSchema.UserResponse.model_validate(user)

    }

@auth_router.post("/auth/change-password")
async def change_password(
    data: ChangePasswordRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(userService.get_current_user)
):
    if not await userService.check_password(current_user, data.current_password):
        raise HTTPException(status_code=400, detail="Password is incorrect")
    
    await userService.update_password(session=session, user=current_user, raw_password=data.new_password)
    return {"status": True, "message": "Password updated successfully"}

@auth_router.post("/auth/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    session: AsyncSession= Depends(get_async_session)
):
    user = await userService.get_user_by_email(session= session, email= data.email)
    

    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "User does not exist")
    reset_token = create_reset_token(email= data.email)
    url = f"{settings.DOMAIN_URL}/reset-password?email={data.email}&code={reset_token}"
        # https://merchant.korapay.com/auth/reset-password?email=chowdome.cu@gmail.com&code=5iiTenNRpMs919svQGs2tZZV6gFKFzabBZtc8VmL9MoT5atP1T&action=password_reset
    try:
        await emailService.set_reset_url(email= data.email, url= url)
    except Exception as e:
        return JSONResponse(content={"status": False, "message": f"Error occurred while sending otp: {e}"}, status_code= 400)
    return {"status": True, "message": "Password reset email sent succesfully"}

@auth_router.post("/auth/forgot-password/verify-reset")
async def forgot_password(
    data: VerifyForgotPasswordRequest,
    session: AsyncSession= Depends(get_async_session)
):
    user = await userService.get_user_by_email(session= session, email= data.email)
    email = authService.decode_reset_token(token= data.token)

    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "User does not exist")
    
    if user.email != email or email is None:
        raise HTTPException(status_code=400, detail="Token verification failed")
    
    user = await userService.update_password(session= session, user= user, raw_password= data.new_password)
    token = create_access_token({"sub": user.id})

    return {
        "status": True,
        "message": "Password updated successfully",
        "access_token": token,
        "token_type": "bearer"
    }