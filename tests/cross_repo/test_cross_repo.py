import pytest                                                                                                                               
from aider.repomap import RepoMap                                                                                                           
from aider.integration_analyzer import IntegrationAnalyzer                                                                                  
                                                                                                                                            
@pytest.fixture                                                                                                                             
def test_repos():                                                                                                                           
    return [                                                                                                                                
        RepoMap("tests/fixtures/cross-repo/frontend"),                                                                                      
        RepoMap("tests/fixtures/cross-repo/backend")                                                                                        
    ]                                                                                                                                       
                                                                                                                                            
@pytest.mark.slow  # If long-running                                                                                                        
def test_cross_repo_analysis(test_repos):                                                                                                   
    frontend_repo, backend_repo = test_repos                                                                                                
    analyzer = IntegrationAnalyzer([frontend_repo, backend_repo])                                                                           
                                                                                                                                            
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