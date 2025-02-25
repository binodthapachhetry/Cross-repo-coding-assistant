from fastapi import APIRouter, HTTPException                                                                                                
from pydantic import BaseModel                                                                                                              
                                                                                                                                            
router = APIRouter()                                                                                                                        
                                                                                                                                            
class LoginRequest(BaseModel):                                                                                                              
    username: str                                                                                                                           
    password: str                                                                                                                           
                                                                                                                                            
@router.post("/auth/login")                                                                                                                      
async def login(request: LoginRequest):                                                                                                     
    if request.username == "test" and request.password == "test":                                                                           
        return {"status": "success"}                                                                                
    raise HTTPException(status_code=401, message="Invalid credentials")  