# Aider — AI-Powered Cross-Repository Coding Assistant                                                                                                                                                                                         
 **Aider** turns any Git repository into an ongoing conversation with a Large-Language Model.                                        
 Request refactors, bug-fixes or explanations; Aider stages, commits and streams diffs back to you                                   
 while preserving a clean history.                                                                                                   
                                                                                                                                     
 ## Key Features                                                                                                                     
 • LLM-driven editing (whole-file, edit-block, udiff, etc.)                                                                          
 • Git automation: auto-stage, commit, undo/redo, branch safety checks                                                               
 • CLI, Streamlit GUI and optional voice input                                                                                       
 • Cross-repository reasoning via `aider/cross_repo_graph.py`                                                                        
 • 15-plus language support through tree-sitter  tags cache                                                                         
 • Live file watcher surfacing AI TODO comments                                                                                      
 • Analytics & benchmarking harness (SWE-Bench, custom grids)                                                                        
                                                                                                                                     
 ## Quick Start                                                                                                                      
 ```bash                                                                                                                             
 pip install aider                                                                                                                   
 # run inside any git repo                                                                                                           
 aider                                                                                                                               
 ```                                                                                                                                 
                                                                                                                                     
 ## Example Session                                                                                                                  
 ```text                                                                                                                             
 > aider                                                                                                                             
 Aider: Which files would you like to add?                                                                                           
 You: src/sample.py                                                                                                                  
 You: "Rename function `greet` to `say_hello` everywhere."                                                                           
 Aider streams patch …                                                                                                               
 ```                                                                                                                                 
                                                                                                                                     
 ## Architecture (High Level)                                                                                                        
 ```                                                                                                                                 
 ┌─ Input/Output (aider/io.py)                                                                                                       
 │    ├── CLI / GUI / Voice                                                                                                          
 │    └── Linter                                                                                                                     
 ├─ Coders (aider/coders/*)      ← prompt templates & diff builders                                                                  
 ├─ LLM Adapter (aider/llm.py)   ← wraps LiteLLM, cost tracking                                                                      
 ├─ Repo Layer (aider/repo.py)   ← git plumbing, diff/patch, undo                                                                    
 └─ Cross-Repo Graph (aider/cross_repo_graph.py)                                                                                     
 ```                                                                                                                                 
                                                                                                                                     
 ## Contributing                                                                                                                     
 PRs are welcome! Run `pytest` and `ruff` before submitting.                                                                         
 See `CONVENTIONS.md` for the project’s coding protocol.                                                                             
                                                                                                                                     
 ## License                                                                                                                          
 MIT © 2024 Aider Contributors  
