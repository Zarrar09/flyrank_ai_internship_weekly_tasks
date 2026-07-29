from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Header
from supabase_client import supabase
from pydantic import BaseModel 


app = FastAPI()

class SignUpRequest(BaseModel):
    email: str
    password: str
    
class LoginRequest(BaseModel):
    email: str
    password: str

@app.on_event("startup")
async def startup():
    print("Server is running and connected to supabase")
    
@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/public/info")
async def message():
    return JSONResponse(status_code=200, content={"message": "Welcome Stranger! This information is public."})

@app.get("/protected/profile")
async def accessProfile(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Access token required"})

@app.post("/auth/signup")
async def signup(signup: SignUpRequest):
    email = signup.email
    password = signup.password
    
    if not email or not password:
        return JSONResponse(status_code=400, content={"error" : "Missing email or password"})
    
    
    credentials = {
        "email" : email,
        "password" : password
    }
    
    try:
        response = supabase.auth.sign_up(credentials)
        return JSONResponse(status_code=201, content={"user": response.user.model_dump(mode="json")})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    
    
@app.post("/auth/login")
async def login(loginDetails : LoginRequest):
    email = loginDetails.email
    password = loginDetails.password
    
    if not password:
        return JSONResponse(status_code=400, content={"error": "Missing Password"})
    
    credentials = {
        "email": email,
        "password" : password
    }
    
    try:
        response = supabase.auth.sign_in_with_password(credentials)
        return JSONResponse(
            status_code=200, 
            content={
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
            }
        )
    except:
        return JSONResponse(status_code=401, content={"error": "Invalid Credentials"})