from pathlib import Path
import pytest                                                                                                                               
from aider.repomap import RepoMap                                                                                                           
from aider.integration_analyzer import IntegrationAnalyzer      
from aider.io import InputOutput                                                                            
                                                                                                                                            
@pytest.fixture                                                                                                                             
def test_repos(): 
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "cross-repo"                                                                 
    io = InputOutput()                                                                                                                                                                                                                                                     
    repos = [                                                                                                                               
        RepoMap(root=str(fixtures_dir / "frontend"), io=io),                                                                                
        RepoMap(root=str(fixtures_dir / "backend"), io=io)                                                                                  
    ]                                                                                                                                       
                                                                                                                                                                                                                                             
    return repos    


                                                                                                                                            
@pytest.mark.slow  # If long-running                                                                                                        
def test_cross_repo_analysis(test_repos):                                                                                                   
    frontend_repo, backend_repo = test_repos  

    # Ensure the repos are loaded correctly 
    print("GGGGGGGGGGGG")
    print(frontend_repo.G)                                                                                        

    analyzer = IntegrationAnalyzer([frontend_repo, backend_repo])                                                                           

    print("Endpoints:", analyzer.endpoints)
    for s in analyzer.endpoints:
        print(s)                                                                         

    # Test endpoint matching                                                                                                                
    matched_pairs = analyzer.match_endpoints()                                                                                              
    assert len(matched_pairs) > 0                                                                                                           
                                                                                                                                            
    # Test specific expected connection                                                                                                     
    frontend_component = "src/components/LoginButton.js:handleAuth"                                                                         
    backend_endpoint = "api/auth.py:login"                                                                                                  
    assert any(                                                                                                                             
        pair == (frontend_component, backend_endpoint)                                                                                      
        for pair in matched_pairs                                                                                                           
    )   