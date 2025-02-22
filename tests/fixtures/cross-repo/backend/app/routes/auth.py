from fastapi import APIRouter                                                                                                               
                                                                                                                                             
router = APIRouter()                                                                                                                        
                                                                                                                                             
@router.post("/login")  # Should match frontend call                                                                                        
async def login(username: str, password: str):                                                                                              
    return {"status": "authenticated"} 