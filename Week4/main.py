from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Header
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase_client import supabase
from pydantic import BaseModel 


app = FastAPI()
security = HTTPBearer()

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

# Dependency Function that we recall again and again to verify if correct token or invalid token
async def get_current_user(obaintedCredentials: HTTPAuthorizationCredentials = Depends(security)):
        # if not authorization or not authorization.startswith("Bearer "):
        #     raise HTTPException(status_code=401, detail="Access token required")
        
        # token = authorization.replace("Bearer ", "")
        # This is automatically done by the HTTPBearer dependency that we called at the start
        
        token = obaintedCredentials.credentials
        
        try: 
            response = supabase.auth.get_user(token)
            return {"user": response.user, "token": token}
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/protected/profile")
async def accessProfile(auth = Depends(get_current_user)):    
    return JSONResponse(
        status_code=200, 
        content={
            "id": auth["user"].id,
            "email": auth["user"].email,
            "created_at": str(auth["user"].created_at)
        }
    )
    
@app.get("/protected/dashboard")
async def dashboard(auth = Depends(get_current_user)):
    return JSONResponse(
        status_code=200,
        content={
            "message" : f"Welcome to your dashboard {auth["user"].email}"
        }
    )
    
    
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
    
@app.post("/auth/logout")
async def logout(auth = Depends(get_current_user)):
    token = auth["token"]
    
    try:
        supabase.auth.sign_out(token)
        return JSONResponse(status_code=204, content=None)
    except Exception as e:
        return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})
    